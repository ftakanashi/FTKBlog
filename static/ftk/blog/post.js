/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
$(document).ready(function(){

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
});
});
