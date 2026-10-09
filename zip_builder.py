# ==========================================
# Code Generator Bot
# ZIP Builder (v1.2)
# ==========================================

import os
import zipfile
from datetime import datetime

from config import ZIPS_FOLDER


# ==========================================
# CREATE ZIP
# ==========================================

def create_zip(project_path, output_folder=None):
    """Create a ZIP archive of the project."""

    if not os.path.exists(project_path):
        return {
            "success": False,
            "error": "Project folder not found.",
        }

    if output_folder is None:
        output_folder = ZIPS_FOLDER

    os.makedirs(output_folder, exist_ok=True)

    project_name = os.path.basename(os.path.normpath(project_path))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{project_name}_{timestamp}.zip"
    zip_path = os.path.join(output_folder, zip_filename)

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _directories, files in os.walk(project_path):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(full_path, project_path)
                    # Skip any existing zip files inside the project
                    if relative_path.endswith(".zip"):
                        continue
                    zip_file.write(full_path, relative_path)

        return {
            "success": True,
            "path": zip_path,
            "filename": zip_filename,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


# ==========================================
# HELPERS
# ==========================================

def zip_exists(zip_path):
    return os.path.isfile(zip_path)


def get_zip_size(zip_path):
    if not zip_exists(zip_path):
        return 0
    try:
        return os.path.getsize(zip_path)
    except OSError:
        return 0


def format_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"
    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"
    return f"{size / (1024 ** 3):.2f} GB"


def get_zip_info(zip_path):
    if not zip_exists(zip_path):
        return None

    size = get_zip_size(zip_path)

    return {
        "filename": os.path.basename(zip_path),
        "path": zip_path,
        "size": size,
        "size_formatted": format_size(size),
    }
