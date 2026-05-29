"""PDF utilities for generating study plan PDFs"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def create_study_plan_pdf(student_name, summary, plan_entries, file_path):
    """Create a PDF with the study plan"""
    pdf = canvas.Canvas(file_path, pagesize=letter)
    pdf.setTitle('Smart Study Planner')

    # Header
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(50, 740, 'Smart Study Planner')

    # Summary info
    pdf.setFont('Helvetica', 11)
    pdf.drawString(50, 720, f'Student: {student_name}')
    pdf.drawString(50, 705, f'Generated on: {summary.get("generated_on", "-")}')
    pdf.drawString(50, 690, f'Next exam: {summary.get("next_exam_subject", "-")} on {summary.get("next_exam", "-")}')
    pdf.drawString(50, 675, f'Total study days: {summary.get("total_days", 0)}')
    pdf.drawString(50, 660, f'Estimated study hours: {summary.get("total_hours", 0)}')

    # Divider line
    pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
    pdf.line(50, 652, 560, 652)

    # Plan title
    pdf.setFont('Helvetica-Bold', 13)
    pdf.drawString(50, 630, 'Study Plan Overview')

    # Plan entries
    start_y = 610
    pdf.setFont('Helvetica', 10)
    for entry in plan_entries:
        if start_y < 100:
            pdf.showPage()
            start_y = 740
            pdf.setFont('Helvetica', 10)

        pdf.drawString(50, start_y, f"{entry.get('date', '')} - {entry.get('subject', '')} ({entry.get('hours', 0)} hrs)")
        pdf.drawString(60, start_y - 14, f"Topics: {entry.get('topics', 'N/A')}")
        pdf.drawString(60, start_y - 28, f"Note: {entry.get('note', 'N/A')}")
        start_y -= 50

    pdf.showPage()
    pdf.save()
