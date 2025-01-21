import os

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_package_data_file(*paths: str) -> str:
    return os.path.join(PACKAGE_ROOT, *paths)
