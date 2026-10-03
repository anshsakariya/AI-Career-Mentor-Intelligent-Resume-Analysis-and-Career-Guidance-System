import re
from resumes.services import detect_resume_sections, extract_skills_from_text, extract_contact_info
from resumes.models import ResumeAnalysis
from skills.models import UserSkill

class ResumeAgent:
    """
    Agent responsible for inspecting resume text, assessing section completeness,
    scoring ATS compliance (0-100), and generating tailored recommendations.
    """
    
    def __init__(self):
        self.role_keywords = {
            'Python Developer': ['python', 'django', 'flask', 'sql', 'git', 'rest api', 'postgresql', 'docker', 'pytest'],
            'Django Developer': ['django', 'python', 'rest api', 'postgresql', 'orm', 'celery', 'redis', 'html', 'css'],
            'Full Stack Developer': ['javascript', 'react', 'node', 'python', 'html', 'css', 'sql', 'git', 'rest api'],
            'Backend Developer': ['python', 'java', 'node', 'sql', 'postgresql', 'microservices', 'docker', 'redis', 'api'],
            'Data Analyst': ['python', 'sql', 'pandas', 'numpy', 'matplotlib', 'tableau', 'excel', 'data analysis', 'statistics'],
            'Data Scientist': ['python', 'machine learning', 'pandas', 'numpy', 'scikit-learn', 'deep learning', 'statistics', 'sql'],
            'Machine Learning Engineer': ['python', 'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'docker', 'mlops'],
            'AI Engineer': ['python', 'generative ai', 'llm', 'langchain', 'openai', 'pytorch', 'machine learning', 'transformers'],
            'Software Developer': ['python', 'java', 'c++', 'git', 'sql', 'data structures', 'algorithms', 'object-oriented'],
        }

    def analyze_resume(self, resume):
        """
        Executes complete analysis pipeline on a Resume instance.
        """
        text = resume.extracted_text
        text_lower = text.lower()
        user = resume.user
        target_role = getattr(user.profile, 'target_role', 'Python Developer')

        # 1. Detect Sections
        sections = detect_resume_sections(text)

        # 2. Extract Skills
        extracted_skills = extract_skills_from_text(text)
        
        # Save extracted skills to UserSkill model
        for skill in extracted_skills:
            UserSkill.objects.get_or_create(
                user=user,
                skill=skill,
                is_target=False,
                defaults={'is_extracted': True}
            )

        # 3. Calculate Section Completeness (Structure Score)
        section_count = sum(1 for present in sections.values() if present)
        total_sections = len(sections)
        structure_score = int((section_count / total_sections) * 100) if total_sections > 0 else 50

        # 4. Calculate Skills Score
        skill_count = len(extracted_skills)
        if skill_count >= 10:
            skills_score = 95
        elif skill_count >= 6:
            skills_score = 80
        elif skill_count >= 3:
            skills_score = 65
        else:
            skills_score = 40

        # 5. Calculate Keyword Score against Target Role
        expected_keywords = self.role_keywords.get(target_role, self.role_keywords['Python Developer'])
        matched_kw_count = sum(1 for kw in expected_keywords if kw in text_lower)
        keyword_score = int((matched_kw_count / len(expected_keywords)) * 100) if expected_keywords else 50

        # 6. Education Score
        education_score = 90 if sections.get('education') else 40

        # 7. Experience & Projects Score
        experience_score = 85 if sections.get('experience') else 50
        projects_score = 85 if sections.get('projects') else 45

        # 8. Compute Total Weighted ATS Score
        total_ats_score = int(
            (skills_score * 0.25) +
            (keyword_score * 0.25) +
            (structure_score * 0.15) +
            (education_score * 0.15) +
            (experience_score * 0.10) +
            (projects_score * 0.10)
        )
        total_ats_score = min(100, max(10, total_ats_score))

        # 9. Generate Strengths, Weaknesses, and Suggestions
        strengths = []
        weaknesses = []
        suggestions = []

        if sections.get('education'):
            strengths.append("Contains a clear, dedicated Education section.")
        else:
            weaknesses.append("Missing a distinct Education header.")
            suggestions.append("Add an Education section highlighting your degree and graduation year.")

        if skill_count >= 5:
            strengths.append(f"Strong technical skill coverage with {skill_count} detected skills.")
        else:
            weaknesses.append("Low count of technical skills detected.")
            suggestions.append("Add more specific tools, frameworks, and programming languages to your Skills section.")

        if matched_kw_count >= (len(expected_keywords) // 2):
            strengths.append(f"Good keyword alignment for {target_role} positions.")
        else:
            missing_kws = [kw.title() for kw in expected_keywords if kw not in text_lower][:4]
            weaknesses.append(f"Missing core keywords for target role ({target_role}).")
            if missing_kws:
                suggestions.append(f"Incorporate missing target role keywords: {', '.join(missing_kws)}.")

        if sections.get('projects'):
            strengths.append("Project section detected with hands-on experience.")
        else:
            weaknesses.append("No explicit Projects section found.")
            suggestions.append("Include 2-3 technical projects with GitHub repository links and measurable outcomes.")

        # Save to DB
        resume.ats_score = total_ats_score
        resume.save()

        analysis, _ = ResumeAnalysis.objects.update_or_create(
            resume=resume,
            defaults={
                'ats_score': total_ats_score,
                'skills_score': skills_score,
                'keyword_score': keyword_score,
                'experience_score': experience_score,
                'projects_score': projects_score,
                'education_score': education_score,
                'structure_score': structure_score,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'suggestions': suggestions,
                'detected_sections': sections
            }
        )

        return analysis
