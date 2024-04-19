# import akshare as ak
# import pandas as pd
from com.wdbd.fd.model.dt_model import ActionConfig
from com.wdbd.fd.services.dt.actions.akshare_action import AkStockInfoSzNameCode


if __name__ == '__main__':
    config = ActionConfig()
    config.name = 'AK 交易日历'
    config.p["DOWNLOAD_ALL"] = True

    action = AkStockInfoSzNameCode()
    result = action.handle()
    print(result)
    