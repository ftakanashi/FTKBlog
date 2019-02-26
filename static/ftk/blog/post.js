/**
 * Created by weiyz18939 on 2018/10/28.
 */
$(function () {
    $(document).ready(function () {

        $('body').trigger('loadTheme');

        layui.use('element', function () {
            var element = layui.element;
        });

        // 图片alt居中处理, cursor显示，大小缩放处理
        $('.post-body').find('img.post-image').each(function (i, ele) {
            var altText = $(ele).attr('alt');
            $(ele).parent('p').css('text-align', 'center').append('<div class="alt-tag-wrap"><span class="alt-tag">' + altText + '</span></div>');

            //var currWidth = $(ele).width();
            //var windowWidth = $(window).width();
            //console.log(currWidth, windowWidth);
            //if (currWidth / windowWidth >= 0.5) {
            $(ele).on('click', function (event) {
                event.preventDefault();
                var currWidth = $(this).width();
                var windowWidth = $(window).width();
                if (currWidth / windowWidth < 0.5) {
                    $(this).animate({width: '80%'}, 'fast');
                }
                else {
                    $(this).animate({width: '30%'}, 'fast');
                }
            });
        });

        // 代码折叠
        $('pre.prettyprinted').each(function (i, ele) {
            var codeLineNum = $(ele).find('ol li').length;
            if (codeLineNum >= 2) {
                $(ele).wrap('<div class="code-area"></div>').prepend('<button class="btn btn-xs btn-default code-fold-toggle">折叠</button>');
                if (codeLineNum >= 50) {
                    $(ele).find('ol').hide();
                    $(ele).find('button').text('展开');
                }
            }
        });

        // 开关边栏动画
        $('#left-ground-toggle').click(function (event) {
            event.preventDefault();
            var toggle = $(this);
            var leftGround = $('.left-ground');
            var mainGround = $('.main-ground');
            if ($(leftGround).css('display') === 'none') {
                $(toggle).animate({width: '15%'}, 'slow');
                $(leftGround).fadeIn('fast');
                $(mainGround).animate({width: '70%', 'margin-left': '18%'});
            }
            else {
                $(toggle).animate({width: '25px'}, 'slow');
                $(leftGround).fadeOut();
                $(mainGround).animate({width: '90%', 'margin-left': '5%'});
            }
        });

        // 开关灯
        $('#light-toggle').click(function (event) {
            var post = $('.post');
            var currentBg = $(post).css('background-color');
            if (currentBg === 'white' || currentBg === 'rgb(255, 255, 255)' || currentBg === '#ffffff') {
                $(post).css({'background-color': '#cce8cf'});
            }
            else {
                $(post).css({'background-color': 'white'});
            }
        });

        // 生成目录
        $('#make-category').click(function(event){
            event.preventDefault();
            layer.open({
                id: 3521,
                type: 1,
                content: '<div id="toc"></div>',
                title: '文章目录',
                offset: 'rt',
                maxmin: true,
                area: ['20%', '80%'],
                resize: true,
                shade: false
            });
            $('#toc').tocify({
                context: '#postContent',
                selectors: 'h1,h2,h3,h4,h5',
                scrollTo: 95,
                highlightOffset: 0
            });
        });


        // 页面内搜索
        $('#intern-search-input').focus(function (event) {
            layer.tips('输入文本回车可以在页面搜索，多个关键词之间可以用|隔开。', this, {tips: 3, time: 1000});
        }).keyup(function (event) {
            if (event.keyCode != 13) {
                if (event.keyCode == 38) {
                    $('.intern-search-jump-go.prev').trigger('click');
                }
                else if (event.keyCode == 40) {
                    $('.intern-search-jump-go.next').trigger('click');
                }
                return;
            }
            var kw = $(this).val();
            var found = $('#postContent').textSearch(kw, {
                markClass: 'highlight',
                divStr: '|',
                nullReport: false,
                callback: function (foundCount) {
                    if (foundCount > 0) {
                        layer.msg('一共找到了 ' + foundCount + ' 处文字');
                        $('.intern-search-jump').show().find('span').text('1');
                        $('#textsearch_1').addClass('current');
                        $.scrollTo('#textsearch_1');
                    }
                    else {
                        layer.msg('没有找到相关文字');
                        $('.intern-search-jump').hide();
                    }
                }
            });
        });

        $('.intern-search-jump-go').click(function (event) {
            var guideIndex = $(this).parent().find('span');
            var index = parseInt($(guideIndex).text());
            if ($(this).hasClass('prev')) {
                if (index <= 1) {
                    layer.msg('已经到最上面了');
                    return;
                }
                index--;
                $(guideIndex).text(index.toString());
                $.scrollTo('#textsearch_' + index);
                $('.highlight').removeClass('current');
                $('#textsearch_' + index).addClass('current');
            }
            else if ($(this).hasClass('next')) {
                index++;
                if ($('#textsearch_' + index).length === 0) {
                    layer.msg('已经到最下面了');
                    return;
                }
                $(guideIndex).text(index.toString());
                $.scrollTo('#textsearch_' + index);
                $('.highlight').removeClass('current');
                $('#textsearch_' + index).addClass('current');
            }
        });

        // 零碎积累wyz-item的转化
        var s = $('#start-of-wyz-items').parent();
        if (s.length > 0){  // 找到标识DOM
            var title = $(s).next('h5');
            var oldTitle;
            while(title.length > 0){
                var content = $(title).nextUntil('h5');
                var newItem = '<div class="wyz-item">';
                var newTitle = '<h3 class="wyz-item-title">' + $(title).text() + '</h3>';
                var newContent;
                if (content.length <= 1){
                    newContent = '<div class="wyz-item-content">' + $(content).html() + '</div>';
                }
                else{
                    var contentStr = [];
                    var i = 0;
                    while (i < content.length){
                        contentStr.push($(content[i]).html());
                        i++;
                    }
                    newContent = '<div class="wyz-item-content">' + contentStr.join('<br>') + '</div>';
                }
                newItem = newItem + newTitle + newContent + '</div>';
                $(title).before(newItem);
                oldTitle = $(title);
                $(content).remove();
                title = $(oldTitle).next('h5');
                $(oldTitle).remove();
            }
        }

        // 点赞
        $('#great-up').click(function (event) {
            var direct;
            var count = $('#great-count');
            if ($(this).find('i').hasClass('fa-thumbs-o-up')) {
                direct = '+';
                $(this).find('i').removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                $(count).text((parseInt($(count).text()) + 1).toString());
            }
            else {
                direct = '-';
                $(this).find('i').removeClass('fa-thumbs-up').addClass('fa-thumbs-o-up');
                $(count).text((parseInt($(count).text()) - 1).toString());
            }

            $.ajax({
                url: location.pathname,
                type: 'post',
                dataType: 'json',
                data: {
                    act: 'great',
                    direct: direct
                },
                success: function (data) {
                    layer.msg('谢谢点赞！');
                },
                error: function (xml, err, exc) {
                    try {
                        layer.msg(JSON.parse(xml.responseText).msg);
                    }
                    catch (e) {
                        layer.msg('未知错误');
                    }
                }
            });
        });

        // 折叠评论
        $('.collapse-comment').click(function () {
            $('.layui-colla-content').removeClass('layui-show');
        });

        // 删除评论
        $('.delete-comment').click(function (event) {
            var uuid = $(this).attr('name');
            layer.confirm('确定删除此条评论吗？', {icon: 3, title: '提示'}, function (index) {
                var loadLayer = layer.load('1', {shade: 0.5});
                $.ajax({
                    url: location.pathname,
                    type: 'delete',
                    dataType: 'json',
                    data: {
                        target: 'comment',
                        uuid: uuid
                    },
                    complete: function () {
                        layer.close(loadLayer);
                    },
                    success: function (data) {
                        location.reload();
                    },
                    error: function (xml, err, exc) {
                        try {
                            layer.msg(JSON.parse(xml.responseText).msg);
                        }
                        catch (e) {
                            layer.msg('未知错误');
                        }
                    }
                })
            });
        });

        // 跳到相关评论
        $('.jump-to-comment').click(function (event) {
            var tuuid = $(this).attr('name');
            var tdom = $('#comment_' + tuuid);
            if (tdom.length < 1) {
                layer.msg('那条评论已经被删除啦！');
            }
            else {
                $('.layui-colla-item').each(function (i, ele) {
                    $(ele).removeClass('active');
                });
                $(tdom).parents('.layui-colla-item').addClass('active');
                $.scrollTo('#comment_' + tuuid);
            }
        });
    })
        .on('click', '.code-fold-toggle', function (event) {
        // 在进行textSearch之后文档被重新加载，按照一般模式的代码折叠打开绑定操作会失效，所以移到这里
        $(this).next('ol').slideToggle();
        if ($(this).text() == '折叠') {
            $(this).text('展开');
        }
        else {
            $(this).text('折叠');
        }
    })
        .on('click', '#fold-code-all', function (event) {
        var i = $(this).find('i');
        if ($(i).hasClass('fa-level-up')) {
            $('.code-fold-toggle').each(function (i, ele) {
                if ($(ele).text() == '折叠') {
                    $(ele).trigger('click');
                }
            });
            $(i).removeClass('fa-level-up').addClass('fa-level-down');
        }
        else {
            $('.code-fold-toggle').each(function (i, ele) {
                if ($(ele).text() === '展开') {
                    $(ele).trigger('click');
                }
            });
            $(i).removeClass('fa-level-down').addClass('fa-level-up');
        }
    })
        .on('click', '.wyz-item-title', function(event){
            var contentBlock = $(this).next('.wyz-item-content');
            var isDisplayed = $(contentBlock).css('display') != 'none';
            if (isDisplayed){
                $(this).css({background: 'white', 'border-style': 'dashed'}, 'slow');
            }
            else{
                $(this).css({background: '#f4f4f4', 'border-style': 'solid'}, 'slow');
            }
            $(contentBlock).slideToggle();
        });
});
