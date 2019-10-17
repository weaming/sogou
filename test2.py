def get_suv(snuid):
    import requests
    import time
    from urllib.parse import urlencode
    import uuid

    data = {
        "uigs_cl": "first_click",
        "uigs_refer": "",
        "uigs_t": str(int(round(time.time() * 1000))),
        "uigs_productid": "vs_web",
        "terminal": "web",
        "vstype": "weixin",
        "pagetype": "result",
        "channel": "result_account",
        "s_from": "",
        "sourceid": "",
        "type": "weixin_search_pc",
        "uigs_cookie": "SUID%2Csct",
        "uuid": uuid.uuid1(),
        "weixintype": "1",
        "exp_status": "-1",
        "exp_id_list": "0_0",
        "wuid": "",
        "snuid": snuid.split("=")[-1],
        "rn": "1",
        "login": "0",
        "uphint": "0",
        "bottomhint": "0",
        "page": "1",
        "exp_id": "null_0-null_1-null_2-null_3-null_4-null_5-null_6-null_7-null_8-null_9",
        "time": "20429",
    }
    suv_url = "https://pb.sogou.com/pv.gif?" + urlencode(data)

    response = requests.get(suv_url)
    print(response, response.cookies)


get_suv('B5DF86EA9E9B0BBF66E57CCE9F7A8143')
