# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file dla PDF Converter GUI
Wygenerowano: 2025-11-05
"""

block_cipher = None

a = Analysis(
    ['pdf_converter_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pdfplumber',
        'pdfminer',
        'pdfminer.six',
        'pandas',
        'openpyxl',
        'PIL',
        'PIL.Image',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        'codecs',
        'io',
        'threading',
        'charset_normalizer',
        'pypdfium2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.tests',
        'pandas.tests',
        'scipy',
        'pytest',
    ],
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
    name='PDF_Converter_Millennium_CHF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Wyłącz konsolę dla aplikacji GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Możesz dodać ikonę: icon='icon.ico'
)
