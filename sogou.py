#!/usr/local/bin/python3
import os
import json
import sys
from random import random
from time import time

import requests
import uuid
import hashlib
import simple_colors as C
from objectify_json import ObjectifyJSON
from request_data import headers, data as body
from jsonkv import JsonKV


version = "2.7"
cache_dir = os.getenv("SOGOU_CACHE_DIR", os.path.expanduser("~/.sogou/"))
DEBUG = os.getenv("DEBUG")


def prepare_dir(path):
    if not path.endswith("/"):
        path = os.path.dirname(path)

    if not os.path.isdir(path):
        os.makedirs(path)


prepare_dir(cache_dir)
db = JsonKV(os.path.join(cache_dir, "translate.cache.json"))
COOKIE_FILE = os.path.join(cache_dir, "cookie.json")


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="text or file path startswith '/'")
    parser.add_argument("--gray", default=False, action="store_true", help="no colors")
    parser.add_argument(
        "--cache", default=False, action="store_true", help="cache http results"
    )
    args = parser.parse_args()
    return args


def get_text(text):
    text = text.strip()
    if text.startswith("/") and os.path.isfile(text):
        with open(text) as f:
            return f.read().strip()
    if text == "-":
        return sys.stdin.read().strip()
    return text


def md5(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


def parse_cookies(text):
    return {x.strip().split('=')[0]: x.strip().split('=')[1] for x in text.split(';')}


def get_cookies() -> dict:
    return {}
    ck = read_file(COOKIE_FILE)
    def _parse_ck(ck):
        if ck:
            try:
                return json.loads(ck)
            except Exception:
                return parse_cookies(ck)

    cks = _parse_ck(ck)
    if not cks:
        if DEBUG:
            host = 'http://127.0.0.1:7379'
        else:
            host = 'https://kv.drink.cafe'
        ck = requests.get(f'{host}/GET/sogou-translate-cookies').json()['GET']
        cks = _parse_ck(ck)
        if not cks:
            raise Exception(f'get cookies fail: {cks}')
        write_file(COOKIE_FILE, json.dumps(cks))
        return cks


def get_seccode():
    import js2py

    UA = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    )

    headers = {
        "Sec-Fetch-Mode": "no-cors",
        "User-Agent": UA,
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://translate.sogou.com/",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }

    def get_suv():
        return str(int(time() * 1000000) + int(random() * 1000))

    def get_seccode_cookies():
        res = requests.get("https://translate.sogou.com/", headers=headers)
        return {
            "SNUID": res.cookies.get("SNUID"),
            "SUID": res.cookies.get("SUID"),
            "ABTEST": res.cookies.get("ABTEST"),
            "IPLOC": res.cookies.get("IPLOC"),
            "SUV": get_suv(),
        }

    cookies = get_seccode_cookies()
    response = requests.get(
        "https://translate.sogou.com/logtrace", headers=headers, cookies=cookies
    )
    if DEBUG:
        print(response.status_code, response.text)
    text = response.text
    rv = js2py.eval_js(text + "; window.seccode;")
    return str(rv)


def read_file(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    if os.path.isfile(path):
        with open(path) as f:
            return f.read()
    return None


def write_file(path, content):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    prepare_dir(path)
    with open(path, "w") as f:
        return f.write(content)


def cal_secret(data):
    """
    the key point
    """
    # key = "front_9ee4f0a1102eee31d09b55e4d66931fd"
    # key = "41ee21a5ab5a13f72687a270816d1bfd"
    # key = "b33bf8c58706155663d1ad5dba4192dc"
    key_file = os.path.join(cache_dir, "key.txt")
    key = read_file(key_file)
    if not key:
        key = get_seccode()
        write_file(key_file, key)
    a = f"{data['from']}{data['to']}{data['text']}{key}"
    data["s"] = md5(a)
    if DEBUG:
        print(key, a, md5(a))


def get_data(data, args):
    text = get_text(args.text)
    data["text"] = text
    data["uuid"] = str(uuid.uuid4())
    cal_secret(data)
    return data


def http_post_translate(args):
    # disable colors for integrating with alfred
    data = get_data(body, args)
    if DEBUG:
        print(data)
    return do_request(data, args)


def do_request(data, args):
    api = "https://translate.sogou.com/reventondc/translateV2"
    cookies = get_cookies()
    if args.cache:
        with db:
            key = f'{data["text"]}-{args.__dict__}'
            v = db[key]
            if v:
                return v
            res = requests.post(api, headers=headers, cookies=cookies, data=data)
            data = res.json()
            v = res.status_code, data
            # clear cache
            if len(db.data) > int(os.getenv("SOGOU_CACHE_SIZE", 1000)):
                db.data = {}
            db[key] = v
            return v
    else:
        if DEBUG:
            print("-" * 100)
            print(api)
            print(headers)
            print(cookies)
            print(data)
            print("-" * 100)
        res = requests.post(api, headers=headers, cookies=cookies, data=data)
        data = res.json()
        v = res.status_code, data
        return v


def main():
    args = parse_args()
    status_code, data = http_post_translate(args)

    if args.gray:
        yellow = green = lambda x: x
    else:
        green = C.green
        yellow = C.yellow

    if status_code == 200 and data.get("status") == 0:
        if DEBUG:
            print(data)
        data = ObjectifyJSON(data["data"])
        bilingual = data.bilingual.data.list

        if os.getenv("SOGOU_SIMPLE"):
            print(data.translate.text)
            print(data.translate.dit)
        else:
            print("{}: {}".format(green("  From"), data.translate["from"]))
            print("{}: {}".format(green("    To"), data.translate.to))
            print("{}: {}".format(green("  Text"), data.translate.text))
            print("{}: {}".format(green("Result"), data.translate.dit))

            if bilingual:
                print("")
                for i, eg in enumerate(bilingual, start=1):
                    print(f"{yellow(i)}. {green(eg.summary.source)}")
                    print(f"   {eg.summary.target}\n")

    else:
        print(status_code)
        print(data)
        sys.exit(1)


if __name__ == "__main__":
    main()
