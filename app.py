import os
import json
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from utils import db_utils
from ocr.ocr_utils_new import parse_timetable_file, parse_syllabus_file
from study_plans.plan_generator_v2 import generate_study_plan_v2, build_summary_v2
from utils.pdf_utils import create_study_plan_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PDF_FOLDER = os.path.join(BASE_DIR, 'generated_pdfs')
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'smart-study-planner-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PDF_FOLDER'] = PDF_FOLDER

# Ensure required folders exist
for folder in [UPLOAD_FOLDER, PDF_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Initialize database tables and connection
db_utils.init_db(DATABASE_PATH)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('landing.html', active_page='home')


@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        student_name = request.form.get('student_name', 'Smart Student').strip() or 'Smart Student'
        timetable = request.files.get('timetable')
        syllabus = request.files.get('syllabus')

        if not timetable or not allowed_file(timetable.filename):
            flash('Please upload a valid exam timetable image or PDF file.', 'error')
            return redirect(url_for('upload_page'))

        if not syllabus or not allowed_file(syllabus.filename):
            flash('Please upload a valid syllabus image or PDF file.', 'error')
            return redirect(url_for('upload_page'))

        timetable_name = secure_filename(f"timetable_{datetime.now().strftime('%Y%m%d%H%M%S')}_{timetable.filename}")
        syllabus_name = secure_filename(f"syllabus_{datetime.now().strftime('%Y%m%d%H%M%S')}_{syllabus.filename}")
        timetable_path = os.path.join(app.config['UPLOAD_FOLDER'], timetable_name)
        syllabus_path = os.path.join(app.config['UPLOAD_FOLDER'], syllabus_name)

        timetable.save(timetable_path)
        syllabus.save(syllabus_path)

        db_utils.record_upload(DATABASE_PATH, timetable_name, syllabus_name)

        try:
            exam_items = parse_timetable_file(timetable_path)
            syllabus_items = parse_syllabus_file(syllabus_path)
        except RuntimeError as ocr_error:
            flash(str(ocr_error), 'error')
            return redirect(url_for('upload_page'))

        if not exam_items:
            flash('Could not detect exam subjects or dates from the timetable. Try a clearer file.', 'error')
            return redirect(url_for('upload_page'))

        plan_entries, subject_summary = generate_study_plan_v2(exam_items, syllabus_items, student_name)
        plan_summary = build_summary_v2(plan_entries, exam_items, subject_summary)

        plan_id = db_utils.save_study_plan(
            DATABASE_PATH,
            student_name,
            json.dumps(exam_items),
            json.dumps(subject_summary),
            json.dumps(plan_entries),
            json.dumps(plan_summary),
        )

        return redirect(url_for('dashboard', plan_id=plan_id))

    return render_template('upload.html', active_page='upload')


@app.route('/dashboard')
def dashboard():
    plan_id = request.args.get('plan_id', type=int)
    plan = db_utils.get_plan(DATABASE_PATH, plan_id)

    if not plan:
        return redirect(url_for('upload_page'))

    exam_items = json.loads(plan['exam_data'])
    subjects = json.loads(plan['subjects_data'])
    plan_entries = json.loads(plan['plan_entries'])
    summary = json.loads(plan['summary_data'])

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        student_name=plan['student_name'],
        generated_at=plan['generated_at'],
        exam_items=exam_items,
        subjects=subjects,
        plan_entries=plan_entries,
        summary=summary,
        plan_id=plan['id']
    )


@app.route('/study-plan')
def study_plan():
    plan_id = request.args.get('plan_id', type=int)
    plan = db_utils.get_plan(DATABASE_PATH, plan_id)

    if not plan:
        return redirect(url_for('upload_page'))

    plan_entries = json.loads(plan['plan_entries'])
    summary = json.loads(plan['summary_data'])
    return render_template(
        'study_plan.html',
        active_page='study_plan',
        student_name=plan['student_name'],
        plan_entries=plan_entries,
        summary=summary,
        plan_id=plan['id']
    )


@app.route('/progress')
def progress_page():
    plan_id = request.args.get('plan_id', type=int)
    plan = db_utils.get_plan(DATABASE_PATH, plan_id)

    if not plan:
        return redirect(url_for('upload_page'))

    plan_entries = json.loads(plan['plan_entries'])
    summary = json.loads(plan['summary_data'])
    progress_info = db_utils.get_progress(DATABASE_PATH, plan['id'])

    return render_template(
        'progress.html',
        active_page='progress',
        student_name=plan['student_name'],
        plan_entries=plan_entries,
        summary=summary,
        progress=progress_info,
        plan_id=plan['id']
    )


@app.route('/about')
def about_page():
    return render_template('about.html', active_page='about')


@app.route('/download-plan/<int:plan_id>')
def download_plan(plan_id):
    plan = db_utils.get_plan(DATABASE_PATH, plan_id)
    if not plan:
        flash('Study plan not found. Generate a plan first.', 'error')
        return redirect(url_for('upload_page'))

    pdf_filename = f"smart-study-plan-{plan_id}.pdf"
    pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)

    if not os.path.exists(pdf_path):
        plan_entries = json.loads(plan['plan_entries'])
        summary = json.loads(plan['summary_data'])
        create_study_plan_pdf(plan['student_name'], summary, plan_entries, pdf_path)

    return send_file(pdf_path, as_attachment=True)


@app.route('/update-progress', methods=['POST'])
def update_progress():
    data = request.get_json() or {}
    plan_id = data.get('plan_id')
    completed_tasks = data.get('completed_tasks')
    total_tasks = data.get('total_tasks')

    if not plan_id or completed_tasks is None or total_tasks is None:
        return jsonify({'success': False, 'message': 'Missing progress data.'}), 400

    progress_percent = int(round((completed_tasks / total_tasks) * 100))
    progress_percent = min(max(progress_percent, 0), 100)

    db_utils.save_progress(DATABASE_PATH, plan_id, completed_tasks, total_tasks, progress_percent)
    return jsonify({'success': True, 'progress_percent': progress_percent})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)