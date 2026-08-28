import os
import re
import json
import argparse
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

try:
    import pymupdf
except ImportError:
    # Compatibility fallback for older PyMuPDF installations
    import fitz as pymupdf

from docx import Document

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

# Final score weights
SEMANTIC_WEIGHT = 40
SKILL_WEIGHT = 35
EXPERIENCE_WEIGHT = 15
EDUCATION_WEIGHT = 10

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

llm_client = None
llm_disabled = False


# ============================================================
# COMMON SKILLS
# ============================================================

SKILL_LIST = {
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "golang",
    "rust",
    "php",
    "ruby",
    "kotlin",
    "swift",

    # Web
    "html",
    "css",
    "react",
    "react.js",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "express",
    "next.js",
    "nextjs",

    # Backend / APIs
    "rest api",
    "restful api",
    "api",
    "fastapi",
    "flask",
    "django",
    "spring",
    "spring boot",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "sqlite",
    "oracle",
    "redis",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "nlp",
    "natural language processing",
    "computer vision",
    "generative ai",
    "genai",
    "llm",
    "large language model",
    "transformers",
    "hugging face",
    "huggingface",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "keras",
    "opencv",
    "pandas",
    "numpy",

    # Data
    "data analysis",
    "data analytics",
    "data science",
    "statistics",
    "excel",
    "power bi",
    "tableau",

    # Cloud / DevOps
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "docker",
    "kubernetes",
    "git",
    "github",
    "gitlab",
    "jenkins",
    "ci/cd",
    "linux",

    # Testing
    "selenium",
    "pytest",
    "junit",
    "unit testing",
    "automation testing",
    "manual testing",
    "software testing",
    "test automation",

    # Other
    "agile",
    "scrum",
    "jira",
    "salesforce",
    "sap",
}


# ============================================================
# FILE EXTRACTION
# ============================================================

def read_txt(file_path):
    """Read a TXT file."""
    return Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    )


def read_pdf(file_path):
    """Extract text from a PDF."""
    text_parts = []

    document = pymupdf.open(file_path)

    try:
        for page in document:
            text_parts.append(page.get_text())
    finally:
        document.close()

    return "\n".join(text_parts)


def read_docx(file_path):
    """Extract text from DOCX."""
    document = Document(file_path)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text(file_path):
    """Extract text based on file extension."""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".txt":
        return read_txt(file_path)

    if suffix == ".pdf":
        return read_pdf(file_path)

    if suffix == ".docx":
        return read_docx(file_path)

    raise ValueError(
        f"Unsupported file format: {suffix}"
    )


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """Normalize text for matching."""
    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def phrase_in_text(phrase, text):
    """
    Check whether a skill/phrase exists in text.
    Handles punctuation such as python / Python.
    """
    phrase = normalize_text(phrase)
    text = normalize_text(text)

    escaped = re.escape(phrase)

    # Word boundaries for normal phrases
    pattern = rf"(?<!\w){escaped}(?!\w)"

    return re.search(pattern, text) is not None


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):
    """
    Extract known technical skills from text.
    """
    normalized = normalize_text(text)

    found = set()

    for skill in SKILL_LIST:
        skill_normalized = normalize_text(skill)

        pattern = rf"(?<!\w){re.escape(skill_normalized)}(?!\w)"

        if re.search(pattern, normalized):
            found.add(skill)

    return sorted(found)


def calculate_skill_score(jd_skills, resume_skills):
    """
    Calculate skill match percentage.
    """
    if not jd_skills:
        return 0.0

    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    matched = jd_set.intersection(resume_set)

    return round(
        (len(matched) / len(jd_set)) * 100,
        2
    )


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def estimate_experience(text):
    """
    Estimate years of experience from resume text.
    """
    normalized = normalize_text(text)

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+in",
    ]

    values = []

    for pattern in patterns:
        matches = re.findall(pattern, normalized)

        for match in matches:
            try:
                values.append(float(match))
            except ValueError:
                pass

    if values:
        return round(max(values), 1)

    # Fresher / entry-level indicators
    if any(
        phrase in normalized
        for phrase in [
            "fresher",
            "recent graduate",
            "recently graduated",
            "entry level",
            "entry-level",
        ]
    ):
        return 0.0

    return 0.0


def extract_required_experience(jd_text):
    """
    Extract required experience from the JD.
    """
    normalized = normalize_text(jd_text)

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"at\s+least\s+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]

    values = []

    for pattern in patterns:
        matches = re.findall(pattern, normalized)

        for match in matches:
            try:
                values.append(float(match))
            except ValueError:
                pass

    if values:
        return max(values)

    return 0.0


