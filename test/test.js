/**
 * Created by weiyz18939 on 2019/2/25.
 */

$(document).ready(function(){
    function makeCategory(nodes) {
        var res = '<div class="category">';
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            m = $(node)[0].tagName.match(/H([12345])/);
            if (!m) {
                continue;
            }
            var level = m[1];
            res += '<div class="category-' + level + '"><a href="#'+$(node).attr('id')+'">' + $(node).text() + '</a></div>';
        }

        res += '</div>';
        return res;
    }
});