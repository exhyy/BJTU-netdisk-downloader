import requests
import json
import argparse
import os
from lxml import etree

def get_argparser():
    description = "Downloader for BJTU-Netdisk"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-l", "--link", type=str, required=True, help="The share link")
    parser.add_argument("-p", "--password", type=str, required=True, help="The password (case-sensitive)")
    parser.add_argument("--output_path", type=str, default="./output", help="The path where you want to save your file")
    parser.add_argument("-r", "--rename", type=str, default="", help="The filename you want to use. The original filename is used by default.")
    return parser

def check_password(link, password):
    check_url = 'https://mail.bjtu.edu.cn/coremail/s/json?func=nf:checkFilePassword'
    data = {}
    elements = link.split("download.jsp?")
    elements = elements[1].split("&")
    for e in elements:
        pair = e.split("=")
        data[pair[0]]=pair[1]
    data["password"] = password
    check = requests.post(check_url, data=json.dumps(data))
    return check.status_code == 200

if __name__ == '__main__':
    parser = get_argparser()
    args = parser.parse_args()
    if args.link[-1] == '/' or args.link[-1] == '\\':
        args.link = args.link[:-1]
    if check_password(args.link, args.password):
        url = args.link + "&func=nf:downloadFile&password=" + args.password
        response = requests.post(url)
        if response.status_code == 200:
            if args.rename != "":
                filename = args.rename
            else:
                # 读取原文件名
                html = etree.HTML(requests.get(args.link).text)
                filename = html.xpath('/html/body/div[2]/div[2]/div[1]/h4/text()')
                filename = filename[0]
            filename = os.path.join(os.path.abspath(args.output_path), filename)
            if not os.path.exists(args.output_path):
                os.makedirs(args.output_path)
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"File saved to \"{filename}\"")
        else:
            print("Download UNSUCCESSFULLY!")
    else:
        print("Incorrect password!")

