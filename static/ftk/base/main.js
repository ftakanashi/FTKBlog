/**
 * Created by weiyz18939 on 2018/10/24.
 */

$(document).ready(function(event){

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
});