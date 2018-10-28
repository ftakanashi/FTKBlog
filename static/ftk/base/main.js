/**
 * Created by weiyz18939 on 2018/10/24.
 */

$(document).ready(function(event){
    $('div.navbar-inverse').css({top: $(window).scrollTop()});
    $(window).scroll(function(event){
        $('div.navbar-inverse').css({top: $(window).scrollTop()});
    });

    // left-ground滚动条
    //$('.left-ground').mCustomScrollbar({
    //    theme: 'dark',
    //    scrollbarPosition: 'outside'
    //});

    // 各个固定按钮功能
    var mailAddr = $('#MailAddr').val();
    $('#goTop').find('a').click(function(event){
        $(window).scrollTop(0);
    });
    $('#sendMail').find('a').click(function(event){
        window.location = 'mailto:'+ mailAddr +'?subject=来自博客的邮件&subject=来自博客的邮件&body=【来源URL：'+ location.href +'】';
    })
});