import json
import os
from platformdirs import user_data_dir


data_subscribers = {}


def get_data_dir():
    # Get the user data directory
    return user_data_dir("notes", "NoteTakingApp", ensure_exists=True)


def subscribe_to_data(file_path: str, document_name: str, callback: callable):
    # Subscribe to data changes in a JSON file
    # prepend the user data directory
    file_path = os.path.join(get_data_dir(), file_path)

    if file_path not in data_subscribers:
        data_subscribers[file_path] = {}
    if document_name not in data_subscribers[file_path]:
        data_subscribers[file_path][document_name] = []
    data_subscribers[file_path][document_name].append(callback)


def store_data(file_path, document_name, data):
    # Store data into a JSON file
    # get the user data directory
    data_dir = get_data_dir()

    # prepend the user data directory
    file_path = os.path.join(data_dir, file_path)

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                documents = json.load(f)
            except json.JSONDecodeError:
                documents = {}
    else:
        documents = {}

    documents[document_name] = data

    with open(file_path, "w") as f:
        json.dump(documents, f, indent=2)

    # notify subscribers
    if file_path in data_subscribers and document_name in data_subscribers[file_path]:
        for callback in data_subscribers[file_path][document_name]:
            callback(data)


def remove_data(file_path, document_name):
    # Remove data from a JSON file
    # prepend the user data directory
    file_path = os.path.join(get_data_dir(), file_path)

    if not os.path.exists(file_path):
        return

    with open(file_path, "r") as f:
        documents = json.load(f)

    if document_name in documents:
        del documents[document_name]

    # notify subscribers
    if file_path in data_subscribers and document_name in data_subscribers[file_path]:
        for callback in data_subscribers[file_path][document_name]:
            callback(None)

    with open(file_path, "w") as f:
        json.dump(documents, f, indent=2)


def fetch_data(file_path, document_name, default=None):
    # Fetch data from a JSON file
    # prepend the user data directory
    file_path = os.path.join(get_data_dir(), file_path)

    if not os.path.exists(file_path):
        return default

    with open(file_path, "r") as f:
        try:
            documents = json.load(f)
        except json.JSONDecodeError:
            return default

    if document_name in documents:
        return documents[document_name]
    else:
        return default
