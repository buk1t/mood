from setuptools import setup

APP = ["main.py"]
DATA_FILES = [("web", ["web/index.html", "web/style.css", "web/app.js"]),
              ("data", [])]

OPTIONS = {
    "argv_emulation": False,
    "packages": ["webview"],
    "includes": [],
    "plist": {
        "CFBundleName": "Mood Journal",
        "CFBundleDisplayName": "Mood Journal",
        "CFBundleIdentifier": "com.buk1t.moodjournal",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
