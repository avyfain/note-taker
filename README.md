# Note Taker - Privacy focused AI note taking app, that runs on-device

Privacy-focused, command-line note-taking app that uses Locaal's on-device AI SDK for transcription and summarization. Transcribe meetings and generate concise summaries, all locally. Free, open-source, and built for developers. 

## Features

- **Private**: Data stays on your device. No servers or third-party access, ensuring complete privacy.
- **Real-Time**: Transcribe in 99+ languages.
- **Smart**: AI-generated summaries with customizable templates.
- **Portable**: No data lock-in. Your notes are saved as markdown files either locally or on your favorite cloud storage provider.
- **Works Offline**: No internet connection required.
- **Non-Intrusive**: Runs in the background. No bots joining your calls.
- **Customizable**: Choose AI models and summary templates.
- **Cross-Platform**: Supports Windows, macOS, Linux.
- **Cost-Effective**: No server or usage fees.

## How It Works

- Built leveraging Locaal's on-device AI SDK:
  - **Transcription**: Uses Locaal's [simpler-whisper](https://github.com/locaal-ai/simpler-whisper/), a multi-threaded local implementation of OpenAI's Whisper model.
  - **Summarization**: Integrates [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for local language model capabilities.
  - **Audio Capture**: Uses [sounddevice](https://python-sounddevice.readthedocs.io/) for microphone and desktop audio capture.

## Prerequisites

- Python 3.11 or higher
- Git

## Installation

1. Install a pre-built version from the [Releases](https://github.com/locaal-ai/note-taker/releases) page, including an installer for windows or a simple standalone app for Mac.

1. Clone the repository:

   ```bash
   git clone https://github.com/locaal-ai/note-taker.git
   cd note-taker
   ```

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Navigate to the `src` directory:

   ```bash
   cd src
   ```

2. Run the main script:

   ```bash
   python main.py
   ```

3. Follow the on-screen prompts to:
   - Transcribe audio from your microphone or desktop
   - Create, read, update, and delete notes
   - Use AI-powered features for text analysis and summarization

## Privacy and Security

- All AI processing occurs on your local device, ensuring your data never leaves your control.
- No internet connection is required for core functionalities.
- Your notes and transcriptions are stored locally in an encrypted format.

## Building from Source

This project uses PyInstaller to create standalone executables for Windows, macOS, and Linux. The build process is automated using GitHub Actions, but you can also build the app locally.

### Prerequisites

- Python 3.11
- PyInstaller 6.10.0
- Platform-specific dependencies (see below)

### Windows

1. Install `simpler-whisper` (https://github.com/locaal-ai/simpler-whisper) prebuilt wheel and `llama-cpp-python`

    ```powershell
    Invoke-WebRequest -Uri https://github.com/locaal-ai/simpler-whisper/releases/download/0.1.0/simpler_whisper-0.1.0-cp311-cp311-cuda-win64-win_amd64.whl -OutFile simpler_whisper-0.1.0-cp311-cp311-win_amd64.whl
    pip install simpler_whisper-0.1.0-cp311-cp311-win_amd64.whl
    rm simpler_whisper-0.1.0-cp311-cp311-win_amd64.whl
    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu125
    ```

1. Install other dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

1. Download the whisper model:

    ```powershell
    mkdir data
    Invoke-WebRequest -Uri https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-q5_1.bin?download=true -OutFile data/ggml-small.en-q5_1.bin
    ```

1. For CPU version:
   ```powershell
   pyinstaller --clean --noconfirm note-taker.spec -- --win
   ```

   For CUDA version:
   ```powershell
   pyinstaller --clean --noconfirm note-taker.spec -- --win --cuda
   ```

1. The executable will be in the `dist` folder.

1. To create an installer:
   - Ensure Inno Setup is installed
   - Run: `iscc note-taker.iss`

### macOS

1. Install dependencies:
   ```
   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal
   pip install -r requirements.txt
   ```

1. Download the models:

   ```bash
   mkdir -p data/
   wget -P data/ "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-q5_1.bin?download=true" -O data/ggml-small.en-q5_1.bin
   curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-encoder.mlmodelc.zip?download=true -o data/ggml-small.en-encoder.mlmodelc.zip
   unzip data/ggml-small.en-encoder.mlmodelc.zip -d data
   rm data/ggml-small.en-encoder.mlmodelc.zip
   ```

1. Build the app:
   ```
   pyinstaller --clean --noconfirm note-taker.spec -- --mac_osx
   ```

1. The app bundle will be in the `dist` folder.

1. To create a DMG:
   ```
   hdiutil create -volname "note-taker" -srcfolder dist/note-taker.app -ov -format UDRO note-taker-macos.dmg
   ```

### Linux

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

1. Download the model:

   ```bash
   wget -P data/ "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-q5_1.bin?download=true" -O data/ggml-small.en-q5_1.bin
   ```

1. Build the app:
   ```
   pyinstaller --clean --noconfirm note-taker.spec
   ```

1. The executable will be in the `dist` folder.

1. To create a tarball:
   ```
   tar -cvf note-taker.tar -C dist note-taker
   ```

### CI/CD Builds

Our GitHub Actions workflow (`build.yaml`) automates builds for multiple platforms:

- Windows: CPU and CUDA versions
- macOS: x86 and ARM64 versions
- Linux: x86_64 version

The workflow handles dependency installation, building, and packaging for each platform. For macOS, it also includes code signing and notarization steps.

## Running the Built Application

### Windows
Run the `note-taker.exe` file in the `dist` folder, or use the installer created by Inno Setup.

### macOS
Open the `note-taker.app` bundle in the `dist` folder, or mount the created DMG and drag the app to your Applications folder.

### Linux
Run the `note-taker` executable in the `dist` folder.

### CI/CD

Our GitHub Actions workflow (`build.yaml`) automates builds for multiple platforms, ensuring the app is always ready for distribution with the latest local AI capabilities.

## Project Structure

```
src/
├── app.py
├── audio
│   ├── AudioCapture.py
│   ├── Transcriber.py
│   └── textual_transcription_textarea.py
├── llm
│   └── model.py
├── main.py
├── main.tcss
├── notes
│   └── manager.py
├── notes_editor_components.py
├── settings_screen.py
├── template_select_modal.py
└── utils
    ├── defaults.py
    ├── helpers.py
    ├── resource_path.py
    └── storage.py
```

## Key Dependencies

- [`simpler-whisper`](https://github.com/locaal-ai/simpler-whisper): Local implementation of Whisper for speech recognition
- [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python): Python bindings for the llama.cpp library
- [`sounddevice`](https://github.com/spatialaudio/python-sounddevice): For audio capture
- [`textual`](https://github.com/Textualize/textual): TUI (Text User Interface) framework

For a complete list, see `requirements.txt`.

## Contributing

We welcome contributions that enhance the app's local AI capabilities, improve privacy features, or optimize performance. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

While this app processes all data locally, users are responsible for ensuring compliance with local laws and regulations regarding data privacy and AI usage.
