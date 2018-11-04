/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
$(document).ready(function(){

    layui.use('element',function(){
        var element = layui.element;
    });

    // 开关边栏动画
    $('.left-ground-toggle a').click(function(event){
        event.preventDefault();
        var toggle = $(this).parent('.left-ground-toggle');
        var leftGround = $('.left-ground');
        var mainGround = $('.main-ground');
        var internSearch = $('#intern-search-input');
        if ($(leftGround).css('display') === 'none'){
            $(internSearch).css({width: 'calc(85% - 25px)'});
            $(toggle).animate({width: '15%'},'slow');
            $(leftGround).fadeIn('fast');
            $(mainGround).animate({width: '70%','margin-left': '18%'});
        }
        else{
            $(toggle).animate({width: '25px'},'slow');
            $(leftGround).fadeOut();
            $(mainGround).animate({width: '90%','margin-left': '5%'});
        }
    });


    // 页面内搜索
    $('#intern-search-input').focus(function(event){
        layer.tips('输入文本回车可以在页面搜索，多个关键词之间可以用|隔开。',this,{tips: 3, time: 1000});
    }).keyup(function(event){
        if (event.keyCode != 13){
            return;
        }
        var kw = $(this).val();
        $('#postContent').textSearch(kw,{
            markClass: 'highlight',
            divStr: '|'
        });
    });

    // 折叠评论
    $('.collapse-comment').click(function(){
        $('.layui-colla-content').removeClass('layui-show');
    });

    // 删除评论
    $('.delete-comment').click(function(event){
        var uuid = $(this).attr('name');
        layer.confirm('确定删除此条评论吗？',{icon: 3,title: '提示'},function(index){
            var loadLayer = layer.load('1',{shade: 0.5});
            $.ajax({
                url: location.pathname,
                type: 'delete',
                dataType: 'json',
                data: {
                    target: 'comment',
                    uuid: uuid
                },
                complete: function(){
                    layer.close(loadLayer);
                },
                success: function(data){
                    location.reload();
                },
                error: function(xml, err, exc){
                    try{
                        layer.msg(JSON.parse(xml.responseText).msg);
                    }
                    catch(e){
                        layer.msg('未知错误');
                    }
                }
            })
        });
    });

    // 跳到相关评论
    $('.jump-to-comment').click(function(event){
        var tuuid = $(this).attr('name');
        var tdom = $('#comment_' + tuuid);
        if (tdom.length < 1){
            layer.msg('那条评论已经被删除啦！');
        }
        else{
            $('.layui-colla-item').each(function(i,ele){
                $(ele).removeClass('active');
            });
            $(tdom).parents('.layui-colla-item').addClass('active');
            $.scrollTo('#comment_' + tuuid);
        }
    });
});
});
