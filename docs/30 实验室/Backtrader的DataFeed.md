# Bt框架的数据源







## 路线一：基于csv文件

使用类：bt.feeds.GenericCSVData



```python
params = (
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
        ('tmformat', '%H:%M:%S'),

        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', 6),
)
```

### 建立我的csv文件格式数据源

继承bt.feeds.GenericCSVData，开发基于自己格式的csv文件数据源。

**添加自己的特殊列**，回测调用，绘图调用

### 添加新列



```python
class GenericCSV_PE(bt.feeds.GenericCSVData):
    """ 增加一列PE的Datafeed """

    # 添加一列'pe'
    lines = ('pe',)
	
    params = (('pe', (7-1)),)   # 第7列
```







## 路线二：基于Pandas



### 基于本地csv文件



```python
def get_csv_pd_datafeed():
    # 使用PandasData对象读取csv文件
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=datetime.datetime(2016, 12, 1), todate=datetime.datetime(2016, 12, 10),
                               open=1-1,
                               close=2-1,
                               high=3-1,
                               low=4-1,
                               )
    return data
```







### 基于互联网 API

### Tushare定制

### 基于本地数据库

pd.

















