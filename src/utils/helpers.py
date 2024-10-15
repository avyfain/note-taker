import os

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
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    """
    Writes the given content to a file.
    """
    with open(file_path, 'w') as file:
        file.write(content)

def delete_file(file_path):
    """
    Deletes a file if it exists.
    """
    if os.path.exists(file_path):
        os.remove(file_path)