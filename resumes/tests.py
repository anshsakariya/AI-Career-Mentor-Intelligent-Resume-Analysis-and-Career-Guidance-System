from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from resumes.models import Resume, ResumeAnalysis
from agents.resume_agent import ResumeAgent

class ResumeTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='resumetest', password='password123')
        self.user.profile.target_role = 'Python Developer'
        self.user.profile.save()

    def test_resume_agent_analysis(self):
        """Test ResumeAgent section detection, skill parsing, and ATS score calculation."""
        sample_text = """
        John Doe
        Email: john@example.com | Phone: 555-0199
        SUMMARY
        Passionate Python developer building web applications.
        EDUCATION
        B.Tech in Computer Science, State University 2024
        SKILLS
        Python, Django, PostgreSQL, SQL, Git, REST API, HTML, CSS
        EXPERIENCE
        Junior Developer at Tech Co. Built Django endpoints.
        PROJECTS
        AI Resume Analyzer: Built Django application with PyPDF2.
        """
        
        dummy_file = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 dummy pdf content", content_type="application/pdf")
        resume = Resume.objects.create(user=self.user, file=dummy_file, extracted_text=sample_text)

        agent = ResumeAgent()
        analysis = agent.analyze_resume(resume)

        self.assertIsInstance(analysis, ResumeAnalysis)
        self.assertGreater(analysis.ats_score, 50)
        self.assertIn("Contains a clear, dedicated Education section.", analysis.strengths)
