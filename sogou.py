import os
import sys
import requests
import uuid
import hashlib
from simple_colors import *
from objectify_json import ObjectifyJSON
from request_data import headers, cookies, data as body

version = '1.0'


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    args = parser.parse_args()
    return args


def get_text(text):
    text = text.strip()
    if text.startswith('/') or text == '-':
        return sys.stdin.read()
    return text


def md5(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


def cal_secret(data):
    """
    the key point
    """
    key = 'front_9ee4f0a1102eee31d09b55e4d66931fd'
    a = f"{data['from']}{data['to']}{data['text']}{key}"
    data['s'] = md5(a)


def get_data(data, args):
    text = get_text(args.text)
    data['text'] = text
    data['uuid'] = str(uuid.uuid4())
    cal_secret(data)
    return data


def main():
    args = parse_args()

    api = 'https://translate.sogou.com/reventondc/translateV1'
    req_data = get_data(body, args)
    if os.getenv('DEBUG'):
        print(req_data)

    res = requests.post(
        api,
        headers=headers,
        cookies=cookies,
        data=req_data,
    )
    data = res.json()
    if res.status_code == 200 and data.get('status') == 0:
        data = ObjectifyJSON(data['data'])
        bilingual = data.bilingual.data.list

        if os.getenv("SOGOU_SIMPLE"):
            print(data.translate.text)
            print(data.translate.dit)
        else:
            print("{}: {}".format(green("  From"), data.translate['from']))
            print("{}: {}".format(green("    To"), data.translate.to))
            print("{}: {}".format(green("  Text"), data.translate.text))
            print("{}: {}".format(green("Result"), data.translate.dit))

            if bilingual:
                print('')
                for i, eg in enumerate(bilingual, start=1):
                    print(f"{yellow(i)}. {green(eg.summary.source)}")
                    print(f"   {eg.summary.target}\n")

    else:
        print(res.status_code)
        print(data)
        sys.exit(1)


if __name__ == '__main__':
    main()
