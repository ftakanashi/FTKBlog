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

function code2num(colorCode){
    if (colorCode[0] == '#'){
        colorCode = colorCode.substr(1);
    }
    var r = parseInt(colorCode.substr(0,2),16);
    var g = parseInt(colorCode.substr(2,2),16);
    var b = parseInt(colorCode.substr(4,2),16);
    return [r,g,b];
}

function darken(color,ext){
    return [color[0] - 10 * ext, color[1] - 10 * ext, color[2] - 10 * ext];
}

function changeTheme(theme){
    var colorSet = theme.colorMap;
    var bg = '/static/image/bg/main/' + theme.bg;
    var main = colorSet[0];
    var oppo = colorSet[1];
    var ass1 = colorSet[2];
    var ass2 = colorSet[3];
    $('div.navbar').css({'background-color': main, 'border-color': main})
        .find('a').css({color: oppo});

    $('.left-ground').css({background: ass1});

    var rgb = code2num(ass2);
    $('.page-footer').css({background: 'rgba('+ rgb.join(',') +',0.9)'});
    $('.footer-copyright').css({background: 'linear-gradient(180deg, rgba('+rgb.join(',')+',0.9) 60%, rgba('+darken(rgb,4).join(',')+',1) 100%)',color: oppo});

    $('body').css({'background-image': 'url('+bg+')'});

    $('.slideunlock-label').css({'background-color': ass1});
    $('.welcome-title').css({background: 'rgba('+code2num(ass1).join(',')+',0.7)'});
    $('.my-carousel').css({'background-image': 'url(' + bg + ')'});
}

$(document).ready(function(event){

    $('body').on('themeChange',function(event){
        var themeSet = [
            {colorMap: ['#323232','#808080','#323232','#323232'], bg: '0.jpg'},
            {colorMap: ['#F0F0D8','#735783','#D9E0CA','#C4B882'], bg: '1.jpg'},
            {colorMap: ['#C0C060','#3E1653','#E0E08C','#C0B060'], bg: '2.jpg'},
            {colorMap: ['#FFF078','#7A5AAE','#F09060','#FFDA78'], bg: '3.jpg'},
            {colorMap: ['#90C078','#F07860','#78A860','#FFF090'], bg: '4.jpg'},
            {colorMap: ['#A89078','#D8D8D8','#D8C0A8','#907878'], bg: '5.jpg'},
            {colorMap: ['#60A8C0','#000000','#60C0F0','#F0D8C0'], bg: '6.jpg'}
        ];
        currentTheme = $.cookie('theme');
        if (!currentTheme){
            theme = themeSet[Math.floor(Math.random() * themeSet.length)];
        }
        else{
            var currIndex = -1;
            currentTheme = JSON.parse(currentTheme);
            for(var i=0;i<themeSet.length;i++){
                if (themeSet[i].bg == currentTheme.bg){
                    currIndex = i;
                    break;
                }
            }
            theme = themeSet[(currIndex >= themeSet.length-1 || currIndex < 0) ? 0 : currIndex + 1];
        }

        changeTheme(theme);
        $.cookie('theme',JSON.stringify(theme),{path: '/'});
    }).on('loadTheme', function(event){
        try{
            var theme = JSON.parse($.cookie('theme'));
        }
        catch(e){
            var defaultTheme = {colorMap: ['#323232','#808080','#323232','#323232'], bg: '0.jpg'};
            theme = defaultTheme;
            $.cookie('theme',JSON.stringify(defaultTheme), {path: '/'});
        }
        changeTheme(theme);
    });


    var navbar = $('div.navbar-inverse');

    //$(navbar).css({top: $(window).scrollTop()});
    //$(window).scroll(function(event){
    //    $(navbar).css({top: $(window).scrollTop()});
    //});
    $('.ground-row').css({'min-height': $(window).height() - $('.footer').height() - $(navbar).height()});
    $('.left-ground').css({top: $(navbar).height() + $('.toolbar').height()});

    // 各个固定按钮功能
    var mailAddr = $('#MailAddr').val();
    $('#goTop').find('a').click(function(event){
        $(window).scrollTop(0);
    });
    $('#sendMail').find('a').click(function(event){
        window.location = 'mailto:'+ mailAddr +'?subject=来自博客的邮件&subject=来自博客的邮件&body=【来源URL：'+ location.href +'】';
    });
    $('#refreshTheme').find('a').click(function(event){
        $('body').trigger('themeChange');
    });

    $.extend({
        'scrollTo': function(tid){
            if (tid.substr(0,1) == '#'){
                selector = tid;
            }
            else{
                selector = '#' + tid;
            }
            $('html,body').animate({scrollTop: $(selector).offset().top - 200 + 'px'},300);
        }
    });
});