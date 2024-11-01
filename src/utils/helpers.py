import os
import platform
import subprocess


def create_directory(directory):
    """
    Creates a directory if it doesn't exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def read_file(file_path):
    """
    Reads the contents of a file and returns them as a string.
    """
    with open(file_path, "r") as file:
        return file.read()


def write_file(file_path, content):
    """
    Writes the given content to a file.
    """
    with open(file_path, "w") as file:
        file.write(content)


def delete_file(file_path):
    """
    Deletes a file if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def open_folder_with_finder(path):
    """
    Opens the given folder in Finder (macOS specific).
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows
        os.startfile(path)
    elif system == "darwin":
        # macOS
        subprocess.Popen(["open", path])
    else:
        # Linux/Unix
        subprocess.Popen(["xdg-open", path])
