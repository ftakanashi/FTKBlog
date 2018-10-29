/**
 * Created by weiyz18939 on 2018/10/29.
 */
$(function(){
$(document).ready(function(){
    $('.login-title,.login-panel').fadeIn(1000);
    $('.bg').fadeIn(1000);

    // 换词菜单
    $('.login-title').click(function(event){
        $.ajax({
            url: location.pathname + '?changeslogan=true',
            type: 'get',
            dataType: 'json',
            data: {},
            success: function(data){
                $('#slogan').text(data.slogan);
                $('#slogan-author').text('——' + data.author);
            }
        });
    });


    $('#submit').click(function(event){
        event.preventDefault();

        var u = $('#usernameInput').val();
        if (u == ''){
            layer.tips('用户名不能为空','#usernameInput',{tips: [2,'#a94442']});
            return;
        }

        var p = $('#passwordInput').val();
        if (p == ''){
            layer.tips('密码不能为空','#passwordInput',{tips: [2,'#a94442']});
            return;
        }

        var load;
        $.ajax({
            url: location.pathname,
            type: 'post',
            dataType: 'json',
            data: {
                u: u,
                p: p
            },
            beforeSend: function(){
                load = layer.load('1');
            },
            complete: function(){
                layer.close(load);
            },
            success: function(data){
                if(data.next){
                    location.pathname = data.next;
                }
                else{
                    location.pathname = '/';
                }
            },
            error: function(xml,err,exc){
                var res;
                try{
                    var jsonRes = JSON.parse(xml.responseText);
                    msg = jsonRes.msg;
                }
                catch(e){
                    msg = '未知错误';
                }
                layer.alert(msg,{icon: '2',title: false, btn: false});
            }
        });
    });
}).keyup(function(event){
    if(event.keyCode == '13'){
        $('#submit').trigger('click');
    }
});
});