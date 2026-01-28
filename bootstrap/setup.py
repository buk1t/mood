# bootstrap/setup.py
from setuptools import setup

APP = ["main.py"]

OPTIONS = {
    "argv_emulation": False,
    "packages": ["webview"],
    "includes": [],
    "plist": {
        "CFBundleName": "mood",
        "CFBundleDisplayName": "mood",
        "CFBundleIdentifier": "com.buk1t.mood",
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
