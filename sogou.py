#!/usr/local/bin/python3
import os
import sys
import requests
import uuid
import hashlib
import simple_colors as C
from simple_colors import *
from objectify_json import ObjectifyJSON
from request_data import headers, cookies, data as body
from jsonkv import JsonKV


version = "1.5"
cache_dir = os.getenv("SOGOU_CACHE_DIR", os.path.expanduser("~/.sogou/"))


def prepare_dir(path):
    if not path.endswith("/"):
        path = os.path.dirname(path)

    if not os.path.isdir(path):
        os.makedirs(path)


prepare_dir(cache_dir)
db = JsonKV(os.path.join(cache_dir, "translate.cache.json"))


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--gray", default=False, action="store_true", help="no colors")
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


def cal_secret(data):
    """
    the key point
    """
    key = "front_9ee4f0a1102eee31d09b55e4d66931fd"
    key = "41ee21a5ab5a13f72687a270816d1bfd"
    a = f"{data['from']}{data['to']}{data['text']}{key}"
    data["s"] = md5(a)


def get_data(data, args):
    text = get_text(args.text)
    data["text"] = text
    data["uuid"] = str(uuid.uuid4())
    cal_secret(data)
    return data


def http_post_translate(args):
    # disable colors for integrating with alfred
    if args.gray:
        yellow = green = lambda x: x
    else:
        green = C.green
        yellow = C.yellow

    data = get_data(body, args)
    if os.getenv("DEBUG"):
        print(data)
    return do_request(data, args)


def do_request(data, args):
    api = "https://translate.sogou.com/reventondc/translateV1"
    with db:
        key = f'{data["text"]}-{args.__dict__}'
        v = db[key]
        if v:
            return v
        res = requests.post(api, headers=headers, cookies=cookies, data=data)
        data = res.json()
        v = res.status_code, data
        db[key] = v
        return v


def main():
    args = parse_args()
    status_code, data = http_post_translate(args)

    if status_code == 200 and data.get("status") == 0:
        if os.getenv("DEBUG"):
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
