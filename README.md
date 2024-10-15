# Note Taking App

This is a command line based note-taking app that allows you to transcribe desktop audio using the `pywhispercpp` library and capture audio from the microphone using the `sounddevice` library.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/note-taking-app.git
   ```

2. Install the dependencies listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Navigate to the `src` directory:

   ```bash
   cd src
   ```

2. Run the `main.py` file to start the note-taking app:

   ```bash
   python main.py
   ```

3. Follow the on-screen instructions to interact with the app. You can create, read, update, and delete notes using the provided commands.

## Project Structure

The project has the following structure:

```
note-taking-app
├── src
│   ├── main.py
│   ├── audio
│   │   ├── capture.py
│   │   └── transcribe.py
│   ├── notes
│   │   └── manager.py
│   └── utils
│       └── helpers.py
├── requirements.txt
├── setup.py
└── README.md
```

- `src/main.py`: Entry point of the application. Initializes the note-taking app and handles user interactions.
- `src/audio/capture.py`: Captures microphone audio using the `sounddevice` library.
- `src/audio/transcribe.py`: Transcribes captured audio using the `pywhispercpp` library.
- `src/notes/manager.py`: Provides methods for creating, reading, updating, and deleting notes. Interacts with the file system to store and retrieve note data.
- `src/utils/helpers.py`: Contains utility functions for various tasks.
- `requirements.txt`: Lists the project dependencies.
- `setup.py`: Used for packaging and distributing the project.
- `README.md`: Documentation for the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
```

This README file provides an overview of the note-taking app, instructions for installation and usage, project structure, and licensing information.