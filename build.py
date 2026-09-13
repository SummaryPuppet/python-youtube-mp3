import os

from PyInstaller import __main__ as pyinstaller

RAIZ = os.path.dirname(os.path.abspath(__file__))

pyinstaller.run([
    "--onefile",
    "--windowed",
    "--name", "YouTube-MP3",
    "--noconfirm",
    "--clean",
    "--collect-all", "customtkinter",
    "--collect-submodules", "yt_dlp",
    os.path.join(RAIZ, "app_gui.py"),
])