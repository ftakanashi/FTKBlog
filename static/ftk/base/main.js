/**
 * Created by weiyz18939 on 2018/10/24.
 */

$(document).ready(function(event){
    $('div.navbar-inverse').css({top: $(window).scrollTop()});
    $(window).scroll(function(event){
        //var navbar = $('div.navbar-inverse');
        //if (parseInt($(navbar).css('top').replace('px','')) < $(window).scrollTop()){
        //    $(navbar).css({top: $(window).scrollTop() - $(navbar).height() + 'px'}).animate({top: $(window).scrollTop() + 'px'},'fast');
        //}
        //else{
        //    $(navbar).css({top: $(window).scrollTop()});
        //}
        $('div.navbar-inverse').css({top: $(window).scrollTop()});
    });

    $('.navbar-brand').click(function(event){
        event.preventDefault();
        var leftG = $('.left-ground');
        var mainG = $('.main-ground');
        if ($(leftG).css('display') === 'none'){
            $(leftG).slideDown('slow');
            $(mainG).animate({'margin-left': '16%'},'slow');
        }
        else{
            $(leftG).slideUp('slow');
            $(mainG).animate({'margin-left':'15%'},'slow');
        }
    });

    $('.left-ground-toggle a').click(function(event){
        event.preventDefault();
        var toggle = $(this).parent('.left-ground-toggle');
        var leftGround = $('.left-ground');
        var mainGround = $('.main-ground');
        if ($(leftGround).css('display') === 'none'){
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

    // 各个固定按钮功能
    var mailAddr = $('#MailAddr').val();
    $('#goTop').find('a').click(function(event){
        $(window).scrollTop(0);
    });
    $('#sendMail').find('a').click(function(event){
        window.location = 'mailto:'+ mailAddr +'?subject=来自博客的邮件&subject=来自博客的邮件&body=【来源URL：'+ location.href +'】';
    })
});