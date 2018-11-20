/**
 * Created by weiyz18939 on 2018/11/8.
 */
$(function(){
    function refreshVeriCode(callback, complete){
        var veriCodeInput = $('#veriCodeInput');
        $.ajax({
            url: $('#veri-code-url').val(),
            type: 'get',
            dataType: 'json',
            data: {veri_code_uuid: $(veriCodeInput).attr('name')},
            success: function(data){
                $(veriCodeInput).attr('name',data.veri_code_uuid).
                prev('img').attr('src', 'data:image/jpeg;base64,' + data.veri_code).
                parent().show();
                callback(0);
            },
            error: function(xml, err, exc){
                try{
                    layer.msg(JSON.parse(xml.responseText).msg);
                }
                catch(e){
                    layer.msg('未知错误');
                }
                callback(1);
            },
            complete: complete
        });
    }

    $(document).ready(function(){

        $('body').trigger('loadTheme');

        $('.form-group.required').each(function(i,ele){
            $(ele).prepend('<span class="text-danger">*</span>');
        });

        $('#relatePostCheck').change(function(event){
            $(this).parents('div.row').find('div:nth-child(2)').slideToggle('slow');
        });

        $('#relatePostSelect').select2({
            language: 'zh-CN',
            width: '100%'
        });

        //获取 & 刷新验证码
        $('.refresh-veri-code').click(function(event){
            var loadLayer = layer.load('2');
            var btn = $(this);
            var constant = $(this).hasClass('constant');
            refreshVeriCode(function(status){
                if (status === 0 && !constant){
                    $(btn).parent().hide();
                }
            },function(){
                layer.close(loadLayer);
            });
        });

        $('#submit').click(function(event){
            event.preventDefault();
            var loadLayer = layer.load('1',{shade: 0.6});
            var author = $('#authorInput').val();
            var contact = $('#contactInput').val();
            var title = $('#titleInput').val();
            var content = $('#contentInput').val();
            var relatePost = $('#relatePostSelect').val();
            var veriCode = $('#veriCodeInput').val();
            var veriCodeUuid = $('#veriCodeInput').attr('name');

            if (!author){
                layer.tips('请填写此项','#authorInput',{tips: [3,'red']});
                $.scrollTo('#authorInput');
                layer.close(loadLayer);
                return;
            }

            if (!content){
                layer.tips('请填写此项','#contentInput',{tips: [1,'red']});
                $.scrollTo('#contentInput');
                layer.close(loadLayer);
                return;
            }
            $.ajax({
                url: location.pathname,
                type: 'post',
                dataType: 'json',
                data: {
                    author: author,
                    contact: contact,
                    title: title,
                    content: content,
                    relatePost: relatePost,
                    veriCode: veriCode,
                    veriCodeUuid: veriCodeUuid
                },
                complete: function(){layer.close(loadLayer);},
                success: function(data){
                    layer.msg('留言成功，谢谢反馈');
                    setTimeout('location.href="/"',1000);
                },
                error: function(xml, err, exc){
                    try{
                        layer.msg(JSON.parse(xml.responseText).msg);
                        if(xml.status === 502){
                            $('.refresh-veri-code.constant').trigger('click');
                        }
                    }
                    catch(e){
                        layer.msg('未知错误');
                    }
                }
            });
        });
    });
});