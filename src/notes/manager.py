import os
import json
import uuid
import platformdirs


class NoteManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NoteManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, notes_directory=None):
        if hasattr(self, "_initialized") and self._initialized:
            return
        if notes_directory is None:
            notes_directory = platformdirs.user_data_dir("notes", "NoteTakingApp")
        if not os.path.exists(notes_directory):
            os.makedirs(notes_directory)
        self.notes_directory = notes_directory
        self.json_file = os.path.join(self.notes_directory, "notes.json")
        self.selected_note: dict | None = None
        self._initialized = True
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
        self.notes[note_uuid] = {"uuid": note_uuid, "title": title, "path": note_path}
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

    def update_note_content(self, uuid, new_content):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        note_path = self.notes[uuid]["path"]
        with open(note_path, "w") as file:
            file.write(new_content)

    def delete_note(self, uuid):
        if uuid not in self.notes:
            raise KeyError("Note not found")
        note_path = self.notes[uuid]["path"]
        if os.path.exists(note_path):
            os.remove(note_path)
        del self.notes[uuid]
        self._save_json_store()

    def delete_note_by_index(self, index: int):
        note_uuids = list(self.notes.keys())
        if 0 <= index < len(note_uuids):
            self.delete_note(note_uuids[index])
        else:
            raise IndexError("Index out of range")

    def list_notes(self):
        return list(self.notes.values())
