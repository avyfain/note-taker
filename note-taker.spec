# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

# parse command line arguments
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--mac_osx', action='store_true')
parser.add_argument('--win', action='store_true')
parser.add_argument('--debug', action='store_true')
parser.add_argument('--cuda', action='store_true')
parser.add_argument('--arch', type=str, choices=['x86_64', 'arm64', 'universal2'], help='Mac OSX: Specify the target architecture')

args = parser.parse_args()

note_taker_sources = [
    'src/app.py',
    'src/main.py',
    'src/settings_screen.py',
    'src/notes_editor_components.py',
    'src/audio/AudioCapture.py',
    'src/audio/textual_transcription_textarea.py',
    'src/audio/Transcriber.py',
    'src/llm/model.py',
    'src/notes/manager.py',
    'src/utils/helpers.py',
    'src/utils/resource_path.py'
    'src/utils/defaults.py'
    'src/utils/storage.py'
]

datas = [
    ('src/main.tcss', '.'),
    ('.env', '.'),
    ('data/ggml-small.en-q5_1.bin', 'data/')
]

if args.mac_osx:
    datas += [
        ('data/ggml-small.en-encoder.mlmodelc/weights/weight.bin', 'data/ggml-small.en-encoder.mlmodelc/weights/'),
        ('data/ggml-small.en-encoder.mlmodelc/metadata.json', 'data/ggml-small.en-encoder.mlmodelc/'),
        ('data/ggml-small.en-encoder.mlmodelc/model.mil', 'data/ggml-small.en-encoder.mlmodelc/'),
        ('data/ggml-small.en-encoder.mlmodelc/coremldata.bin', 'data/ggml-small.en-encoder.mlmodelc/'),
        ('data/ggml-small.en-encoder.mlmodelc/analytics/coremldata.bin', 'data/ggml-small.en-encoder.mlmodelc/analytics/'),
    ]

numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
llama_cpp_datas, llama_cpp_binaries, llama_cpp_hiddenimports = collect_all('llama_cpp')
whisper_datas, whisper_binaries, whisper_hiddenimports = collect_all('simpler-whisper')
ws_hiddenimports=['websockets', 'websockets.legacy']

a = Analysis(
    note_taker_sources,
    pathex=[],
    binaries=numpy_binaries + llama_cpp_binaries + whisper_binaries,
    datas=datas + numpy_datas + llama_cpp_datas + whisper_datas,
    hiddenimports=numpy_hiddenimports + ws_hiddenimports + llama_cpp_hiddenimports + whisper_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow',
        'torch',
        'torchvision',
        'torchaudio',
        'transformers',
        'diffusers',
        'PyQt6',
        'PySide6',
        'matplotlib',
        'tkinter',
        'nltk',
        'django',
        'av',
        'numpy.tests',
        'numpy.testing',
        'numpy.lib.tests',
        'numpy.doc'
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

if args.win:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='note-taker',
        debug=args.debug is not None and args.debug,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        windowed=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='note-taker',
    )
elif args.mac_osx:
    exe = EXE(
        pyz,
        a.binaries,
        a.datas,
        a.scripts,
        name='note-taker',
        debug=args.debug is not None and args.debug,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        windowed=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=args.arch if args.arch is not None else 'universal2',
        codesign_identity=os.environ.get('APPLE_APP_DEVELOPER_ID', ''),
        entitlements_file='./entitlements.plist',
    )
#    app = BUNDLE(
#        exe,
#        name='note-taker.app',
#        bundle_identifier='ai.locaal.note-taker',
#        version='0.0.1',
#        info_plist={
#            'NSPrincipalClass': 'NSApplication',
#            'NSAppleScriptEnabled': False,
#            'NSCameraUsageDescription': 'Getting images from the camera to perform OCR',
#            'NSMicrophoneUsageDescription': 'Record the microphone for speech recognition',
#        }
#    )
else:
    exe = EXE(
        pyz,
        a.binaries,
        a.datas,
        a.scripts,
        name='note-taker',
        debug=args.debug is not None and args.debug,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
    )
