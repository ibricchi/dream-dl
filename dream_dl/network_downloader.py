from enum import Enum
import time
import os
import json

from dream_dl.base import DreamDownloader
from dream_dl.helper import make_curl
from dream_dl.dataclasses import *

def download(
        config: Config,
        webpage: Webpage,
        path: str,
        timeout: int = 600,
    ) -> None | Error:
    path = os.path.abspath(path)
    if os.path.exists(path):
        return Error(f"File {path} already exists")
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))

    config.options += ["--enable-logging", "--log-level=0"]
    config.capabilities |= {
        "goog:loggingPrefs" : {"performance": "ALL"}
    }

    downloader = DreamDownloader(config)
    print("Navigating to webpage: " + webpage.url)
    
    if not downloader.navigate(webpage):
        return Error("Failed to navigate to webpage")

    print("Navigated to webpage: " + webpage.url)

    logs = downloader.driver.get_log('performance')
    # for entry in logs:
    #     print(entry)

    mp4_urls = []
    m3u8_urls = []
    for entry in logs:
        try:
            message_obj = json.loads(entry.get("message"))
            message = message_obj.get("message", {})
            params = message.get("params", {})
            response = params.get("response", {})
            headers = response.get("headers", {})
            content_type = headers.get("Content-Type", "")
            url = response.get("url", "")
            if content_type == "video/mp4":
                mp4_urls.append(url)
            elif content_type == "application/vnd.apple.mpegurl":
                m3u8_urls.append(url)
        except Exception as e:
            pass
    
    if len(mp4_urls) > 0:
        video_url = mp4_urls[0]
        print("Downloading video from: " + video_url)
        os.system(make_curl(video_url, path))
    elif len(m3u8_urls) > 0:
        video_url = m3u8_urls[0]
        os.system(f"ffmpeg -i {video_url} -c copy {path}")
    else:
        return Error("Failed to find video url")
