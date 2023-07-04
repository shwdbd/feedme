```sql
-- 银行股指标表
DROP TABLE ods_bankstock_index ;
CREATE TABLE ods_bankstock_index (
	stockid VARCHAR(10),
	stock_name VARCHAR(20),
	fr_date VARCHAR(8),
	index_id VARCHAR(10),
	index_name VARCHAR(50),
	index_value NUMERIC,
	CONSTRAINT t_ods_bankstock_index_PK PRIMARY KEY (stockid,fr_date,index_id)
);

-- 银行财报处理情况表
DROP TABLE ods_bankstock_fr_handle_log;
CREATE TABLE ods_bankstock_fr_handle_log (
	stockid VARCHAR(10),
	stock_name VARCHAR(20),
	fr_date VARCHAR(8),
	handled VARCHAR(1),
    index_names VARCHAR(500),
    last_modifed_dt VARCHAR(8),
	CONSTRAINT t_ods_bankstock_fr_handle_log_PK PRIMARY KEY (stockid,fr_date)
);
```



