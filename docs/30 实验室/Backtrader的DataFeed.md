# Bt框架的数据源

如何向backtrader回测框架提供Datafeed数据源，尝尝是初学者的拦路虎。

本文档面向初学者，用代码实例演示如何构建Bt框架的数据源（Datafeed）

Bt框架提供了很多现成的Datafeed（参考：https://backtrader.com/docu/dataautoref/），其中可分两大类：

一、基于csv文件的

二、基于pandas的。

## 路线一：基于csv文件

可以直接使用bt.feeds.GenericCSVData读取csv文件。

调用者可以根据自己文件的情况，调整参数以取得正确的Datafeed。可以调整的参数，主要是“格式参数”和“列参数”。默认的参数如下：

格式参数为全局参数，有：

| 参数      | 说明               | 默认值            |
| --------- | ------------------ | ----------------- |
| nullvalue |                    | float('NaN')      |
| dtformat  | 文件中日期列的格式 | %Y-%m-%d %H:%M:%S |
| tmformat  | 文件中时间列的格式 | %H:%M:%S          |

列参数为定义每个列的情况，用户可以指定每个列所处的位置或字段信息。

例如：('open', 1) 表示open列在文件中第2列（从第0列开始计算），其参数也可以是str，表明所处的列名，如('open', “open”)

GenericCSVData中默认有7个列，这7个列必须存在或显示声明不存在。他们是：

- ('datetime', 0),
- ('time', -1),
- ('open', 1),
- ('high', 2),
- ('low', 3),
- ('close', 4),
- ('volume', 5),
- ('openinterest', 6)

列参数可以选择的内容有以下几种：

| 值         | 说明                                   |      |
| ---------- | -------------------------------------- | ---- |
| None       | 说明这列不存在                         |      |
| -1         | 自动匹配，bt框架会根据列名查找相同的列 |      |
| 0,1,2, ... | 文件中所在列位置，从0开始              |      |
| str        | 文件中对应的列名                       |      |

#### 代码示例

```python
# 使用GenericCSVData读取csv文件
def get_csv_datafeed():
    # 使用GenericCSVData读取csv文件
    
    # 本地文件路径
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    data = bt.feeds.GenericCSVData(dataname=datapath,
                                   fromdate=datetime.datetime(2016, 12, 1),
                                   todate=datetime.datetime(2016, 12, 4),
                                   dtformat=('%Y-%m-%d'),
                                   datetime=0,			   # datetime列在第1列
                                   close=(3-1),			   # close列在第3列
                                   openinterest=None,      # 指明无此列
                                   )
    return data
```



继承bt.feeds.GenericCSVData，开发基于自己格式的csv文件数据源。

**添加自己的特殊列**，回测调用，绘图调用

### 添加新列

*如果bt框架提供的列不够用怎么办？*

Bt允许我们继承GenericCSVData，并个性化定义自己的列。下面就是添加PE列的例子

```python
class GenericCSV_PE(bt.feeds.GenericCSVData):
    """ 增加一列PE的Datafeed """

    # 添加一列'pe'
    lines = ('pe',)
	
    params = (('pe', (7-1)),)   # 第7列
```

其中需要在两处添加定义：

1. lines中添加一列，名为pe
2. params中添加pe列的定义，其位置在第7列。

## 路线二：基于Pandas

非csv文件格式数据源，只要能读取成为pd.Dataframe都可以转成DataFeed。

这种场景有：

- 各类pd支持的文件（如：xxx）
- 支持pd的各类互联网api接口
- 各类关系型数据库。

构建bt.feeds.PandasData时需要注意：

- 日期、时间列必须是dataframe的index列；

### 基于本地csv文件



```python
def get_csv_pd_datafeed():
    # 使用PandasData对象读取csv文件
    # 文件路径
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=dataframe,
                               fromdate=datetime.datetime(2016, 12, 1),
                               todate=datetime.datetime(2016, 12, 10),
                               open=1-1,
                               close=2-1,
                               high=3-1,
                               low=4-1,
                               )
    return data
```







### 

### Tushare API

### 基于本地数据库

pd.



## 附件1 CSV示例文件

```csv
datetime,open,close,high,low,volume,pe
2016-12-01,12.424,22.433,2.45,2.418,345810322.0,1
2016-12-02,2.111,2.222,2.433,2.403,359834282.0,2
2016-12-05,2.392,2.373,2.393,2.364,455702257.0,3
2016-12-06,2.372,2.368,2.383,2.367,203386391.0,4
2016-12-07,2.368,2.375,2.376,2.361,210462691.0,5
2016-12-08,2.379,2.38,2.388,2.375,230304569.0,6
2016-12-09,2.378,2.413,2.421,2.372,362651828.0,7
```

















