#!/usr/bin/env python

import os
import argparse

from dream_dl.dataclasses import *
import dream_dl.source_downloader as sd
import dream_dl.network_downloader as nd

parser = argparse.ArgumentParser(description="Download a video from any website")
parser.add_argument("url", type=str, help="URL of the video")
parser.add_argument("path", type=str, help="Path to save the video")
parser.add_argument("downloader", type=str, help="Downloader to use", choices=["source", "network"])
parser.add_argument("--use-js-injection", "-uji", action="store_true", help="Use JS injection mode", required=False)
parser.add_argument("--use-curl", "-ucurl", action="store_true", help="Use CURL mode", required=False)
parser.add_argument("--force", "-f", action="store_true", help="Force download even if file exists", required=False)
parser.add_argument("--load_sleep", "-ls", type=int, help="Time (s) to wait between loading page and starting script", default=5, required=False)

args = parser.parse_args()

# check path dir exists
path = os.path.abspath(args.path)
if not os.path.exists(os.path.dirname(path)):
    print(f"Path {os.path.dirname(args.path)} does not exist")
    exit(1)
if os.path.exists(path) and not args.force:
    print(f"File {path} already exists")
    exit(1)
if os.path.exists(path) and args.force:
    os.remove(path)

config = Config()
webpage = Webpage(url = args.url)

if args.downloader == "source":
    methods = []
    if args.use_js_injection:
        methods.append(sd.DM.JS_INJECTION)
    if args.use_curl:
        methods.append(sd.DM.CURL)
    if len(methods) == 0:
        methods.append(sd.DM.JS_INJECTION)

    res = sd.download(
        config = config,
        webpage = webpage,
        path = path,
        modes = methods,
        timeout = 600,
    )
elif args.downloader == "network":
    res = nd.download(
        config = config,
        webpage = webpage,
        path = path,
        timeout = 600,
    )
if isinstance(res, Error):
    print(f"Error: {res.msg}")
    exit(1)