# import akshare as ak
# import pandas as pd
from com.wdbd.fd.model.dt_model import ActionConfig
from com.wdbd.fd.services.dt.actions.akshare_action import AkStockHistoryData, AkStockInfoShNameCode, AkStockInfoBjNameCode, AkStockInfoSzNameCode, AkshareStockList


if __name__ == '__main__':
    config = ActionConfig()
    config.name = 'AK 股票日线'
    config.p["DOWNLOAD_ALL"] = False
    config.p["trade_date"] = '20240430'
    # config.p["start_date"] = '20240401'
    # config.p["end_date"] = '20240403'
    # config.p["symbol_list"] = ['600016.SH', '000001.SZ']
    # config.p["symbol_list"] = ['200011.SZ']

    action = AkStockHistoryData()
    action.set_action_parameters(config)
    result = action.handle()
    print(result)


# if __name__ == '__main__':
#     action = AkStockInfoShNameCode()
#     result = action.handle()
#     print(result)
#     action = AkStockInfoSzNameCode()
#     result = action.handle()
#     print(result)
#     action = AkStockInfoBjNameCode()
#     result = action.handle()
#     print(result)
    
#     action = AkshareStockList()
#     result = action.handle()
#     print(result)
