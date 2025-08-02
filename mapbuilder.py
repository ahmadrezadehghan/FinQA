import os
from pathlib import Path

def print_tree(path: Path, prefix: str = ""):
    """
    Recursively prints a directory tree starting from the given path.

    :param path: pathlib.Path object pointing to a directory or file
    :param prefix: string prefix for tree structure formatting
    """
    if path.is_dir():
        print(f"{prefix}{path.name}/")
        # List children once to avoid multiple I/O operations
        children = list(path.iterdir())
        for index, child in enumerate(children):
            # Determine connectors
            is_last = index == len(children) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "
            # Recurse into directories, print files
            if child.is_dir():
                print_tree(child, prefix + connector)
            else:
                print(f"{prefix + connector}{child.name}")
    else:
        # If path is a file, just print its name
        print(f"{prefix}{path.name}")

if __name__ == '__main__':
    # Change this to your starting directory
    start_path = Path(r"C:\Users\AHMAD\Desktop\web_perper\training")
    if not start_path.exists():
        print(f"Error: Path '{start_path}' does not exist.")
    else:
        print_tree(start_path)
