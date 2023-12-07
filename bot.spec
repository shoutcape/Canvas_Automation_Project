# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/kauti/Documents/Canvas_Botti-Copy/bot.py'],
    pathex=['C:/Users/kauti/Documents/Canvas_Botti-Copy/virtualenv'],
    binaries=[],
    datas=[('C:/Users/kauti/Documents/Canvas_Botti-Copy/contents', 'contents/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\kauti\\Downloads\\favicon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='bot',
)
