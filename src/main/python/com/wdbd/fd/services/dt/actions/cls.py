import com.wdbd.fd.services.dt.actions.akshare_action as ak


def download_daily():
    a1 = ak.Ak_SSE_Summary()
    a1.handle()

    print("-" * 20)
    a2 = ak.Ak_Stock_Cal()
    a2.handle()


if __name__ == "__main__":
    download_daily()
