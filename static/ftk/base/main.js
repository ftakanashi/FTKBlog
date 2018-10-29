/**
 * Created by weiyz18939 on 2018/10/24.
 */

function getParam(key,defaultValue){
    var search = location.search.substr(1);
    var kvs = search.split('&');
    for(var i=0;i<kvs.length;i++){
        var kv = kvs[i];
        var info = kv.split('=');
        var k = info[0];
        var v = info[1];
        if (k == key){
            return v;
        }
    }
    return defaultValue;
}

$(document).ready(function(event){

    $('div.navbar-inverse').css({top: $(window).scrollTop()});
    $(window).scroll(function(event){
        $('div.navbar-inverse').css({top: $(window).scrollTop()});
    });

    // left-ground lazy load
    $('.shake').ready(function(){
        console.log('left done');
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