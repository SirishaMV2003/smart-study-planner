# Smart Study Planner 📚

A Flask-based application that helps students create personalized study plans by analyzing exam timetables and syllabus documents using OCR technology.

## Features

✅ **OCR-Powered Document Analysis**
- Extracts exam dates and subject codes from timetable PDFs/images
- Identifies main topics from syllabus documents
- Supports PDF and image file formats

✅ **Intelligent Study Plan Generation**
- Automatically generates balanced study schedules
- Allocates study hours based on topic complexity
- Includes revision days before exams

✅ **Interactive Dashboard**
- View exam countdown
- Track progress with completion percentage
- Download study plan as PDF

✅ **Modern UI**
- Responsive design
- Glassmorphism effects
- Intuitive navigation

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Database**: SQLite
- **OCR**: EasyOCR
- **PDF Handling**: PyPDF2, ReportLab
- **Image Processing**: Pillow

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SirishaMV2003/smart-study-planner.git
   cd smart-study-planner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   **Windows**:
   ```bash
   venv\\Scripts\\activate
   ```
   
   **macOS/Linux**:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask app**
   ```bash
   python app.py
   ```

2. **Open in browser**
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload Documents**: Navigate to the Upload page and select your exam timetable and syllabus files
2. **View Dashboard**: See extracted subjects, exam dates, and generated study plan
3. **Track Progress**: Mark completed topics and track overall progress
4. **Download Plan**: Export your study plan as a PDF

## Project Structure

```
smart-study-planner/
├── app.py                     # Main Flask application
├── requirements.txt           # Project dependencies
├── database.db               # SQLite database
├── templates/                # HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── study_plan.html
│   ├── progress.html
│   └── about.html
├── static/                   # CSS, JS, images
├── ocr/                      # OCR processing modules
│   ├── ocr_utils_new.py
│   └── subjects_config.py
├── study_plans/              # Study plan generation
│   └── plan_generator_v2.py
└── utils/                    # Utility functions
    ├── db_utils.py
    └── pdf_utils.py
```

## Key Modules

### OCR Module (`ocr/ocr_utils_new.py`)
- Parses timetable files to extract exam dates and subjects
- Extracts main topics from syllabus documents
- Uses predefined subject codes for accurate identification

### Study Plan Generator (`study_plans/plan_generator_v2.py`)
- Generates balanced study schedules
- Allocates study hours based on topic count
- Distributes topics across available days
- Adds revision days before exams

### Database Module (`utils/db_utils.py`)
- Manages SQLite database
- Stores uploads, study plans, and progress
- Provides data retrieval functions

### PDF Export (`utils/pdf_utils.py`)
- Creates professional PDF reports
- Includes study plan, topics, and timeline

## Supported Subject Codes

- 25MT21 - MATHEMATICS
- 25CHC22 - CHEMISTRY
- 25CED23 - CIVIL ENGINEERING DESIGN
- 25PL25 - PYTHON
- 25ICO27 - INDIAN CONSTITUTION
- 25ENL26 - ENGLISH
- 25PHC22 - PHYSICS
- 25ES24 - ENVIRONMENTAL SCIENCE
- 25ET25 - ENVIRONMENTAL TECHNOLOGY

*To add more subject codes, edit `ocr/subjects_config.py`*

## Troubleshooting

### "Connection Refused" Error
- Ensure Flask is running on port 5000
- Try: `http://127.0.0.1:5000` instead of localhost

### OCR Not Working
- Verify file is clear and readable
- Ensure subject codes are defined in `subjects_config.py`

### PDF Download Issues
- Check that `generated_pdfs` folder is writable
- Verify ReportLab is properly installed

## Future Enhancements

- [ ] User authentication and accounts
- [ ] Calendar view and weekly planner
- [ ] Email reminders for upcoming exams
- [ ] Mobile app version
- [ ] Support for multiple languages
- [ ] AI-powered personalized tips

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an GitHub issue.

---

**Made with ❤️ for students**
