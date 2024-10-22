# Local AI Note Taking App

This is a privacy-focused, command-line note-taking app that leverages Locaal's on-device AI for transcription and text processing. It allows you to transcribe desktop audio and capture microphone input, all while keeping your data secure and private on your local machine.

## Key Features

- **Local AI Processing**: Utilizes on-device AI models for transcription and text analysis, ensuring your data never leaves your computer.
- **Privacy-First**: All operations are performed locally, guaranteeing complete data privacy and security.
- **Cost-Effective**: No cloud services or subscriptions required - use advanced AI features for free.
- **Cross-Platform**: Supports Windows, macOS, and Linux.
- **Offline Capability**: Fully functional without an internet connection.

## How It Works

- **Audio Transcription**: Uses `faster_whisper`, a local implementation of OpenAI's Whisper model, for accurate speech-to-text conversion.
- **Text Processing**: Integrates `llama-cpp-python`, based on `ggerganiv/llama.cpp`, for advanced local language model capabilities.
- **Audio Capture**: Employs `sounddevice` for reliable microphone and desktop audio capture.

## Prerequisites

- Python 3.11 or higher
- Git

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/locaal-ai/note-taker.git
   cd note-taker
   ```

2. Install the dependencies:

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
src
|   app.py
|   main.py
|   main.tcss
|
+---audio
|       AudioCapture.py
|       textual_transcription_textarea.py
|       whisper_transcribe.py
|
+---llm
|       model.py
|
+---notes
|       manager.py
|
\---utils
        helpers.py
        resource_path.py
```

## Key Dependencies

- [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper): Local implementation of Whisper for speech recognition
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
