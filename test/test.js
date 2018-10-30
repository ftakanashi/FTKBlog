/**
 * Created by weiyz18939 on 2018/10/30.
 */

$(function(){
    $(document).ready(function(){
        var textEditor;
        textEditor = editormd('content',{
            width: '80%',
            height: 740,
            path: 'editormd/lib/',
            markdown: '',
            codeFold: true,
            saveHtmlToTextarea: true,
            searchPlace: true,
            watch: true,
            htmlDecode: 'style,script,iframe|on*',
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
            imageUploadUrl: '/upload',
            onload: function(){

            }
        });
        $('#mybutton').click(function(event){
            console.log(textEditor.getMarkdown());
        });
    });
});