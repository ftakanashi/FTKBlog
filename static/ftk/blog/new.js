/**
 * Created by weiyz18939 on 2018/10/30.
 */
$(function(){
$(document).ready(function(){

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


    $('#reset').click(function(event){
        $('#titleInput,#abstractInput,#post-content-editor-markdown-doc,#post-content-editor-html-code').val('');
        $('.tag-check').removeClass('active');
        $('#categorySelect').val('').trigger('change');
        contentEditor.clear();
    });

    // todo 博文自动保存

});
});