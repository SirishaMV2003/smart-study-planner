"""Database utilities for SQLite management"""
import sqlite3
import json
from datetime import datetime


def get_db_connection(db_path):
    """Get database connection"""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path):
    """Initialize database tables"""
    connection = get_db_connection(db_path)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timetable_file TEXT,
            syllabus_file TEXT,
            uploaded_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            subject_name TEXT,
            difficulty TEXT,
            topics TEXT,
            FOREIGN KEY(plan_id) REFERENCES study_plans(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            subject_name TEXT,
            exam_date TEXT,
            FOREIGN KEY(plan_id) REFERENCES study_plans(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            generated_at TEXT,
            subjects_data TEXT,
            exam_data TEXT,
            plan_entries TEXT,
            summary_data TEXT,
            progress_percent INTEGER,
            streak_days INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            completed_tasks INTEGER,
            total_tasks INTEGER,
            progress_percent INTEGER,
            updated_at TEXT,
            FOREIGN KEY(plan_id) REFERENCES study_plans(id)
        )
    ''')

    connection.commit()
    connection.close()


def record_upload(db_path, timetable_file, syllabus_file):
    """Record file upload"""
    connection = get_db_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO uploads (timetable_file, syllabus_file, uploaded_at) VALUES (?, ?, ?)',
        (timetable_file, syllabus_file, datetime.now().isoformat())
    )
    connection.commit()
    connection.close()


def save_study_plan(db_path, student_name, exam_data, subjects_data, plan_entries, summary_data):
    """Save study plan to database"""
    connection = get_db_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO study_plans (student_name, generated_at, exam_data, subjects_data, plan_entries, summary_data, progress_percent) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (student_name, datetime.now().isoformat(), exam_data, subjects_data, plan_entries, summary_data, 0)
    )
    connection.commit()
    plan_id = cursor.lastrowid
    connection.close()
    return plan_id


def get_plan(db_path, plan_id):
    """Retrieve study plan"""
    connection = get_db_connection(db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM study_plans WHERE id = ?', (plan_id,))
    plan = cursor.fetchone()
    connection.close()
    return dict(plan) if plan else None


def save_progress(db_path, plan_id, completed_tasks, total_tasks, progress_percent):
    """Save progress update"""
    connection = get_db_connection(db_path)
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM progress WHERE plan_id = ?',
        (plan_id,)
    )
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            'UPDATE progress SET completed_tasks = ?, total_tasks = ?, progress_percent = ?, updated_at = ? WHERE plan_id = ?',
            (completed_tasks, total_tasks, progress_percent, datetime.now().isoformat(), plan_id)
        )
    else:
        cursor.execute(
            'INSERT INTO progress (plan_id, completed_tasks, total_tasks, progress_percent, updated_at) VALUES (?, ?, ?, ?, ?)',
            (plan_id, completed_tasks, total_tasks, progress_percent, datetime.now().isoformat())
        )
    
    connection.commit()
    connection.close()


def get_progress(db_path, plan_id):
    """Get progress for a plan"""
    connection = get_db_connection(db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM progress WHERE plan_id = ?', (plan_id,))
    progress = cursor.fetchone()
    connection.close()
    return dict(progress) if progress else {'completed_tasks': 0, 'total_tasks': 0, 'progress_percent': 0}
