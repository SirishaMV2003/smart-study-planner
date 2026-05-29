"""
Study Plan Generator v2
Generates personalized study plans from exam schedule and syllabus
"""

import re
import math
from datetime import date, datetime, timedelta

QUOTES = [
    'Start strong today and your exam confidence grows with every session.',
    'Small study wins add up fast when your plan stays clear and calm.',
    'Balance your practice, review smartly, and stay ahead of exam stress.',
    'A steady rhythm beats a last-minute rush every time.',
    'Study with focus, rest with purpose, and your results will reflect it.'
]


def parse_date(text):
    """Parse date from various formats"""
    text = text.replace('/', '-').strip()
    for fmt in ['%d-%m-%Y', '%d-%m-%y', '%d %b %Y', '%d %B %Y', '%d %m %Y']:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    
    digits = re.findall(r'\d+', text)
    if len(digits) >= 3:
        day, month, year = digits[0], digits[1], digits[2]
        year = year if len(year) == 4 else f'20{year}'
        try:
            return date(int(year), int(month), int(day))
        except ValueError:
            pass
    
    return date.today() + timedelta(days=7)


def pick_quote(index=0):
    """Get motivational quote"""
    return QUOTES[index % len(QUOTES)]


def generate_study_plan_v2(exam_items, syllabus_items, student_name):
    """
    Generate study plan from exam schedule and syllabus
    
    Args:
        exam_items: List of {subject, code, date}
        syllabus_items: List of {subject, topics, hours_needed}
        student_name: Student name
        
    Returns:
        Tuple of (plan_entries, summary_subjects)
    """
    
    # Map syllabus items by subject name
    syllabus_map = {item['subject']: item for item in syllabus_items}
    
    # Sort exams by date
    sorted_exams = sorted(exam_items, key=lambda x: parse_date(x['date']))
    
    today = date.today()
    current_date = today
    plan_entries = []
    summary_subjects = []
    
    for exam in sorted_exams:
        subject = exam['subject']
        exam_date = parse_date(exam['date'])
        code = exam.get('code', '')
        
        # Get subject info from syllabus
        subject_info = syllabus_map.get(subject, {})
        topics = subject_info.get('topics', ['Core Concepts', 'Practice Problems', 'Revision'])
        hours_needed = subject_info.get('hours_needed', 2.5)
        days_needed = subject_info.get('days_needed', 1)
        difficulty = subject_info.get('difficulty', 'Medium')
        num_topics = subject_info.get('num_topics', len(topics))
        
        # Calculate available days
        days_available = max((exam_date - today).days, 1)
        
        # Determine study days
        study_days = min(days_needed, days_available)
        if study_days < 1:
            study_days = 1
        
        # Calculate hours per day
        hours_per_day = max(2, int(hours_needed / study_days * 10) / 10)
        
        # Topics per day
        topics_per_day = max(1, math.ceil(len(topics) / study_days))
        
        # Create summary
        summary_subjects.append({
            'subject': subject,
            'code': code,
            'num_topics': num_topics,
            'hours_needed': hours_needed,
            'days_needed': days_needed,
            'days_available': days_available,
            'exam_date': exam_date.strftime('%d %b %Y'),
            'urgent': days_needed > days_available,
            'difficulty': difficulty
        })
        
        # Create daily study entries
        for day_index in range(study_days):
            start_idx = day_index * topics_per_day
            end_idx = min(start_idx + topics_per_day, len(topics))
            daily_topics = topics[start_idx:end_idx]
            
            if current_date >= exam_date:
                current_date = today
            
            topics_text = '; '.join(daily_topics) if daily_topics else 'Core Concepts'
            
            note = f'Study {len(daily_topics)} topic(s): {topics_text}. '
            if days_needed > days_available:
                note = f'🔴 URGENT: {note} Complete before exam!'
            elif study_days < days_available:
                note += f'Spread across {study_days} days.'
            
            plan_entries.append({
                'date': current_date.strftime('%d %b %Y'),
                'subject': subject,
                'code': code,
                'topics': topics_text,
                'hours': hours_per_day,
                'difficulty': difficulty,
                'note': note
            })
            
            current_date += timedelta(days=1)
        
        # Add revision day before exam
        revision_date = exam_date - timedelta(days=1)
        if revision_date >= today:
            plan_entries.append({
                'date': revision_date.strftime('%d %b %Y'),
                'subject': subject,
                'code': code,
                'topics': f'Revision: {subject}',
                'hours': 1.5,
                'difficulty': difficulty,
                'note': '📚 Revision day - Review main topics and practice questions'
            })
    
    # Remove duplicates
    merged = []
    seen = set()
    for entry in plan_entries:
        key = (entry['date'], entry['subject'], entry['topics'])
        if key not in seen:
            merged.append(entry)
            seen.add(key)
    
    # Add quotes
    for idx, entry in enumerate(merged):
        entry['quote'] = pick_quote(idx)
    
    return merged, summary_subjects


def build_summary_v2(plan_entries, exam_items, subject_details=None):
    """Build study plan summary"""
    total_days = len({entry['date'] for entry in plan_entries})
    total_hours = sum(entry['hours'] for entry in plan_entries)
    subject_count = len(exam_items)
    
    next_exam = min(parse_date(item['date']) for item in exam_items)
    next_exam_subject = min(exam_items, key=lambda x: parse_date(x['date']))['subject']
    
    summary = {
        'total_days': total_days,
        'total_hours': round(total_hours, 1),
        'subject_count': subject_count,
        'next_exam': next_exam.strftime('%d %b %Y'),
        'next_exam_subject': next_exam_subject,
        'quote': pick_quote(subject_count),
        'generated_on': date.today().strftime('%d %b %Y')
    }
    
    if subject_details:
        summary['subject_details'] = subject_details
        summary['urgent_count'] = sum(1 for s in subject_details if s.get('urgent', False))
    
    return summary
