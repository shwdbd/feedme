/** left_menu.js */
// 生成菜单的html
function get_menu_html(data) {
    html = ""
    for (var i = 0; i < data.length; i++) { 
        var node = data[i];
        // console.log(node);
        // console.log(node.authorityId)
        // console.log(node.authorityName)
        
        if (node.parentId == -1) {
            // 顶级菜单
            // console.log(node.authorityId)
            html += '<li class="layui-nav-item layui-nav-itemed">\n';
            html += '  <a class="" href="javascript:;">' + node.authorityName + '</a>\n'
        } else {
            // 普通节点
            html += '  <dl class="layui-nav-child" >\n'
            if (node.menuUrl != '') {
                html += '    <dd ><a href="' + node.menuUrl + '" target="main_frame">' + node.authorityName + '</a></dd>\n'
            } else {
                html += '    <dd ><a href="javascript:;">' + node.authorityName + '</a></dd>\n'
            }
        }

        // 有子节点
        if (node.data != null)
            // console.log(node.data)
            // console.log(get_menu_html(node.data))
            html += get_menu_html(node.data)       
        
        if (node.parentId == -1) {
            html += '</li>\n'
        } else {
            html += '  </dl>\n'
        }
    }
    return html
}