# 使用Flask和Layui实现文件上传

本文目标是通过代码示例，演示开发Web版文件上传功能实现。

目标读者是对Layui和Flask有开发基础的开发者。

内容：

- 单个文件上传
- 多文件上传

## 单个文件上传

单个文件上传需要实现以下几个目标：

- 网页前端上用户选择文件上传，可对上传文件的类型、大小做限制；
- 网页前端上允许同一表单内文本框等常规组件和文件上传一并处理；
- 后台接受文件上传，可对文件做保存等处理，并按业务处理结果返回内容
- 后台可接收普通POST请求；
- 网页前端可接受后台返回值，并回显上传状态。

### 实现思路

前端说明

- 文件上传使用的是专用的layui.upload组件，官方文档：<http://layui-doc.pearadmin.com/doc/modules/upload.html>
- upload的表单提交，使用bindAction属性，绑定提交按钮；
- auto需要设置为false，否则会自动提交，不等用户点击上传按钮
- url是指向后台服务地址

后端说明：（flask实现）

- 使用request.files.get("file")方式取得上传的文件，f为File对象
- 返回值一定要按layui规范返回，其中data中内容可个性化处理

### 代码示例

前端网页代码：

```html
<h1>单个文件上传示例</h1>

<form class="layui-form" id="addform" name="addform" lay-filter="formConfig" method="post" action="/demo/file_upload/file_upload_action/" enctype="multipart/form-data">

    <div class="layui-form-item">
        <label class="layui-form-label">表单值V1</label>
        <div class="layui-input-block">
            <input type="text" name="v1" class="layui-input" id="v1" >
        </div>
    </div>

    <button type="button" class="layui-btn" id="upload_field">
        <i class="layui-icon">&#xe67c;</i>上传图片
    </button>
    <button type="button" class="layui-btn" id="upload_action">提交</button>

</form>

<script>
    layui.use(['upload', 'jquery'], function(){
        var $ = layui.jquery;
        var upload = layui.upload;
        
        //执行实例
        var uploadInst = upload.render({
            elem: '#upload_field' //绑定元素
            ,url: '/demo/file_upload/file_upload_action/' //上传接口
            ,auto: false        // 非自动提交
            ,multiple: false    // 一次提交一个文件
            ,accept: 'file'     // 允许上传的文件类型
            ,bindAction: '#upload_action'   // 绑定的上传动作按钮
            ,before: function() {
                // 将Form
                this.data = {
                    "v1": $("#v1").val()
                }
            }
            ,done: function(res){
                //假设code=0代表上传成功
                if(res.code == 0){
                    //do something （比如将res返回的图片链接保存到表单的隐藏域）
                    console.info("上传成功")
                    console.info(res)
                }
            }
            ,error: function(){
                //请求异常回调
                console.info("error")
            }
        });
    });
</script>
```

```python
# 单文件上传页
@bp.route('/file_upload')
def file_upload():
    """ 返回 单文件上传页 """
    return render_template('demo/file_upload.html')


# 单文件上传动作
@bp.route('/file_upload_action/', methods=['GET', 'POST'])
def file_upload_action():
    """ 返回 单文件上传动作 """
    # 接收表单数据：
    v1 = request.form.get('v1')
    print("v1 = {0}".format(v1))
    # 接受文件上传数据
    f = request.files.get("file")       # 获取前端传来的文件
    print("file = {0}".format(f))
    # f.save('C:\\temp\\{0}'.format(f.filename))       # 将文件保存下来
    print("上传、另存为 ok")
    # 返回值
    return {
        "code": 0, "msg": "上传成功", "data": {
            "v1": v1
        }
    }
```

## 多个文件上传

在单个文件上传基础上增加功能：

- 多个文件一并提交，提交前有待上传文件列表显示；
- 未上传前可删除待上传文件
- 上传后回显上传结果，几个成功，几个失败（是否可以回显更多的个性化内容）

代码实现要点：

- 多文件上传，实际是发起N个Post请求
- done 回调可将后台数据前传
- allDone回调可得到总计上传成功或失败的数量

### 代码示例

```html
<h1>多文件上传示例</h1>


<button type="button" class="layui-btn layui-btn-normal" id="testList">选择多文件</button>

<div class="layui-upload-list">
    <table class="layui-table">
    <thead>
        <tr>
        <th>文件名</th>
        <th>大小</th>
        <!-- <th>上传进度</th> -->
        <th>操作</th>
        </tr>
    </thead>
    <tbody id="demoList"></tbody>
    </table>
</div>
<button type="button" class="layui-btn" id="testListAction">开始上传</button>

<script>
    layui.use(['upload', 'element', 'layer'], function () {
        var $ = layui.jquery
        
        form = layui.form
          
        //演示多文件列表
        var upload = layui.upload;
        var uploadListIns = upload.render({
            elem: '#testList'
            ,elemList: $('#demoList') //列表元素对象
            ,url: '/demo/file_upload/file_multi_upload_action/'
            ,accept: 'file'
            ,multiple: true
            ,number: 3
            ,auto: false
            ,bindAction: '#testListAction'
            // ,progress: function(n, elem, e, index){ //注意：index 参数为 layui 2.6.6 新增
            //     element.progress('progress-demo-'+ index, n + '%'); //执行进度条。n 即为返回的进度百分比
            // }
            ,choose: function(obj){   
                var that = this;
                var files = this.files = obj.pushFile(); //将每次选择的文件追加到文件队列
                //读取本地文件
                obj.preview(function(index, file, result){
                var tr = $(['<tr id="upload-'+ index +'">'
                ,'<td>'+ file.name +'</td>'
                ,'<td>'+ (file.size/1014).toFixed(1) +'kb</td>'
                //,'<td><div class="layui-progress" lay-filter="progress-demo-'+ index +'"><div class="layui-progress-bar" lay-percent=""></div></div></td>'
                ,'<td>'
                    ,'<button class="layui-btn layui-btn-xs demo-reload layui-hide">重传</button>'
                    ,'<button class="layui-btn layui-btn-xs layui-btn-danger demo-delete">删除</button>'
                ,'</td>'
                ,'</tr>'].join(''));
                
                //单个重传
                tr.find('.demo-reload').on('click', function(){
                obj.upload(index, file);
                });
                
                //删除
                tr.find('.demo-delete').on('click', function(){
                delete files[index]; //删除对应的文件
                tr.remove();
                uploadListIns.config.elem.next()[0].value = ''; //清空 input file 值，以免删除后出现同名文件不可选
                });
                
                that.elemList.append(tr);
                //element.render('progress'); //渲染新加的进度条组件
            });
            }
            ,done: function(res, index, upload){ //成功的回调
                var that = this;
                if(res.code == 0){ //上传成功
                    var tr = that.elemList.find('tr#upload-'+ index)
                    ,tds = tr.children();
                    tds.eq(3).html(''); //清空操作
                    delete this.files[index]; //删除文件队列已经上传成功的文件
                    return;
                }
                this.error(index, upload);
            }
            ,allDone: function(obj){ //多文件上传完毕后的状态回调
                console.log(obj)
            }
            ,error: function(index, upload){ //错误回调
                var that = this;
                var tr = that.elemList.find('tr#upload-'+ index)
                ,tds = tr.children();
                tds.eq(3).find('.demo-reload').removeClass('layui-hide'); //显示重传
            }
            
        });
    });
</script>
```
