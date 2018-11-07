/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
    $(document).ready(function(){
        var accessed = $.cookie('accessed');
        if (!accessed){
            $('body').fadeIn('slow');
            $('.welcome-title').fadeIn('slow');
            setTimeout('$(\'.my-carousel\').fadeOut(\'slow\');',3000);
            $('.my-carousel').click(function(event){
                $(this).fadeOut('slow');
            });
            $.cookie('accessed',true,{expires: 1});
        }
        else{
            $('.my-carousel').hide();
            $('body').show();
        }


        //layui.use('carousel',function(){
        //    var carousel = layui.carousel;
        //    carousel.render({
        //        elem: '#test1',
        //        width: '100%',
        //        arrow: 'hover',
        //        anim: 'fade'
        //    });
        //});

        //收放左边栏
        $('.navbar-brand').click(function(event){
            event.preventDefault();
            var leftG = $('.left-ground');
            var mainG = $('.main-ground');
            var blurBg = $('div.blur');
            if ($(leftG).css('display') === 'none'){
                $(blurBg).fadeIn();
                $(leftG).slideDown('slow');
                $(mainG).animate({'margin-left': '16%'},'slow');
            }
            else{
                $(leftG).slideUp('slow');
                $(blurBg).fadeOut();
                $(mainG).animate({'margin-left':'15%'},'slow');
            }
        });
    });
});