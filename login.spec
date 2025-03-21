# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Jefferson\\Proyecto Contabilidad\\login.py'],
    pathex=[],
    binaries=[],
    datas=[('login.py', '.'), ('menu.py', '.'), ('partidas_contables.py', '.'), ('BalIco.png', '.'), ('BalsaIco.png', '.'), ('Config.png', '.'), ('EstaIco.png', '.'), ('LibMaIco.png', '.'), ('logo.png', '.'), ('ParCoIco.png', '.')],
    hiddenimports=[],
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
    name='login',
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
    icon=['D:\\Jefferson\\Proyecto Contabilidad\\icon.ico'],
)
