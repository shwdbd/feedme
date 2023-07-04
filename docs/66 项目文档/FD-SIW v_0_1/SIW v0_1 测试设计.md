本文档的目的是规划、设计单元测试方面工作，作为后续开发的依据。

# 测试范围

依照 [SIW v0.1 产品需求文档](https://shimo.im/docs/rLkORCRnEFMVohSp) 中的功能需求，开展单元测试。

仅测试项目内功能，Feedme项目公共需求不涉及。

# 测试代码规则

测试代码存放在项目测试文件夹（src\test）下

项目代码存放在：src\test\python\com\wdbd\feedme\fd\siw

测试代码符合Python单元测试代码规则

# 单元测试清单

## TestSuite

全部测试代码归并在 com.wdbd.feedme.fd.siw.SIW_V_0_1_Suite.py 内

## TestCase清单

需要实现以下这些单元测试

|测试类|用例|说明|
|:----|:----|:----|
|test_cmbc|解析民生银行财报|    |
|TestCMBCExactor|test_exactor_2022Annual|解析22年年报|
|    |test_exactor_2021Annual|解析21年年报|
|    |test_exactor_2023_Q1|解析23年一季报|
|test_fr_exactor|测试财报读取器功能|    |
|TestFrExactor|test_single_file|单个解析文件|
|    |test_load_by_folder|解析整个文件夹目录|
|test_tools|测试SIW公共工具类功能|    |
|TestSIWTools|test_check_rpfile_format|检查 财报文件名|
|    |test_get_exception_logger|检查 获取异常日志|
|    |test_to_number|中文数字转浮点|
|    |test_get_stock_info|根据文件解析财报信息|
|    |test_archive_file|文件备份|
|    |test_save_to_db|指标集存入数据库|
|**test_icbc**|解析工商银行财报|    |
|TestICMBCExactor|test_exactor_2022Annual|解析22年年报|
|    |test_exactor_2021Annual|解析21年年报|
|    |test_exactor_2023_Q1|解析23年一季报|
|**test_cib**|解析兴业银行财报|    |
|TestCIBxactor|test_exactor_2022Annual|解析22年年报|
|    |test_exactor_2021Annual|解析21年年报|
|    |test_exactor_2023_Q1|解析23年一季报|





