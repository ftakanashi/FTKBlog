/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
    $(document).ready(function(){
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
    });
});