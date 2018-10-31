/**
 * Created by weiyz18939 on 2018/10/30.
 */
$(function(){
$(document).ready(function(){
    // 界面初始化工作
    $('.tag-check').click(function(){
        $(this).toggleClass('active');
    });

    $('#categorySelect').select2({
        language: 'zh-CN'
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
        markdown: '',
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
        imageUploadUrl: location.pathname + 'upload/'
    });

    // 先验自动保存
    var autoSavePre = JSON.parse($.cookie('autosave'));
    if(autoSavePre && (Date.now() - autoSavePre.timestamp) < 1000 * 10 * 60){
        layer.confirm('发现最近('+moment(autoSavePre.timestamp).fromNow()+')自动保存的内容，是否恢复？',{icon:3,title:'提示'},function(index){
            contentEditor.insertValue(autoSavePre.content);
            layer.msg('恢复成功',{offset: 'lb'});
        });
    }

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
        var title = $('#titleInput').val();
        if (!title){
            $.scrollTo('titleInput');
            layer.tips('标题不能为空','#titleInput',{tips: [1,'darkred']});
            return;
        }
        var content = contentEditor.getMarkdown();
        var category = $('#categorySelect').val();
        if (!category){
            $.scrollTo('categorySelect');
            layer.tips('请选择分类','#categorySelect',{tips: [1,'darkred']});
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
            isPublished = 'false';
        }

        $.ajax({
            url: location.pathname,
            type: 'post',
            dataType: 'json',
            data: {
                title: title,
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
                $.cookie('autosave',null);
                setTimeout('location.href = "' + next + '"', 3000);
                layer.load('1',{shade: 0.5});
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
            }
        });

    });

    // 手动恢复缓存内容
    $('#restoreContent').click(function(event){
        var autoSave = JSON.parse($.cookie('autosave'));
        if (!autoSave){
            layer.msg('抱歉，没有找到自动保存内容');
            return;
        }
        layer.confirm('是否恢复最近( '+moment(autoSave.timestamp).fromNow()+')的自动存档?',{icon:3,title:'提示'},function(index){
            contentEditor.clear().insertValue(autoSave.content);
            layer.msg('恢复完成',{offset: 'lb'});
        });
    });

    // todo 博文自动保存
    function autoSave(){
        layer.msg('自动保存中...',{offset: 'lb'});
        var currentContent = contentEditor.getMarkdown();
        $.cookie('autosave',JSON.stringify({'timestamp': Date.now(),'content': currentContent}));
        layer.msg('自动保存成功',{offset: 'lb'});
    }
    setInterval(autoSave,3 * 60 * 1000);

});
});