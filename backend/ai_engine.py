import re
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

COMMON_SKILLS = [
    "python", "java", "react", "next.js", "javascript", "machine learning", "ai", 
    "html", "css", "sql", "fastapi", "django", "node.js", "aws", "docker",
    "typescript", "vue", "angular", "mongodb", "postgresql", "git", "linux",
    "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "opencv",
    "kubernetes", "gcp", "azure", "ci/cd", "graphql", "rest api", "flask",
    "spring boot", "c++", "c#", "ruby", "php", "swift", "kotlin", "golang",
    "rust", "figma", "tableau", "power bi", "excel", "agile", "scrum"
]

def extract_experience_years(text: str) -> int:
    text_lower = text.lower()
    # Pattern 1: X+ years of experience / X years experience
    pattern_yrs = r'\b(\d{1,2})\+?\s*(?:years?|yrs?)\b'
    matches_yrs = re.findall(pattern_yrs, text_lower)
    years_extracted = [int(m) for m in matches_yrs if int(m) < 40]
    
    # Pattern 2: Year ranges (e.g., 2018 - 2022, 2021 to Present)
    pattern_range = r'\b(20\d{2}|19\d{2})\s*[-–—\s/to]+\s*(20\d{2}|19\d{2}|present|current|now)\b'
    matches_range = re.findall(pattern_range, text_lower)
    range_years = 0
    current_year = 2026
    for start, end in matches_range:
        s_yr = int(start)
        if end in ['present', 'current', 'now']:
            e_yr = current_year
        else:
            try:
                e_yr = int(end)
            except:
                e_yr = current_year
        if e_yr >= s_yr:
            range_years += (e_yr - s_yr)
            
    ext_years = max(years_extracted) if years_extracted else 0
    total_years = max(ext_years, range_years)
    return min(max(total_years, 0), 30)

def extract_education(text: str) -> str:
    text_lower = text.lower()
    if re.search(r'\b(ph\.?d|doctorate|doctor of philosophy)\b', text_lower):
        return "PhD"
    if re.search(r'\b(master\'?s?|m\.?s\.?|m\.?tech|m\.?c\.?a\.?|m\.?b\.?a\.?|m\.?sc\.?)\b', text_lower):
        return "Master's"
    if re.search(r'\b(bachelor\'?s?|b\.?s\.?|b\.?tech|b\.?c\.?a\.?|b\.?a\.?|b\.?sc\.?|degree)\b', text_lower):
        return "Bachelor's"
    if re.search(r'\b(associate\'?s?)\b', text_lower):
        return "Associate's"
    return "None detected"

def get_skills(text: str) -> set:
    text_lower = text.lower()
    found = set()
    for skill in COMMON_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            # Format skills nicely
            if skill in ["next.js", "ci/cd", "rest api"]:
                found.add(skill)
            elif skill in ["aws", "gcp", "ai", "sql", "html", "css"]:
                found.add(skill.upper())
            else:
                found.add(skill.title())
    return found

def extract_information(text: str):
    """
    Extracts basic info like email, phone, skills, education and experience.
    """
    info = {
        "email": None,
        "phone": None,
        "skills": [],
        "education": "None detected",
        "experience_years": 0
    }
    
    # 1. Extract Email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        info["email"] = emails[0]
        
    # 2. Extract Phone
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        info["phone"] = phones[0]
        
    # 3. Experience & Education
    info["experience_years"] = extract_experience_years(text)
    info["education"] = extract_education(text)
    
    # 4. Skills
    info["skills"] = list(get_skills(text))
    
    return info

