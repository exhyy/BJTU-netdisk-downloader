import requests
import json
import argparse
import os
from lxml import etree
from tqdm import tqdm
from urllib.parse import unquote

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
        data[pair[0]] = pair[1]
    data["password"] = password
    check = requests.post(check_url, data=json.dumps(data))
    return check.status_code == 200

if __name__ == '__main__':
    parser = get_argparser()
    args = parser.parse_args()
    if args.link[-1] == '/' or args.link[-1] == '\\':
        args.link = args.link[:-1]
    args.link = unquote(args.link)
    if check_password(args.link, args.password):
        url = args.link + "&func=nf:downloadFile&password=" + args.password
        response = requests.post(url, stream=True)
        if response.status_code == 200:
            if args.rename != "":
                filename = args.rename
            else:
                # 读取原文件名
                html = etree.HTML(requests.get(args.link).text)
                filename = html.xpath('/html/body/div[2]/div[2]/div[1]/h4/text()')
                filename = filename[0]
            dst = os.path.join(args.output_path, filename)
            if not os.path.exists(args.output_path):
                os.makedirs(args.output_path)
            file_size = int(response.headers["content-length"])
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=filename)
            with open(dst, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(1024)
            progress_bar.close()
            print(f"File saved to \"{dst}\"")
        else:
            print("ERROR: Download UNSUCCESSFULLY!")
    else:
        print("ERROR: Incorrect password!")