def calculate_experience_score(candidate_years, required_years):
    """
    Calculate experience score out of 100.
    """
    if required_years <= 0:
        if candidate_years > 0:
            return 100.0
        return 70.0

    if candidate_years >= required_years:
        return 100.0

    score = (candidate_years / required_years) * 100

    return round(max(0.0, min(100.0, score)), 2)


# ============================================================
# EDUCATION
# ============================================================

def extract_education(text):
    """
    Detect common education qualifications.
    """
    normalized = normalize_text(text)

    education_keywords = [
        "phd",
        "doctorate",
        "master",
        "m.tech",
        "mtech",
        "m.e.",
        "mba",
        "msc",
        "m.sc",
        "bachelor",
        "b.tech",
        "btech",
        "b.e.",
        "be ",
        "bsc",
        "b.sc",
        "bca",
        "mca",
        "diploma",
        "computer science",
        "information technology",
        "software engineering",
        "data science",
        "artificial intelligence",
    ]

    found = []

    for keyword in education_keywords:
        if keyword in normalized:
            found.append(keyword.strip())

    return sorted(set(found))


def calculate_education_score(jd_text, resume_text):
    """
    Estimate education relevance.
    """
    jd_education = extract_education(jd_text)
    resume_education = extract_education(resume_text)

    if not jd_education:
        return 70.0

    if not resume_education:
        return 30.0

    jd_text_normalized = normalize_text(jd_text)
    resume_text_normalized = normalize_text(resume_text)

    matches = 0

    for keyword in jd_education:
        if keyword in resume_text_normalized:
            matches += 1

    if matches == 0:
        # Check broader technical relevance
        technical_fields = [
            "computer science",
            "information technology",
            "software engineering",
            "artificial intelligence",
            "data science",
        ]

        for field in technical_fields:
            if (
                field in jd_text_normalized
                and field in resume_text_normalized
            ):
                matches += 1

    if matches == 0:
        return 40.0

    score = (matches / len(jd_education)) * 100

    return round(max(0.0, min(100.0, score)), 2)


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def calculate_semantic_similarity(
    model,
    jd_text,
    resume_text
):
    """
    Calculate semantic similarity using Sentence Transformers.
    """
    jd_embedding = model.encode(
        jd_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    resume_embedding = model.encode(
        resume_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarity = util.cos_sim(
        jd_embedding,
        resume_embedding
    ).item()

    # Convert [-1,1] into [0,100]
    score = ((similarity + 1) / 2) * 100

    return round(
        max(0.0, min(100.0, score)),
        2
    )


# ============================================================
# OVERALL SCORE
# ============================================================

def calculate_overall_score(
    semantic_score,
    skill_score,
    experience_score,
    education_score
):
    """
    Calculate weighted final score.
    """
    score = (
        semantic_score * SEMANTIC_WEIGHT / 100
        + skill_score * SKILL_WEIGHT / 100
        + experience_score * EXPERIENCE_WEIGHT / 100
        + education_score * EDUCATION_WEIGHT / 100
    )

    return round(
        max(0.0, min(100.0, score)),
        2
    )


# ============================================================
# DETERMINISTIC REASONING
# ============================================================

def generate_fallback_reasoning(
    jd_text,
    resume_text,
    result
):
    """
    Generate reasoning without an LLM.

    This guarantees that the application continues to work
    even when the OpenAI API is unavailable.
    """
    matched = result["matched_skills"]
    missing = result["missing_skills"]

    semantic = result["semantic_similarity"]
    skill = result["skill_match"]
    experience = result["experience_score"]
    education = result["education_score"]
    overall = result["overall_score"]

    candidate_years = result["estimated_experience"]
    required_years = result["required_experience"]

    strengths = []

    if matched:
        preview = ", ".join(matched[:8])
        strengths.append(
            f"matches relevant skills including {preview}"
        )

    if semantic >= 75:
        strengths.append(
            "has strong semantic alignment with the job description"
        )
    elif semantic >= 55:
        strengths.append(
            "shows moderate semantic alignment with the job description"
        )

    if required_years <= 0 and candidate_years > 0:
        strengths.append(
            f"shows approximately {candidate_years:g} years of experience"
        )
    elif required_years > 0 and candidate_years >= required_years:
        strengths.append(
            f"meets the estimated experience requirement of "
            f"{required_years:g} years"
        )

    if education >= 70:
        strengths.append(
            "has relevant educational background"
        )

    if not strengths:
        strengths.append(
            "shows some relevant evidence against the job description"
        )

    gaps = []

    if missing:
        gaps.append(
            "missing identified skills such as "
            + ", ".join(missing[:8])
        )

    if required_years > candidate_years:
        gaps.append(
            f"estimated experience ({candidate_years:g} years) "
            f"is below the requested {required_years:g} years"
        )

    if education < 50:
        gaps.append(
            "limited evidence of directly relevant education"
        )

    if not gaps:
        gaps.append(
            "no major gaps were detected using the available rules"
        )

    reasoning = (
        f"Overall score: {overall}/100. "
        f"The candidate {', '.join(strengths)}. "
        f"Semantic similarity is {semantic}/100 and skill matching is "
        f"{skill}/100. Experience score is {experience}/100 and "
        f"education score is {education}/100. "
        f"Main consideration: {'; '.join(gaps)}."
    )

    return reasoning


# ============================================================
# OPENAI REASONING
# ============================================================

def initialize_llm():
    """
    Initialize OpenAI client only when an API key is available.
    """
    global llm_client

    if not OPENAI_API_KEY:
        print(
            "OpenAI API key not found. "
            "Using deterministic reasoning."
        )
        return

    if OpenAI is None:
        print(
            "OpenAI package unavailable. "
            "Using deterministic reasoning."
        )
        return

    try:
        llm_client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        print(
            f"OpenAI reasoning enabled "
            f"({OPENAI_MODEL})."
        )

    except Exception as exc:
        llm_client = None

        print(
            f"OpenAI initialization failed: {exc}. "
            "Using deterministic reasoning."
        )


def generate_llm_reasoning(
    jd_text,
    resume_text,
    result
):
    """
    Ask OpenAI for candidate reasoning.

    If quota/API errors occur, LLM is disabled for the rest
    of the run so we don't repeatedly generate 429 errors.
    """
    global llm_disabled

    if llm_client is None or llm_disabled:
        return None

    matched = result["matched_skills"]
    missing = result["missing_skills"]

    prompt = f"""
You are an AI resume screening assistant.

Evaluate the candidate against the job description.

JOB DESCRIPTION:
{jd_text[:12000]}

RESUME:
{resume_text[:12000]}

CALCULATED SCORES:
Overall score: {result["overall_score"]}/100
Semantic similarity: {result["semantic_similarity"]}/100
Skill match: {result["skill_match"]}/100
Experience score: {result["experience_score"]}/100
Education score: {result["education_score"]}/100

Matched skills:
{", ".join(matched) if matched else "None"}

Missing skills:
{", ".join(missing) if missing else "None"}

Estimated candidate experience:
{result["estimated_experience"]} years

Estimated required experience:
{result["required_experience"]} years

Write a concise professional hiring rationale.

Mention:
1. Strongest relevant skills
2. Experience fit
3. Education relevance
4. Main skill gaps
5. Overall suitability

Do not invent information that is not present in the resume.
Keep the answer under 120 words.
"""

    try:
        response = llm_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise resume screening "
                        "assistant. Use only the supplied information."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=250,
        )

        content = response.choices[0].message.content

        if content:
            return content.strip()

        return None

    except Exception as exc:
        # Disable LLM after first failure.
        # This prevents 10 repeated 429 errors.
        llm_disabled = True

        print(
            f"LLM unavailable: {type(exc).__name__}. "
            "Switching to deterministic reasoning."
        )

        return None


# ============================================================
# CANDIDATE ANALYSIS
# ============================================================

def analyze_candidate(
    jd_text,
    resume_text,
    model,
    filename
):
    """
    Complete candidate evaluation.
    """

    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)

    matched_skills = sorted(
        set(jd_skills).intersection(resume_skills)
    )

    missing_skills = sorted(
        set(jd_skills).difference(resume_skills)
    )

    skill_score = calculate_skill_score(
        jd_skills,
        resume_skills
    )

    semantic_score = calculate_semantic_similarity(
        model,
        jd_text,
        resume_text
    )

    candidate_experience = estimate_experience(
        resume_text
    )

    required_experience = extract_required_experience(
        jd_text
    )

    experience_score = calculate_experience_score(
        candidate_experience,
        required_experience
    )

    education_score = calculate_education_score(
        jd_text,
        resume_text
    )

    overall_score = calculate_overall_score(
        semantic_score,
        skill_score,
        experience_score,
        education_score
    )

    result = {
        "candidate": Path(filename).stem,
        "filename": filename,
        "overall_score": overall_score,
        "semantic_similarity": semantic_score,
        "skill_match": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "estimated_experience": candidate_experience,
        "required_experience": required_experience,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "reasoning": "",
    }

    # Try LLM first if available
    reasoning = generate_llm_reasoning(
        jd_text,
        resume_text,
        result
    )

    # Guaranteed fallback
    if not reasoning:
        reasoning = generate_fallback_reasoning(
            jd_text,
            resume_text,
            result
        )

    result["reasoning"] = reasoning

    return result


