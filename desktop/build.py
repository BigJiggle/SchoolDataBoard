"""Builds the SchoolBoard desktop app for the computer it runs on, checks it starts, and zips it for sharing.

    pip install -r requirements.txt -r requirements-desktop.txt
    python desktop/build.py

Output (in dist/):
    macOS    SchoolBoard.app      + SchoolBoard-macOS-<arch>.zip
    Windows  SchoolBoard.exe      + SchoolBoard-Windows.zip
    Linux    SchoolBoard/         + SchoolBoard-Linux.tar.gz
"""

import os
import platform
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESKTOP = os.path.join(ROOT, "desktop")
DIST = os.path.join(ROOT, "dist")


def run(cmd: list[str], **kw):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT, **kw)


def build() -> str:
    sep = ";" if os.name == "nt" else ":"
    args = [
        sys.executable, "-m", "PyInstaller", "desktop.py", "--name", "SchoolBoard", "--noconfirm", "--clean", "--windowed",
        "--add-data", f"app/static{sep}app/static",
        "--collect-submodules", "uvicorn",
        "--collect-data", "tzdata",        # Windows has no time-zone database of its own
        "--collect-data", "certifi",       # HTTPS to Canvas/Schoology/Claude from the packaged app
        "--exclude-module", "tkinter", "--exclude-module", "pytest",
    ]
    if sys.platform == "darwin":
        args += ["--icon", "desktop/icon.icns", "--osx-bundle-identifier", "app.schoolboard.desktop"]
        target = os.path.join(DIST, "SchoolBoard.app")
    elif os.name == "nt":
        args += ["--icon", "desktop/icon.ico", "--onefile"]
        target = os.path.join(DIST, "SchoolBoard.exe")
    else:
        args += ["--icon", "desktop/icon.png"]
        target = os.path.join(DIST, "SchoolBoard")
    run(args)
    return target


def executable(target: str) -> str:
    if target.endswith(".app"):
        return os.path.join(target, "Contents", "MacOS", "SchoolBoard")
    if target.endswith(".exe"):
        return target
    return os.path.join(target, "SchoolBoard")


def package(target: str) -> str:
    if sys.platform == "darwin":
        arch = "arm64" if platform.machine() == "arm64" else "intel"
        out = os.path.join(DIST, f"SchoolBoard-macOS-{arch}.zip")
        # ditto keeps the bundle's symlinks and permissions intact (a plain zip breaks .app bundles).
        run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", target, out])
        return out
    if os.name == "nt":
        out = os.path.join(DIST, "SchoolBoard-Windows")
        return shutil.make_archive(out, "zip", DIST, "SchoolBoard.exe")
    out = os.path.join(DIST, "SchoolBoard-Linux")
    return shutil.make_archive(out, "gztar", DIST, "SchoolBoard")


if __name__ == "__main__":
    target = build()
    run([executable(target), "--selftest"], timeout=180)
    print("built", package(target))
