# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['run.py'],
    pathex=['E:\myWork\SaaSOpTool\venv\Lib\site-packages'],
    binaries=[],
	datas=[('E:\myWork\SaaSOpTool\\venv\Lib\site-packages\onnxruntime\capi\onnxruntime_providers_shared.dll','onnxruntime\capi'), 
	('E:\myWork\SaaSOpTool\\venv\Lib\site-packages\ddddocr\common.onnx','ddddocr'), 
	('E:\myWork\SaaSOpTool\\venv\Lib\site-packages\ddddocr\common_old.onnx','ddddocr')],
    hiddenimports=['PySide2.QtXml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
