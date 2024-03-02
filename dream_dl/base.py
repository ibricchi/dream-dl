import time

from selenium import webdriver 
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as Service

from dream_dl.dataclasses import *

class DreamDownloader:
    config: Config
    driver: webdriver.Chrome
    def __init__(self, config: Config):
        self.config = config
        
        options = webdriver.ChromeOptions()
        for option in self.config.options:
            options.add_argument(option)
        for capability, value in self.config.capabilities.items():
            options.set_capability(capability, value)
        options.add_experimental_option("prefs", self.config.experimental_options)
        self.driver = webdriver.Chrome(service=Service(
            self.config.chrome_driver),
            options=options)
        
        stealth(self.driver, **self.config.stealth_options)

    def navigate(self, webpage: Webpage) -> bool:
        self.driver.get(webpage.url)
        if not self.driver:
            return False
        if webpage.local_storage_mod:
            commands = []
            for key, value in webpage.local_storage_mod.items():
                commands.append(f"localStorage.setItem('{key}', '{value}');")
            script = "\n".join(commands)
            self.driver.execute_script(script)
            self.driver.get(webpage.url)
        time.sleep(webpage.load_sleep)
        return True

