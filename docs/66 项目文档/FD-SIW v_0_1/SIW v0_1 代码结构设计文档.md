本文档为项目Python结构设计文档，共开发与单元测试参考使用。

# 包设计

项目代码存放在 com.wdbd.feedme.fd.siw 包中。

包之间依赖关系如下图：

![图片](data:image/png;base64,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)


## 包依赖

需要用到以下包：

|包|说明|
|:----|:----|
|com.wdbd.feedme.fd.common.common.py|公共工具|
|com.wdbd.feedme.fd.orm.ods_tables.py|ODS表实体类|

## Lib依赖

需要依赖的类包有：

|Lib|说明|
|:----|:----|
|pdfplumber|pdf文件解析|

# 类设计

com.wdbd.feedme.fd.siw 包主要类有：

|Module|Class|说明|
|:----|:----|:----|
|__init__.py|FinanceReportExactor|银行股股票指标 读取器|
|    |FinanceReport|财报文件对象|
|tools.py|    |项目工具对象和函数|
|cli.py|    |命令行接口代码|
|banks.py|AbstractStockExactor|单一股票财报提取器(抽象基类)|
|    |CMBC|民生银行，提取器|
|    |ICBC|工商银行，提取器|
|    |CIB|兴业银行，提取器|

## Tools公共工具类

tools.py中集中工具类函数，有：

* 异常日志，get_exception_logger
* 中文数字转浮点，to_number
* 检查 财报文件名 是否符合要求，check_rpfile_format
* 根据文件解析财报信息，get_stock_info
* 文件备份，archive_file
* 指标集存入数据库，save_to_db
## FinanceReportExactor

FinanceReportExactor是一个服务接口，面向GUI、命令行接口等提供统一封装程序。

目前提供 单一文件解析、按文件夹解析两个接口。

```python
def load_by_file(self, filename: str) -> dict:
        """
        读取单个文件并将解析到数据存入FD数据库
        需要做的事情有：
        1. 解析文件
        2. 数据存入数据库
        3. 文件归档

        返回值：
        正确则返回：
        {
          "result": True,
          "messages": "",
          "stock": {"id": "SH600016', 'name': 'xxxx', 'fr_date': '2023年年报'}
          "index": {"指标1": "abc", "指标2": "efg"}
        }
        错误返回：
        {
          "result": False,
          "messages": "出错信息"
        }

        Args:
            filename (str): 文件完整路径

        Returns:
            dict: 执行结果
        """
        pass
  
def load_by_dir(self, foloder_path) -> dict:
        """
        读取某个文件夹下的所有财报单个文件并将解析到数据存入FD数据库

        返回值：
        正确则返回：
        {
          "result": True,
          "messages": "",
          "files": {
              "文件1": {
                "result": True,
                "messages": "",
                "index": {"指标1": "abc", "指标2": "efg"}
              },
              "文件2": {
                "result": True,
                "messages": "",
                "index": {"指标1": "abc", "指标2": "efg"}
              },
          }
        }
        错误返回：
        {
          "result": False,
          "messages": "出错信息",
          "files": {
              "文件1": {
                "result": True,
                "messages": "xxxx"},
              "文件2": {
                "result": True,
                "messages": "xxxx"},
          }
        }
        """
        # TODO 待实现
        return None
```

## AbstractStockExactor数据提取器

详细说明

## CLI命令行接口

cli.py存放命令行接口代码，使用 click 类库实现。

**命令1：解析财报文件命令：**

fd_cli.py siw **load** [OPTIONS]

Options:

  -d, --dir TEXT   按文件夹解析，参数指定目录位置

  -f, --file TEXT   按单个文件解析，参数指定文件绝对路径

**命令2：查询指标命令：**

fd_cli.py siw **query** [OPTIONS]

Options:

  -s, --stock TEXT  股票代码或名称，支持模糊查询

  -t, --time TEXT  财报期限，支持yyyyQn，或 yyyy年报 或仅 年份yyyy

  -i, --index TEXT  指标名称，支持模糊查询

