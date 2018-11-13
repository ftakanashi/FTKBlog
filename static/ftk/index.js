/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function(){
    $(document).ready(function(){

        $('body').trigger('loadTheme');

        var slider = new SliderUnlock('.slideunlock-slider', {
            labelTip: '>>>>>推动历史的行程>>>>>',
            successLabelTip: '但是还要考虑历史的…行程'
        }, function(){
            $('.my-carousel').fadeOut(1200);
            $.cookie('accessed', true, {path: '/'});
        },function(){});
        slider.init();

        var accessed = $.cookie('accessed');
        if (!accessed){
            $('body').fadeIn('slow');
            $('.welcome-title').fadeIn('slow');
        }
        else{
            $('.my-carousel').hide();
            $('body').show();
        }


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

        // 打开show-more
        $('.show-more').click(function(event){
            event.preventDefault();
            $(this).fadeOut().parent().find('.category-hidden').fadeIn();
        });

    });
});