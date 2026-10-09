# ==========================================
# Code Generator Bot
# Project Generator / Session Manager (v1.2)
# ==========================================

import os
import uuid

from config import PROJECTS_FOLDER


# ==========================================
# ACTIVE SESSIONS (in-memory)
# ==========================================

user_sessions = {}


# ==========================================
# PROJECT FOLDER
# ==========================================

def create_project(user_id, project_type):

    user_folder = os.path.join(PROJECTS_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    project_id = uuid.uuid4().hex[:8]
    project_folder = os.path.join(user_folder, project_id)
    os.makedirs(project_folder, exist_ok=True)

    images_folder = os.path.join(project_folder, "images")
    assets_folder = os.path.join(project_folder, "assets")
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(assets_folder, exist_ok=True)

    return {
        "project_id": project_id,
        "project_type": project_type,
        "project_folder": project_folder,
        "images_folder": images_folder,
        "assets_folder": assets_folder,
    }


# ==========================================
# START PROJECT
# ==========================================

def start_project(user_id, project_type):

    project = create_project(user_id, project_type)

    user_sessions[user_id] = {
        "project_id": project["project_id"],
        "project_type": project["project_type"],
        "project_folder": project["project_folder"],
        "images_folder": project["images_folder"],
        "assets_folder": project["assets_folder"],
        "step": "idea",
        "idea": "",
        "images": [],
        "files": [],
    }

    return user_sessions[user_id]


# ==========================================
# SESSION HELPERS
# ==========================================

def get_session(user_id):
    return user_sessions.get(user_id)


def save_idea(user_id, idea):
    session = get_session(user_id)
    if not session:
        return False
    session["idea"] = idea
    session["step"] = "images"
    return True


def add_image(user_id, filename):
    session = get_session(user_id)
    if not session:
        return False
    session["images"].append(filename)
    return True


def get_images(user_id):
    session = get_session(user_id)
    if not session:
        return []
    return session["images"]


def finish_images(user_id):
    session = get_session(user_id)
    if not session:
        return False
    session["step"] = "generating"
    return True


def generation_complete(user_id):
    session = get_session(user_id)
    if not session:
        return False
    session["step"] = "completed"
    return True


def get_project_path(user_id):
    session = get_session(user_id)
    if not session:
        return None
    return session["project_folder"]


def get_project_id(user_id):
    session = get_session(user_id)
    if not session:
        return None
    return session["project_id"]


def get_project_type(user_id):
    session = get_session(user_id)
    if not session:
        return None
    return session["project_type"]


def get_project_idea(user_id):
    session = get_session(user_id)
    if not session:
        return None
    return session["idea"]


def end_project(user_id):
    if user_id in user_sessions:
        del user_sessions[user_id]
        return True
    return False
