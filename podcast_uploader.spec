# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Hardcoded script directory
script_dir = r'e:/Projects/Programming-projects/Work-in-Progress/Notebooklm-podcast-episode-uploader'
credentials_path = os.path.join(script_dir, 'credentials.json')

a = Analysis(
    [os.path.join(script_dir, 'wav_to_mp3_converter.py')],
    pathex=[script_dir],
    binaries=[],
    datas=[(credentials_path, '.')],
    hiddenimports=[
        'google.auth.transport.requests',
        'google_auth_oauthlib.flow',
        'google.oauth2.credentials',
        'googleapiclient.discovery',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Podcast Episode Uploader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Changed to False for windowed application
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Podcast Episode Uploader'
)