def calculate_match_score(resume_text: str, job_description: str):
    """
    Calculates a structured match score and breakdown between resume and job description.
    """
    if nlp is None:
        return {
            "score": 0,
            "score_breakdown": {"skills": 0, "experience": 0, "education": 0, "keyword": 0},
            "matched_keywords": [],
            "missing_skills": [],
            "improvement_suggestions": ["Ensure spaCy model is loaded for parsing."],
            "ai_recommendation": "NLP model not loaded.",
            "recommended_roles": []
        }
        
    doc_resume = nlp(resume_text.lower())
    doc_jd = nlp(job_description.lower())
    
    # --- 1. Skills Calculation ---
    jd_skills = get_skills(job_description)
    resume_skills = get_skills(resume_text)
    
    matched_skills = jd_skills & resume_skills
    missing_skills = jd_skills - resume_skills
    
    if jd_skills:
        skills_score = (len(matched_skills) / len(jd_skills)) * 100
    else:
        # Default to resume skills density if no specific skills in JD
        skills_score = min(len(resume_skills) * 10, 100) if resume_skills else 50

    # --- 2. Experience Calculation ---
    resume_exp = extract_experience_years(resume_text)
    
    # Find expected experience in JD (default to 2 if not found)
    jd_exp_matches = re.findall(r'\b(\d{1,2})\+?\s*(?:years?|yrs?)\b', job_description.lower())
    jd_exp_req = int(jd_exp_matches[0]) if jd_exp_matches else 2
    
    if resume_exp >= jd_exp_req:
        experience_score = 100
    else:
        experience_score = (resume_exp / jd_exp_req) * 100 if jd_exp_req > 0 else 100
        if resume_exp > 0:
            experience_score = max(experience_score, 45) # baseline for some experience

    # --- 3. Education Calculation ---
    resume_edu = extract_education(resume_text)
    
    # Determine if JD prefers PhD or Master's
    jd_edu_req = "Bachelor's"
    jd_lower = job_description.lower()
    if re.search(r'\b(ph\.?d|doctorate)\b', jd_lower):
        jd_edu_req = "PhD"
    elif re.search(r'\b(master\'?s?|m\.?s\.?|m\.?tech|m\.?b\.?a\.?)\b', jd_lower):
        jd_edu_req = "Master's"
        
    edu_ranks = {"PhD": 4, "Master's": 3, "Bachelor's": 2, "Associate's": 1, "None detected": 0}
    resume_rank = edu_ranks.get(resume_edu, 0)
    jd_rank = edu_ranks.get(jd_edu_req, 2)
    
    if resume_rank >= jd_rank:
        education_score = 100
    elif resume_rank == jd_rank - 1:
        education_score = 75
    else:
        education_score = 50

    # --- 4. Keyword Calculation ---
    jd_keywords = [token.lemma_ for token in doc_jd if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop]
    resume_lemmas = [token.lemma_ for token in doc_resume]
    
    unique_jd_keywords = set(jd_keywords)
    matched_keywords = unique_jd_keywords.intersection(set(resume_lemmas))
    
    if unique_jd_keywords:
        keyword_score = (len(matched_keywords) / len(unique_jd_keywords)) * 100
    else:
        # Semantic fallback
        keyword_score = doc_resume.similarity(doc_jd) * 100

    # --- Overall Score Calculation (Weighted) ---
    # 40% Skills, 25% Experience, 15% Education, 20% Keywords
    overall_score = (skills_score * 0.40) + (experience_score * 0.25) + (education_score * 0.15) + (keyword_score * 0.20)
    overall_score = min(max(overall_score, 0), 100)

    # --- 5. Recommended Roles ---
    roles_map = {
        "Frontend Developer": {"react", "next.js", "javascript", "typescript", "html", "css", "vue", "angular", "figma"},
        "Backend Developer": {"python", "java", "golang", "fastapi", "django", "node.js", "sql", "postgresql", "mongodb", "spring boot", "c++", "rest api"},
        "Machine Learning Engineer": {"machine learning", "ai", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "opencv"},
        "DevOps Engineer": {"aws", "gcp", "azure", "docker", "kubernetes", "linux", "git", "ci/cd"},
    }
    
    matched_roles = []
    resume_skills_lower = {s.lower() for s in resume_skills}
    for role, role_skills in roles_map.items():
        overlap = resume_skills_lower.intersection(role_skills)
        if len(overlap) >= 1:
            matched_roles.append((role, len(overlap)))
            
    matched_roles.sort(key=lambda x: x[1], reverse=True)
    recommended_roles = [r[0] for r in matched_roles[:3]]
    
    # Fallbacks
    if not recommended_roles:
        if "Python" in resume_skills or "Java" in resume_skills:
            recommended_roles = ["Backend Developer", "Software Engineer"]
        else:
            recommended_roles = ["Software Engineer"]
    elif len(recommended_roles) == 1:
        recommended_roles.append("Software Engineer")

    # --- 6. Improvement Suggestions ---
    suggestions = []
    if missing_skills:
        suggestions.append(f"Add missing skills requested by this JD: {', '.join(list(missing_skills)[:3])}.")
    if resume_exp < jd_exp_req:
        suggestions.append(f"Detail more hands-on projects or work experience to demonstrate the required {jd_exp_req} years (currently {resume_exp} years found).")
    else:
        suggestions.append("Add measurable outcomes/KPIs for your roles (e.g. 'Improved API response time by 30%').")
        
    if resume_rank < jd_rank:
        suggestions.append(f"Consider acquiring certifications or detailing academic work equivalent to a {jd_edu_req} degree.")
    if keyword_score < 50:
        suggestions.append("Include more specific industry-related nouns and phrases from the job description to pass ATS screening.")
        
    if len(suggestions) < 3:
        suggestions.append("Ensure your resume contains working links to your professional portfolio or GitHub repositories.")
        suggestions.append("Clearly separate technical skills into categories (e.g. Languages, Frameworks, Tools).")

    # --- 7. AI Recommendation Paragraph ---
    if overall_score >= 80:
        recommendation = f"Highly Recommended. The applicant represents an excellent fit with a {overall_score:.0f}% overall match. They possess the core skills ({', '.join(list(matched_skills)[:3])}) and meet the experience/education criteria."
    elif overall_score >= 55:
        rec_matched_skills = list(matched_skills)[:2]
        matched_str = f" in {', '.join(rec_matched_skills)}" if rec_matched_skills else ""
        recommendation = f"Consider for Interview. Good candidate with a {overall_score:.0f}% match. Has solid foundations{matched_str}, but has skill gaps in {', '.join(list(missing_skills)[:2]) if missing_skills else 'certain domains'}."
    else:
        recommendation = f"Not Recommended. Low compatibility ({overall_score:.0f}% match). There are significant skill gaps ({', '.join(list(missing_skills)[:3]) if missing_skills else 'technical areas'}) and experience mismatch."

    return {
        "score": round(overall_score, 1),
        "score_breakdown": {
            "skills": round(skills_score, 1),
            "experience": round(experience_score, 1),
            "education": round(education_score, 1),
            "keyword": round(keyword_score, 1)
        },
        "matched_keywords": list(matched_keywords),
        "missing_skills": list(missing_skills),
        "improvement_suggestions": suggestions,
        "ai_recommendation": recommendation,
        "recommended_roles": recommended_roles
    }

