from typing import Any
from dataclasses import dataclass, field

@dataclass(kw_only=True)
class Config:
    chrome_driver: str = "/usr/bin/chromedriver"
    options: list[str] = field(default_factory=lambda: [
        "--headless",
        "--disable-web-security",
    ])
    capabilities: dict[str, Any] = field(default_factory=dict)
    experimental_options: dict[str, Any] = field(default_factory=dict)
    stealth_options: dict[str, Any] = field(default_factory=lambda: {
        "languages": ["en-US", "en"],
        "vendor": "Google Inc.",
        "platform": "Win32",
        "webgl_vendor": "Intel Inc.",
        "renderer": "Intel Iris OpenGL Engine",
        "fix_hairline": True,
    })

@dataclass(kw_only=True)
class Webpage:
    url: str
    local_storage_mod: dict[str, str] | None = None
    load_sleep: int = 5
    timeout: int = 600

# create a result object with type hinting
@dataclass
class Error:
    msg: str

    def __init__(self, msg: str):
        self.msg = msg
