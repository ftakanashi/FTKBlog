/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
$(document).ready(function(){
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
});
});
