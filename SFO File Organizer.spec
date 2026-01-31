# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

import sys
import os

# Get the absolute path to the project directory (current directory)
project_dir = os.path.abspath(".")

datas = [('custom_rules.json', '.'), ('app_icon.ico', '.'), ('app_icon.png', '.')]
binaries = []
hiddenimports = ['app_config', 'organizer', 'history', 'rules', 'scheduler', 'watchdog']
# rules_ui is a single file, not a package, so we don't need collect_all



a = Analysis(
    ['gui.py', 'app_config.py', 'organizer.py', 'history.py', 'rules.py', 'scheduler.py'],
    pathex=[project_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SFO File Organizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon=['app_icon.ico'],
)
