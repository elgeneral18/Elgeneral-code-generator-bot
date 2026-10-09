# ==========================================
# Code Generator Bot
# Database (v1.2)
# ==========================================

import sqlite3
from datetime import datetime

from config import DATABASE_NAME


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            project_type TEXT,
            project_name TEXT,
            project_path TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# USERS
# ==========================================

def user_exists(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user_id,),
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None


def add_user(user_id, username, first_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, joined_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            username,
            first_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()


def get_user(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, username, first_name, joined_at
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    )

    user = cursor.fetchone()
    conn.close()

    return user


def get_users_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()

    return count


# ==========================================
# PROJECTS
# ==========================================

def add_project(user_id, project_type, project_name, project_path):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO projects
        (user_id, project_type, project_name, project_path, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            project_type,
            project_name,
            project_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    project_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return project_id


def update_project_name(project_path, project_name):
    """Update project name after AI generation succeeds."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE projects
        SET project_name = ?
        WHERE project_path = ?
        """,
        (project_name, project_path),
    )

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    return affected > 0


def get_user_projects(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, project_type, project_name, project_path, created_at
        FROM projects
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )

    projects = cursor.fetchall()
    conn.close()

    return projects


def get_projects_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM projects")
    count = cursor.fetchone()[0]
    conn.close()

    return count
