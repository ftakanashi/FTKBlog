/**
 * Created by weiyz18939 on 2018/10/30.
 */
// by zhangxixnu 2010-06-21  welcome to visit my personal website http://www.zhangxinxu.com/
// textSearch.js v1.0 文字，关键字的页面纯客户端搜索
// 2010-06-23 修复多字母检索标签破碎的问题
// 2010-06-29 修复页面注释显示的问题
// 2013-05-07 修复继续搜素关键字包含之前搜索关键字没有结果的问题
// 不论何种情况，务必保留作者署名。

(function($){
    $.fn.textSearch = function(str,options){
        var defaults = {
            divFlag: true,
            divStr: " ",
            markClass: "",
            markColor: "red",
            nullReport: true,
            callback: function(){
                return false;
            }
        };
        var sets = $.extend({}, defaults, options || {}), clStr;
        if(sets.markClass){
            clStr = "class='"+sets.markClass+"'";
        }else{
            clStr = "style='color:"+sets.markColor+";'";
        }

        //对前一次高亮处理的文字还原
        $("mark").each(function() {
            var text = document.createTextNode($(this).text());
            $(this).replaceWith($(text));
        });

        //字符串正则表达式关键字转化
        $.regTrim = function(s){
            var imp = /[\^\.\\\|\(\)\*\+\-\$\[\]\?]/g;
            var imp_c = {};
            imp_c["^"] = "\\^";
            imp_c["."] = "\\.";
            imp_c["\\"] = "\\\\";
            imp_c["|"] = "\\|";
            imp_c["("] = "\\(";
            imp_c[")"] = "\\)";
            imp_c["*"] = "\\*";
            imp_c["+"] = "\\+";
            imp_c["-"] = "\\-";
            imp_c["$"] = "\$";
            imp_c["["] = "\\[";
            imp_c["]"] = "\\]";
            imp_c["?"] = "\\?";
            s = s.replace(imp,function(o){
                return imp_c[o];
            });
            return s;
        };

        // weiyz修改 增加查找所有子字符串位置的函数
        $.allIndexOf = function(str,substr){
            var indices = [];
            var index = str.indexOf(substr);
            while(index != -1){
                indices.push(index);
                index = str.indexOf(substr, index + substr.length);
            }
            return indices;
        };

        $(this).each(function(){
            var t = $(this);
            str = $.trim(str);
            if(str === ""){
                return false;
            }else{
                //将关键字push到数组之中
                var arr = [];
                if(sets.divFlag){
                    arr = str.split(sets.divStr);
                }else{
                    arr.push(str);
                }
            }
            var v_html = t.html();
            //删除注释
            v_html = v_html.replace(/<!--(?:.*)\-->/g,"");

            //将HTML代码支离为HTML片段和文字片段，其中文字片段用于正则替换处理，而HTML片段置之不理
            var tags = /[^<>]+|<(\/?)([A-Za-z]+)([^<>]*)>/g;
            var a = v_html.match(tags), test = 0;
            var foundCount = 0;
            $.each(a, function(i, c){
                if(!/<(?:.|\s)*?>/.test(c)){//非标签
                    //开始执行替换
                    $.each(arr,function(index, con){
                        if(con === ""){return;}
                        //weiyz 适配多查询
                        var reg = new RegExp('(?!♂)' + $.regTrim(con) + '(?!♀)');
                        if(reg.test(c)){
                            //正则替换
                            // weiyz修改 深入每行文字的替换
                            var founds = $.allIndexOf(c,con);
                            for(_ in founds){
                                foundCount ++;
                                c = c.replace(reg, "♂"+foundCount.toString()+"♂"+con+"♀");
                            }
                            test = 1;
                        }
                    });
                    // weiyz修改，给每个mark加上id方便跳转
                    c = c.replace(/♂(\d+?)♂/g,"<mark "+clStr+" id=\"textsearch_$1\">").replace(/♀/g,"</mark>");
                    a[i] = c;
                }
            });
            //将支离数组重新组成字符串
            var new_html = a.join("");

            $(this).html(new_html);

            if(test === 0 && sets.nullReport){
                return false;
            }

            //执行回调函数
            sets.callback(foundCount);
        });
    };
})(jQuery);