# ============================================================
# LOAD RESUMES
# ============================================================

def get_resume_files(resume_directory):
    """
    Find supported resume files recursively.
    """
    directory = Path(resume_directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Resume directory not found: {directory}"
        )

    extensions = {
        ".txt",
        ".pdf",
        ".docx",
    }

    files = [
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in extensions
    ]

    return sorted(files)


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results, output_directory):
    """
    Save ranked candidates to CSV and JSON.
    """
    output_path = Path(output_directory)
    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Ranked order
    results = sorted(
        results,
        key=lambda item: item["overall_score"],
        reverse=True
    )

    # Add rank
    for index, result in enumerate(results, start=1):
        result["rank"] = index

    # CSV-friendly version
    csv_rows = []

    for result in results:
        row = {
            "rank": result["rank"],
            "candidate": result["candidate"],
            "overall_score": result["overall_score"],
            "semantic_similarity": result["semantic_similarity"],
            "skill_match": result["skill_match"],
            "experience_score": result["experience_score"],
            "education_score": result["education_score"],
            "estimated_experience": result["estimated_experience"],
            "required_experience": result["required_experience"],
            "matched_skills": ", ".join(
                result["matched_skills"]
            ),
            "missing_skills": ", ".join(
                result["missing_skills"]
            ),
            "reasoning": result["reasoning"],
        }

        csv_rows.append(row)

    dataframe = pd.DataFrame(csv_rows)

    csv_file = output_path / "ranked_candidates.csv"

    dataframe.to_csv(
        csv_file,
        index=False,
        encoding="utf-8"
    )

    json_file = output_path / "ranked_candidates.json"

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    return csv_file, json_file


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "AI Resume Screening Agent - "
            "Ranks resumes against a job description."
        )
    )

    parser.add_argument(
        "--jd",
        required=True,
        help="Path to Job Description file"
    )

    parser.add_argument(
        "--resumes",
        required=True,
        help="Directory containing resumes"
    )

    parser.add_argument(
        "--output",
        default="outputs",
        help="Output directory"
    )

    args = parser.parse_args()

    jd_path = Path(args.jd)
    resume_directory = Path(args.resumes)

    # --------------------------------------------------------
    # Validate JD
    # --------------------------------------------------------

    if not jd_path.exists():
        raise FileNotFoundError(
            f"Job description not found: {jd_path}"
        )

    print("Loading Job Description...")

    jd_text = extract_text(jd_path)

    if not jd_text.strip():
        raise ValueError(
            "Job Description is empty."
        )

    # --------------------------------------------------------
    # Load semantic model
    # --------------------------------------------------------

    print("Loading semantic similarity model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    # --------------------------------------------------------
    # Initialize LLM
    # --------------------------------------------------------

    initialize_llm()

    # --------------------------------------------------------
    # Find resumes
    # --------------------------------------------------------

    resume_files = get_resume_files(
        resume_directory
    )

    print(
        f"\nFound {len(resume_files)} resumes."
    )

    if not resume_files:
        raise ValueError(
            "No TXT, PDF, or DOCX resumes found."
        )

    # --------------------------------------------------------
    # Process candidates
    # --------------------------------------------------------

    results = []

    for resume_file in resume_files:

        print(
            f"Processing: {resume_file.name}"
        )

        try:
            resume_text = extract_text(
                resume_file
            )

            if not resume_text.strip():
                print(
                    "Warning: Resume is empty. Skipping."
                )
                continue

            result = analyze_candidate(
                jd_text=jd_text,
                resume_text=resume_text,
                model=model,
                filename=resume_file.name
            )

            results.append(result)

        except Exception as exc:
            print(
                f"Error processing "
                f"{resume_file.name}: {exc}"
            )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    results.sort(
        key=lambda item: item["overall_score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("RESUME SCREENING RESULTS")
    print("=" * 60)

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{index:2}. "
            f"{result['candidate']:<20} "
            f"{result['overall_score']:.2f}/100"
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    csv_file, json_file = save_results(
        results,
        args.output
    )

    print("\n")
    print("Results saved:")
    print(csv_file)
    print(json_file)


if __name__ == "__main__":
    main()