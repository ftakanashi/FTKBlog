/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
$(document).ready(function(){

    $('body').trigger('loadTheme');

    layui.use('element',function(){
        var element = layui.element;
    });

    // 图片alt居中处理
    $('.post-body').find('img.post-image').each(function(i,ele){
        var size = [$(ele).width(),$(ele).height()];
        var altText = $(ele).attr('alt');
        $(ele).parent('p').css('text-align', 'center').append('<div class="alt-tag-wrap"><span class="alt-tag">' + altText + '</span></div>');
        if (size[0] >= 800){  // 过大的图片的显示优化
            var rate = size[0] / 800.0;
            $(ele).css({width: size[0]*rate + 'px', height: size[1]*rate + 'px'});
        }
        else if (size[1] >= 500){
            var rate = size[1] / 500.0;
            $(ele).css({width: size[0]*rate + 'px', height: size[1]*rate + 'px'});
        }
    });

    // 开关边栏动画
    $('.left-ground-toggle a').click(function(event){
        event.preventDefault();
        var toggle = $(this).parent('.left-ground-toggle');
        var leftGround = $('.left-ground');
        var mainGround = $('.main-ground');
        var internSearch = $('#intern-search-input');
        if ($(leftGround).css('display') === 'none'){
            //$(internSearch).css({width: 'calc(85% - 100px)'});
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
            if (event.keyCode == 38){
                $('.intern-search-jump-go.prev').trigger('click');
            }
            else if (event.keyCode == 40){
                $('.intern-search-jump-go.next').trigger('click');
            }
            return;
        }
        var kw = $(this).val();
        var found = $('#postContent').textSearch(kw,{
            markClass: 'highlight',
            divStr: '|',
            nullReport: false,
            callback: function(foundCount){
                if (foundCount > 0){
                    layer.msg('一共找到了 ' + foundCount + ' 处文字');
                    $('.intern-search-jump').show().find('span').text('1');
                    $('#textsearch_1').addClass('current');
                    $.scrollTo('#textsearch_1');
                }
                else{
                    layer.msg('没有找到相关文字');
                    $('.intern-search-jump').hide();
                }
            }
        });
    });

    $('.intern-search-jump-go').click(function(event){
        var guideIndex = $(this).parent().find('span');
        var index = parseInt($(guideIndex).text());
        if($(this).hasClass('prev')){
            if (index <= 1){
                layer.msg('已经到最上面了');
                return;
            }
            index --;
            $(guideIndex).text(index.toString());
            $.scrollTo('#textsearch_' + index);
            $('.highlight').removeClass('current');
            $('#textsearch_'+index).addClass('current');
        }
        else if($(this).hasClass('next')){
            index ++;
            if ($('#textsearch_' + index).length === 0){
                layer.msg('已经到最下面了');
                return;
            }
            $(guideIndex).text(index.toString());
            $.scrollTo('#textsearch_' + index);
            $('.highlight').removeClass('current');
            $('#textsearch_'+index).addClass('current');
        }
    });

    // 点赞
    $('#great-up').click(function(event){
        var direct;
        var count = $('#great-count');
        if ($(this).find('i').hasClass('fa-thumbs-o-up')){
            direct = '+';
            $(this).find('i').removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
            $(count).text((parseInt($(count).text()) + 1).toString());
        }
        else{
            direct = '-';
            $(this).find('i').removeClass('fa-thumbs-up').addClass('fa-thumbs-o-up');
            $(count).text((parseInt($(count).text()) - 1).toString());
        }

        $.ajax({
            url: location.pathname,
            type: 'post',
            dataType: 'json',
            data: {
                act: 'great',
                direct: direct
            },
            success: function(data){
                layer.msg('谢谢点赞！');
            },
            error: function(xml, err, exc){
                try{
                    layer.msg(JSON.parse(xml.responseText).msg);
                }
                catch(e){
                    layer.msg('未知错误');
                }
            }
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
