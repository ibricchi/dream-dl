from enum import Enum
import time
import os

from dream_dl.base import DreamDownloader
from dream_dl.helper import make_curl
from dream_dl.dataclasses import *

class DownloadMode(Enum):
    JS_INJECTION = 0
    CURL = 1
DM = DownloadMode

def download(
        config: Config,
        webpage: Webpage,
        path: str,
        modes: list[DM] = [DM.CURL, DM.JS_INJECTION],
        timeout: int = 600,
    ) -> None | Error:
    path = os.path.abspath(path)
    if os.path.exists(path):
        return Error(f"File {path} already exists")
    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))

    if len(modes) == 0:
        return Error("No download modes specified")
    
    config.experimental_options |= {
        "download.default_directory": os.path.dirname(path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }

    downloader = DreamDownloader(config)
    if not downloader.navigate(webpage):
        return Error("Failed to navigate to webpage")

    def find_vid_recursive():
        # check if video tag exists
        videos = downloader.driver.find_elements('tag name', 'video')
        if len(videos) > 0:
            # todo maybe we could do something smart here
            return videos[0].get_attribute("src")
        for iframe in downloader.driver.find_elements('tag name', 'iframe'):
            downloader.driver.switch_to.frame(iframe)
            video = find_vid_recursive()
            if video:
                return video
            downloader.driver.switch_to.parent_frame()
        return None
    if not (video_src := find_vid_recursive()):
        return Error("Failed to find a video tag")
    
    errors = []

    for mode in modes:
        if mode == DM.JS_INJECTION:
            downloader.driver.execute_script("""
            function downloadImage() {{
                console.log('Download started...');
                var xhr = new XMLHttpRequest();
                xhr.open(
                    'GET',
                    '{0}',
                    true
                );
                xhr.responseType = 'blob';
                xhr.onload = function() {{
                    console.log("Download completed")
                    var urlCreator = window.URL || window.webkitURL;
                    var imageUrl = urlCreator.createObjectURL(this.response);
                    var tag = document.createElement('a');
                    tag.href = imageUrl;
                    tag.target = '_blank';
                    tag.download = '{1}';
                    document.body.appendChild(tag);
                    tag.click();
                    document.body.removeChild(tag);
                }};
                xhr.onerror = err => {{
                    console.log('Download Failed');
                    alert('Failed to download picture');
                }};
                console.log("Sending request")
                xhr.send();
            }}
            downloadImage();
            """.format(
                video_src,
                os.path.basename(path),
            ))
            start_time = time.time()
            timedout = False
            while not os.path.exists(path) and not os.path.exists(path + ".crdownload"):
                if time.time() - start_time > timeout:
                    timedout = True
                    break
                time.sleep(1)
            while os.path.exists(path + ".crdownload"):
                if time.time() - start_time > timeout:
                    timedout = True
                    break
                time.sleep(1)
            if not timedout:
                downloader.driver.quit()
                return None
            errors.append("JSInjection: Download timed out")
        elif mode == DM.CURL:
            retval = os.system(make_curl(video_src, path))
            if retval == 0:
                downloader.driver.quit()
                return None
            errors.append("CURL: Download failed")
        else:
            return Error(f"Invalid download mode {mode}")
    return Error("\n".join(errors))
