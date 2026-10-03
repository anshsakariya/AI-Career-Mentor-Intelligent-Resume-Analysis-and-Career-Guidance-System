import re
import PyPDF2
from skills.models import Skill

def extract_resume_text(file_path):
    """
    Extracts raw text from a PDF file using PyPDF2.
    """
    text = ""
    try:
        reader = PyPDF2.PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""

    # Clean whitespace & linebreaks
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = "\n".join(lines)
    return cleaned_text

def extract_contact_info(text):
    """
    Extracts email and phone number using Regex.
    """
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else ""

    return {'email': email, 'phone': phone}

def detect_resume_sections(text):
    """
    Detects presence of key resume sections.
    """
    text_lower = text.lower()
    sections = {
        'summary': any(kw in text_lower for kw in ['summary', 'objective', 'profile', 'about me']),
        'education': any(kw in text_lower for kw in ['education', 'academic', 'qualification', 'degree']),
        'experience': any(kw in text_lower for kw in ['experience', 'employment', 'work history', 'internship']),
        'skills': any(kw in text_lower for kw in ['skills', 'technical skills', 'competencies', 'technologies']),
        'projects': any(kw in text_lower for kw in ['projects', 'academic projects', 'key projects']),
        'certifications': any(kw in text_lower for kw in ['certification', 'certificates', 'courses']),
        'achievements': any(kw in text_lower for kw in ['achievement', 'awards', 'honors']),
    }
    return sections

def extract_skills_from_text(text):
    """
    Matches text against registered DB skills and common tech skill terms.
    """
    text_lower = text.lower()
    matched_skills = set()

    # Load DB skills
    db_skills = Skill.objects.all()
    if db_skills.exists():
        for skill in db_skills:
            # Word boundary regex search to avoid partial word match (e.g. 'c' matching 'chat')
            pattern = r'\b' + re.escape(skill.name.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched_skills.add(skill)

    # Standard default skill library backup if DB skills not fully populated
    default_skill_names = [
        'python', 'django', 'flask', 'fastapi', 'sql', 'postgresql', 'mysql', 'sqlite',
        'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'html', 'css',
        'bootstrap', 'node.js', 'express', 'machine learning', 'data science', 'pandas',
        'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'nltk', 'opencv', 'docker',
        'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github', 'rest api', 'graphql',
        'redis', 'celery', 'linux', 'c++', 'c#', 'php', 'ruby'
    ]

    for skill_name in default_skill_names:
        pattern = r'\b' + re.escape(skill_name) + r'\b'
        if re.search(pattern, text_lower):
            # Check or create DB skill object
            skill_obj, _ = Skill.objects.get_or_create(
                name=skill_name.title() if len(skill_name) > 3 else skill_name.upper(),
                defaults={'category': 'Programming Language'}
            )
            matched_skills.add(skill_obj)

    return list(matched_skills)
