import math
from collections import Counter

from .models import Job
from skills.models import UserSkill
from recommendations.models import JobRecommendation
from resumes.models import Resume

# Try importing sklearn; fallback to pure-python TF-IDF if unavailable
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

def compute_pure_python_cosine_sim(text1, text2):
    """Fallback cosine similarity between two text strings using term frequencies."""
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    
    vec1 = Counter(words1)
    vec2 = Counter(words2)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

def recommend_jobs_for_user(user):
    """
    ML Recommender System calculating job compatibility using TF-IDF text similarity
    and Skill Set overlap matching.
    """
    profile = getattr(user, 'profile', None)
    target_role = profile.target_role if profile else ''
    
    # 1. Fetch User Skills
    user_skill_objs = UserSkill.objects.filter(user=user, is_extracted=True).select_related('skill')
    user_skill_names = set(us.skill.name.lower() for us in user_skill_objs)

    # 2. Fetch Latest Resume Text
    latest_resume = Resume.objects.filter(user=user).order_by('-uploaded_at').first()
    resume_text = latest_resume.extracted_text if latest_resume else ''

    # Build User Profile Document
    user_doc = f"{target_role} {' '.join(user_skill_names)} {resume_text}".lower()

    # 3. Load Jobs
    jobs = Job.objects.all().prefetch_related('required_skills', 'preferred_skills')
    if not jobs.exists():
        return []

    # 4. Prepare Corpus for TF-IDF Vectorization
    job_docs = []
    job_list = list(jobs)
    for job in job_list:
        req_skills_str = ' '.join([s.name.lower() for s in job.required_skills.all()])
        pref_skills_str = ' '.join([s.name.lower() for s in job.preferred_skills.all()])
        job_doc = f"{job.title} {job.company} {job.description} {req_skills_str} {pref_skills_str}".lower()
        job_docs.append(job_doc)

    similarity_scores = []

    if SKLEARN_AVAILABLE:
        corpus = [user_doc] + job_docs
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            user_vector = tfidf_matrix[0:1]
            job_vectors = tfidf_matrix[1:]
            similarity_scores = cosine_similarity(user_vector, job_vectors)[0]
        except Exception:
            similarity_scores = [compute_pure_python_cosine_sim(user_doc, jdoc) for jdoc in job_docs]
    else:
        similarity_scores = [compute_pure_python_cosine_sim(user_doc, jdoc) for jdoc in job_docs]

    recommendations = []

    # 5. Calculate Final Score for Each Job
    for idx, job in enumerate(job_list):
        job_req_skills = set(s.name.lower() for s in job.required_skills.all())
        job_pref_skills = set(s.name.lower() for s in job.preferred_skills.all())
        all_job_skills = job_req_skills.union(job_pref_skills)

        # Skill Overlap
        matched_set = user_skill_names.intersection(all_job_skills)
        missing_set = all_job_skills.difference(user_skill_names)

        # Matched / Missing Skill Names display strings
        matched_skill_names = [s.title() for s in matched_set]
        missing_skill_names = [s.title() for s in missing_set]

        # Skill Match Ratio
        if all_job_skills:
            skill_match_ratio = len(matched_set) / len(all_job_skills)
        else:
            skill_match_ratio = 0.5

        # Experience Match Factor
        exp_factor = 1.0
        if profile and profile.experience_level:
            if profile.experience_level == job.experience_level:
                exp_factor = 1.0
            else:
                exp_factor = 0.85

        # Cosine Similarity Score
        tfidf_sim = float(similarity_scores[idx])

        # Combined Weighted Score (0 to 100)
        final_score = int(
            (skill_match_ratio * 55) +
            (tfidf_sim * 30) +
            (exp_factor * 15)
        )
        final_score = min(99, max(25, final_score))

        # Generate Explanation
        explanation = f"{final_score}% match score calculated using ML Similarity & Skill matching. "
        if matched_skill_names:
            explanation += f"Matched skills: {', '.join(matched_skill_names[:4])}. "
        if missing_skill_names:
            explanation += f"Recommended next skills: {', '.join(missing_skill_names[:3])}."

        # Save to DB
        rec, _ = JobRecommendation.objects.update_or_create(
            user=user,
            job=job,
            defaults={
                'match_score': final_score,
                'matched_skills': matched_skill_names,
                'missing_skills': missing_skill_names,
                'explanation': explanation,
            }
        )
        recommendations.append(rec)

    # Sort by match score descending
    recommendations.sort(key=lambda r: r.match_score, reverse=True)
    return recommendations
