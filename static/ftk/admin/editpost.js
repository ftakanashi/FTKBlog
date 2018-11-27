/**
 * Created by weiyz18939 on 2018/10/30.
 */
$(function(){
$(document).ready(function(){

    $('body').trigger('loadTheme');

    // 离开界面提醒
    $(window).bind('beforeunload', function(event) {
        event.preventDefault();
    });

    // 界面初始化工作
    $('.tag-check').click(function(){
        $(this).toggleClass('active');
    });

    $('#categorySelect').select2({
        language: 'zh-CN',
        width: '100%'
    });

    $('#isTopCheck').bootstrapSwitch({
        size: 'small',
        onText: '是',
        offText: '否'
    });

    $('#isReprintCheck').bootstrapSwitch({
        size: 'mini',
        onText: '是',
        offText: '否',
        onSwitchChange: function(e,data){
            $(this).parents('.form-group').next().slideToggle();
        }
    });

    var contentEditor;
    contentEditor = editormd('post-content-editor',{
        width: '100%',
        height: 640,
        path: $('#editor-md-root').val() + '/lib/',
        markdown: $('#post-content').val(),
        codeFold: true,
        saveHtmlToTextarea: true,
        searchPlace: true,
        watch: true,
        htmlDecode: 'script,style,iframe|on*',
        toolbar: true,
        emoji: true,
        taskList: true,
        tocm: true,
        tex: true,
        dialogLockScreen: false,
        dialogShowMask: true,
        dialogMaskBgColor: '#000',
        dialogMaskOpacity: 0.3,
        flowChart: true,
        sequenceDiagram: true,
        imageUpload: true,
        imageFormats: ['jpg','png','gif','jpeg','bmp'],
        imageUploadURL: $('#upload-url').val().trim()
    });

    $.extend({
        loadCache: function(){
            layer.msg('正在寻找自动保存内容...',{offset: 't',icon: 0});
            $.ajax({
                url: location.pathname,
                type: 'put',
                dataType: 'json',
                data: {
                    act: 'load'
                },
                success: function(data){
                    layer.confirm('发现最近('+moment(Date.now() - 1000 * data.time).fromNow()+')自动保存的内容，是否恢复？',{icon:3,title:'提示'},function(index){
                        contentEditor.insertValue(data.content);
                        $('#uuidInput').val(data.post_uuid);
                        layer.msg('恢复成功',{offset: 't',icon: 1});
                    });
                },
                error: function(xml,err,exc){
                    var msg;
                    try{
                        msg = JSON.parse(xml.responseText).msg;
                    }
                    catch(e){
                        msg = '未知错误';
                    }
                    layer.msg(msg,{offset: 't',icon: 0});
                }
            });
        },
        clearCache: function(){
            $.ajax({
                url: location.pathname,
                type: 'put',
                dataType: 'json',
                data: {
                    act: 'clear'
                }
            })
        }
    });
    // 先验自动保存
    //$.loadCache();

    // 点击重置按钮
    $('#reset').click(function(event){
        layer.confirm('重置将会清空所有已经编写的内容',{icon: 3, title: '确定重置吗？'},function(index){
            $('#titleInput,#abstractInput,#post-content-editor-markdown-doc,#post-content-editor-html-code').val('');
            $('.tag-check').removeClass('active');
            $('#categorySelect').val('').trigger('change');
            contentEditor.clear();
            layer.close(index);
        });
    });

    // 点击保存/提交按钮
    $('#save,#submit').click(function(event){
        event.preventDefault();
        var loadLayer = layer.load('1',{shade: 0.7});
        var title = $('#titleInput').val();
        var uuid = $('#uuidInput').val();
        if (!title){
            $.scrollTo('titleInput');
            layer.tips('标题不能为空','#titleInput',{tips: [1,'darkred']});
            layer.close(loadLayer);
            return;
        }
        var content = contentEditor.getMarkdown();
        var category = $('#categorySelect').val();
        if (!category){
            $.scrollTo('categorySelect');
            layer.tips('请选择分类','#categorySelect',{tips: [1,'darkred']});
            layer.close(loadLayer);
            return;
        }
        var isTop = $('#isTopCheck').is(':checked');
        var isReprint = $('#isReprintCheck').is(':checked');
        var reprintSrc = $('#reprintSrcInput').val();
        var tags = [];
        $('.tag-check').each(function(i,ele){
            var regExp = /tag_(\d+)$/;
            if ($(ele).hasClass('active')){
                var rawId = $(ele).attr('id');
                var id = rawId.match(regExp)[1];
                tags.push(id);
            }
        });
        var isPublished = $('#publish').is(':checked');
        if($(this).attr('id') != 'submit'){
            // 点击保存草稿
            isPublished = 'false';
        }

        $.ajax({
            url: location.pathname,
            type: 'post',
            dataType: 'json',
            data: {
                title: title,
                post_uuid: uuid,
                content: content,
                category: category,
                is_top: isTop,
                is_reprint: isReprint,
                reprint_src: reprintSrc,
                tag: JSON.stringify(tags),
                is_publish: isPublished
            },
            success: function(data){
                var next = data.next;
                var msg = data.msg;
                $.clearCache();
                setTimeout('location.href = "' + next + '"', 3000);
                layer.load('1',{shade: 0.5});
                window.clearInterval(autoSaveInterval);
                layer.msg(msg?msg:'' + '  3秒后跳转到新文章界面');
            },
            error: function(xml, err, exc){
                try{
                    layer.open({
                        title: '保存失败',
                        content: JSON.parse(xml.responseText).msg});
                }
                catch(e){
                    layer.open({
                        title: '保存失败',
                        content: '未知错误'
                    });
                }
            },
            complete: function(){layer.close(loadLayer);}
        });

    });

    // 手动恢复缓存内容
    $('#restoreContent').click(function(event){
        $.loadCache();
    });

    function autoSave(){
        var uuid = $('#uuidInput').val();
        var currentContent = contentEditor.getMarkdown();
        var showMsg = $('#showAutosaveMsg').val() === 'True';
        $.ajax({
            url: location.pathname,
            type: 'put',
            dataType: 'json',
            data: {
                act: 'save',
                content: currentContent,
                post_uuid: uuid
            },
            beforeSend: function(xhr, settings){
                if (showMsg){
                    layer.msg('自动保存中...',{offset: 'rb',icon:0});
                }
                else{
                    console.log('自动保存中...');
                }
            },
            success: function(data){
                if (showMsg){
                    layer.msg(data.msg,{offset: 'rb',icon: 1});
                }
                else{
                    console.log(data.msg);
                }
            },
            error: function(xml,err,exc){
                var msg;
                try{
                    msg = JSON.parse(xml.responseText).msg;
                }
                catch(e){
                    msg = '未知错误';
                }
                if (showMsg){
                    layer.msg(msg,{offset: 'rb',icon: 1});
                }
                else{
                    console.log(msg);
                }
            }
        })
    }
    var autosaveIntervalNum;
    try{
        autosaveIntervalNum = parseInt($('#autosaveIntervalNum').val());
    }
    catch(e){
        autosaveIntervalNum = 5;
    }
    setInterval(autoSave,autosaveIntervalNum * 60 * 1000);
    //setInterval(autoSave,10 * 1000);

});
});