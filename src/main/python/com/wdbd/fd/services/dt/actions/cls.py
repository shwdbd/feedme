import com.wdbd.fd.services.dt.actions.akshare_action as ak


def download_daily():
    # 
    a1 = ak.AkSSESummaryDataDownloader()
    a1.handle()

    print("-" * 20)
    # 交易日历
    a2 = ak.AkStockCalDownloader()
    a2.handle()


if __name__ == "__main__":
    download_daily()
