# ==========================================
# Code Generator Bot
# File Manager (v1.2)
# ==========================================

import os
import shutil


ALLOWED_EXTENSIONS = {
    # Images
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    # Web
    ".html",
    ".css",
    ".js",
    ".json",
    # Documents
    ".txt",
    ".md",
    # Fonts
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}


def is_allowed_file(filename):
    extension = os.path.splitext(filename)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def create_project_folders(project_path):
    folders = {
        "images": os.path.join(project_path, "images"),
        "assets": os.path.join(project_path, "assets"),
        "fonts": os.path.join(project_path, "fonts"),
    }
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    return folders


def save_file(project_path, filename, file_data, folder="assets"):
    if not is_allowed_file(filename):
        return {
            "success": False,
            "error": "نوع الملف غير مسموح.",
        }

    filename = os.path.basename(filename)
    target_folder = os.path.join(project_path, folder)
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, filename)

    try:
        with open(file_path, "wb") as file:
            file.write(file_data)
        return {
            "success": True,
            "filename": filename,
            "path": file_path,
        }
    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


def save_image(project_path, filename, image_data):
    return save_file(project_path, filename, image_data, folder="images")


def save_asset(project_path, filename, file_data):
    return save_file(project_path, filename, file_data, folder="assets")


def save_font(project_path, filename, font_data):
    return save_file(project_path, filename, font_data, folder="fonts")


def get_project_files(project_path):
    files = []
    if not os.path.exists(project_path):
        return files

    for root, _directories, filenames in os.walk(project_path):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, project_path)
            files.append(relative_path)

    return files


def get_project_size(project_path):
    total_size = 0
    if not os.path.exists(project_path):
        return 0

    for root, _directories, filenames in os.walk(project_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass

    return total_size


def delete_project(project_path):
    if not os.path.exists(project_path):
        return False
    try:
        shutil.rmtree(project_path)
        return True
    except Exception:
        return False
