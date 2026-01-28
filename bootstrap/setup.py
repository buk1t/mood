from setuptools import setup

APP = ["main.py"]

DATA_FILES = [
    ("web", ["../web/index.html", "../web/style.css", "../web/app.js"]),
    ("data", []),
    ("", ["../version.json"]),
]

OPTIONS = {
    "argv_emulation": False,
    "packages": ["webview", "bottle", "proxy_tools"],
    "includes": [
        "urllib",
        "urllib.request",
        "urllib.parse",
        "urllib.error",
        "ssl",
        "http.client",
    ],
    "excludes": ["pip", "setuptools", "pkg_resources", "wheel", "test", "unittest"],
    "plist": {
        "CFBundleName": "Mood",
        "CFBundleDisplayName": "Mood",
        "CFBundleIdentifier": "com.buk1t.mood",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
