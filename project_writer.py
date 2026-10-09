# ==========================================
# Code Generator Bot
# Project Writer (v1.2)
# ==========================================

import os


def write_project(project_path, files):
    """Write AI-generated files into the project folder safely."""

    created_files = []

    try:
        os.makedirs(project_path, exist_ok=True)

        for file_data in files:
            relative_path = file_data.get("path", "")
            content = file_data.get("content")

            if not relative_path or content is None:
                continue

            # Normalize and block path traversal
            relative_path = os.path.normpath(relative_path)

            if (
                relative_path.startswith("..")
                or os.path.isabs(relative_path)
                or relative_path.startswith("/")
            ):
                continue

            full_path = os.path.join(project_path, relative_path)
            parent_folder = os.path.dirname(full_path)

            if parent_folder:
                os.makedirs(parent_folder, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as file:
                file.write(content)

            created_files.append(relative_path)

        if not created_files:
            return {
                "success": False,
                "error": "No valid files were written.",
                "files": [],
            }

        return {
            "success": True,
            "files": created_files,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
            "files": created_files,
        }
