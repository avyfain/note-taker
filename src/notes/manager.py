import os
import json
import uuid
import platformdirs
from utils.storage import fetch_data, subscribe_to_data
from utils.defaults import default_storage_folder


class NoteManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NoteManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.notes_directory = None
        self.get_notes_directory()
        self.selected_note: dict | None = None
        self._initialized = True
        self._load_json_store()

    def get_notes_directory(self):
        """
        Retrieves the directory path where notes are stored. If the directory does not exist, it is created.

        Returns:
            str: The path to the notes directory.
        """
        if self.notes_directory is None:
            self.notes_directory = fetch_data(
                "settings.json", "storage_folder", default_storage_folder
            )
            subscribe_to_data(
                "settings.json", "storage_folder", self.set_notes_directory
            )
        if not os.path.exists(self.notes_directory):
            os.makedirs(self.notes_directory)
        self.json_file = os.path.join(self.notes_directory, "notes.json")
        return self.notes_directory

    def set_notes_directory(self, new_notes_directory):
        self.notes_directory = new_notes_directory
        if not os.path.exists(self.notes_directory):
            os.makedirs(self.notes_directory)
        self.json_file = os.path.join(self.notes_directory, "notes.json")
        self._load_json_store()

    def _load_json_store(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as f:
                self.notes = json.load(f)
        else:
            self.notes = {}

    def _save_json_store(self):
        with open(self.json_file, "w") as f:
            json.dump(self.notes, f, indent=2)

    def select_note_by_uuid(self, uuid):
        if uuid in self.notes:
            self.selected_note = self.notes[uuid]
        else:
            raise KeyError("Note not found")

    def select_note_by_index(self, index: int):
        note_uuids = list(self.notes.keys())
        if 0 <= index < len(note_uuids):
            self.selected_note = self.notes[note_uuids[index]]
        else:
            raise IndexError("Index out of range")

    def get_note_path_from_uuid(self, uuid):
        return os.path.join(self.notes_directory, f"{uuid}.txt")

    def create_note(self, title, content) -> str:
        note_uuid = str(uuid.uuid4())
        note_path = self.get_note_path_from_uuid(note_uuid)
        with open(note_path, "w") as file:
            file.write(content)
        self.notes[note_uuid] = {
            "uuid": note_uuid,
            "title": title,
            "path": note_path,
            "created_at": os.path.getmtime(note_path),
            "updated_at": os.path.getmtime(note_path),
        }
        self._save_json_store()
        return note_uuid

    def read_note(self, uuid):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        note_path = self.notes[uuid]["path"]
        with open(note_path, "r") as file:
            return file.read()

    def update_note_title(self, uuid, new_title):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        self.notes[uuid]["title"] = new_title
        self._save_json_store()
        self.notes[uuid]["updated_at"] = os.path.getmtime(self.notes[uuid]["path"])

    def update_note_content(self, uuid, new_content):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        note_path = self.notes[uuid]["path"]
        with open(note_path, "w") as file:
            file.write(new_content)
        self.notes[uuid]["updated_at"] = os.path.getmtime(note_path)

    def update_note_transcription(self, uuid: str, new_transcription: str):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        # create a new file with the transcription with "_transcription" appended to the uuid
        transcription_path = os.path.join(
            self.notes_directory, f"{uuid}_transcription.txt"
        )
        with open(transcription_path, "w") as file:
            file.write(new_transcription)
        self.notes[uuid]["updated_at"] = os.path.getmtime(transcription_path)

    def delete_note(self, uuid: str):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        note_path = self.notes[uuid]["path"]
        if os.path.exists(note_path):
            os.remove(note_path)
        transcription_path = os.path.join(
            self.notes_directory, f"{uuid}_transcription.txt"
        )
        if os.path.exists(transcription_path):
            os.remove(transcription_path)
        del self.notes[uuid]
        self._save_json_store()

    def list_notes(self, sort_by_date=False):
        notes_list = list(self.notes.values())
        if sort_by_date:
            notes_list.sort(
                key=lambda x: (
                    x["updated_at"]
                    if "updated_at" in x
                    else x["created_at"] if "created_at" in x else 0
                ),
                reverse=True,
            )
        return notes_list
