from pathlib import Path
import argparse
import json
import os
import re

import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

import fitz
from docx import Document


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# SKILL DEFINITIONS
# ============================================================

SKILL_ALIASES = {
    "Python": [
        "python"
    ],

    "NLP": [
        "nlp",
        "natural language processing"
    ],

    "Semantic Similarity": [
        "semantic similarity",
        "sentence transformer",
        "embeddings",
        "embedding"
    ],

    "LLM": [
        "llm",
        "large language model",
        "generative ai",
        "genai"
    ],

    "Prompt Engineering": [
        "prompt engineering",
        "prompt design"
    ],

    "Machine Learning": [
        "machine learning",
        "ml"
    ],

    "APIs": [
        "api",
        "apis",
        "rest api",
        "restful api"
    ],

    "Git/GitHub": [
        "git",
        "github"
    ],

    "SQL/Data": [
        "sql",
        "data analysis",
        "pandas",
        "data handling"
    ],

    "RAG/Document Processing": [
        "rag",
        "retrieval augmented generation",
        "document processing",
        "pdf"
    ],

    "FastAPI/Streamlit": [
        "fastapi",
        "streamlit"
    ],

    "AI Agents": [
        "ai agent",
        "ai agents",
        "agentic",
        "agent"
    ],
}


# ============================================================
# SCORING WEIGHTS
# ============================================================

WEIGHTS = {
    "skills": 0.55,
    "semantic_similarity": 0.25,
    "experience": 0.10,
    "education": 0.10,
}


# ============================================================
# READ FILE
# ============================================================

def read_file(file_path):

    extension = file_path.suffix.lower()

    # ---------------- TXT ----------------

    if extension == ".txt":

        return file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    # ---------------- PDF ----------------

    elif extension == ".pdf":

        document = fitz.open(file_path)

        text = ""

        for page in document:

            text += page.get_text()

        document.close()

        return text

    # ---------------- DOCX ----------------

    elif extension == ".docx":

        document = Document(file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        return text

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text):

    text = normalize_text(text)

    detected_skills = {}

    for skill, aliases in SKILL_ALIASES.items():

        found = False

        for alias in aliases:

            pattern = (
                r"(?<!\w)"
                + re.escape(alias.lower())
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                text
            ):

                found = True

                break

        detected_skills[skill] = found

    return detected_skills


# ============================================================
# EXTRACT EXPERIENCE
# ============================================================

def extract_years_of_experience(text):

    text = normalize_text(text)

    patterns = [

        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?",

        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)"

    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        for value in matches:

            try:

                values.append(
                    float(value)
                )

            except ValueError:

                pass

    if values:

        return max(values)

    return 0.0


# ============================================================
# EDUCATION SCORE
# ============================================================

def education_score(text):

    text = normalize_text(text)

    education_terms = [

        "b.tech",
        "btech",
        "b.e",
        "bachelor",
        "m.tech",
        "mtech",
        "master",
        "computer science",
        "information technology"

    ]

    matches = sum(
        term in text
        for term in education_terms
    )

    return min(
        1.0,
        matches / 3.0
    )


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def semantic_similarity(
    jd_text,
    resume_text,
    model
):

    embeddings = model.encode(
        [
            jd_text,
            resume_text
        ],
        normalize_embeddings=True
    )

    similarity = (
        embeddings[0]
        @ embeddings[1]
    )

    return float(
        similarity
    )


# ============================================================
# CALCULATE SCORE
# ============================================================

def calculate_score(
    jd_text,
    resume_text,
    model
):

    # Extract JD skills
    jd_skills = extract_skills(
        jd_text
    )

    # Extract resume skills
    resume_skills = extract_skills(
        resume_text
    )

    # Required skills
    required_skills = [

        skill

        for skill, present
        in jd_skills.items()

        if present
    ]

    # Matched skills
    matched_skills = [

        skill

        for skill in required_skills

        if resume_skills.get(skill)
    ]

    # Missing skills
    missing_skills = [

        skill

        for skill in required_skills

        if not resume_skills.get(skill)
    ]

    # --------------------------------------------------------
    # SKILL SCORE
    # --------------------------------------------------------

    skill_score = (

        len(matched_skills)

        /

        max(
            1,
            len(required_skills)
        )

    )

    # --------------------------------------------------------
    # SEMANTIC SCORE
    # --------------------------------------------------------

    similarity = semantic_similarity(
        jd_text,
        resume_text,
        model
    )

    similarity = max(
        0.0,
        min(
            1.0,
            similarity
        )
    )

    # --------------------------------------------------------
    # EXPERIENCE SCORE
    # --------------------------------------------------------

    years = extract_years_of_experience(
        resume_text
    )

    experience = min(
        1.0,
        years / 2.0
    )

    # --------------------------------------------------------
    # EDUCATION SCORE
    # --------------------------------------------------------

    education = education_score(
        resume_text
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    final_score = 100 * (

        WEIGHTS["skills"]
        * skill_score

        +

        WEIGHTS["semantic_similarity"]
        * similarity

        +

        WEIGHTS["experience"]
        * experience

        +

        WEIGHTS["education"]
        * education

    )

    return {

        "score": round(
            final_score,
            2
        ),

        "skill_match": round(
            skill_score * 100,
            2
        ),

        "semantic_similarity": round(
            similarity * 100,
            2
        ),

        "experience_score": round(
            experience * 100,
            2
        ),

        "education_score": round(
            education * 100,
            2
        ),

        "years_experience": years,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills
    }


# ============================================================
# FALLBACK REASONING
# ============================================================

def create_fallback_reasoning(result):

    matched = (

        ", ".join(
            result["matched_skills"]
        )

        if result["matched_skills"]

        else "None"
    )

    missing = (

        ", ".join(
            result["missing_skills"]
        )

        if result["missing_skills"]

        else "None"
    )

    score = result["score"]

    if score >= 75:

        recommendation = (
            "Strong fit for the role."
        )

    elif score >= 55:

        recommendation = (
            "Moderate fit for the role."
        )

    else:

        recommendation = (
            "Lower fit for the role."
        )

    return (

        f"{recommendation} "

        f"The candidate matched these relevant skills: "
        f"{matched}. "

        f"Missing or unmatched skills: "
        f"{missing}. "

        f"The candidate has approximately "
        f"{result['years_experience']} years of experience. "

        f"Overall screening score: "
        f"{score}/100."

    )


# ============================================================
# LLM REASONING
# ============================================================

def generate_reasoning(
    jd_text,
    resume_text,
    result
):

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    # --------------------------------------------------------
    # If API key does not exist
    # --------------------------------------------------------

    if not api_key:

        return create_fallback_reasoning(
            result
        )

    # --------------------------------------------------------
    # Try OpenAI
    # --------------------------------------------------------

    try:

        from openai import OpenAI

        client = OpenAI(
            api_key=api_key
        )

        prompt = f"""
You are an HR recruitment analyst.

Evaluate the candidate ONLY using the
provided Job Description and Resume.

Explain in 2-4 concise sentences:

1. Why the candidate received this score
2. Main strengths
3. Main skill gaps
4. Overall suitability

Do not invent information.

JOB DESCRIPTION:
{jd_text[:12000]}

RESUME:
{resume_text[:12000]}

COMPUTED SCREENING RESULT:
{json.dumps(result, indent=2)}
"""

        response = client.chat.completions.create(

            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-4o-mini"
            ),

            temperature=0,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are a factual and "
                        "evidence-based recruitment analyst."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]
        )

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    # --------------------------------------------------------
    # If OpenAI fails
    # --------------------------------------------------------

    except Exception as error:

        print(
            f"\nLLM unavailable: "
            f"{type(error).__name__}: {error}\n"
        )

        return create_fallback_reasoning(
            result
        )


# ============================================================
# MAIN AGENT
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="AI Resume Screening Agent"
    )

    parser.add_argument(
        "--jd",
        required=True,
        help="Path to Job Description"
    )

    parser.add_argument(
        "--resumes",
        required=True,
        help="Folder containing resumes"
    )

    parser.add_argument(
        "--output",
        default="outputs",
        help="Output folder"
    )

    args = parser.parse_args()

    jd_path = Path(
        args.jd
    )

    resume_folder = Path(
        args.resumes
    )

    output_folder = Path(
        args.output
    )

    # Create output directory
    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # LOAD JOB DESCRIPTION
    # --------------------------------------------------------

    print(
        "\nLoading Job Description..."
    )

    jd_text = read_file(
        jd_path
    )

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    print(
        "Loading semantic similarity model..."
    )

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    # --------------------------------------------------------
    # FIND RESUMES
    # --------------------------------------------------------

    supported_extensions = {

        ".txt",
        ".pdf",
        ".docx"

    }

    resume_files = [

        file

        for file in resume_folder.iterdir()

        if file.is_file()
        and file.suffix.lower()
        in supported_extensions

    ]

    print(
        f"\nFound {len(resume_files)} resumes."
    )

    if not resume_files:

        print(
            "No supported resume files found."
        )

        return

    # --------------------------------------------------------
    # PROCESS RESUMES
    # --------------------------------------------------------

    records = []

    for resume_file in resume_files:

        print(
            f"Processing: "
            f"{resume_file.name}"
        )

        try:

            resume_text = read_file(
                resume_file
            )

            result = calculate_score(
                jd_text,
                resume_text,
                model
            )

            reasoning = generate_reasoning(
                jd_text,
                resume_text,
                result
            )

            result["candidate"] = (
                resume_file.stem
            )

            result["reasoning"] = (
                reasoning
            )

            records.append(
                result
            )

        except Exception as error:

            print(
                f"Error processing "
                f"{resume_file.name}: "
                f"{error}"
            )

    # --------------------------------------------------------
    # RANK CANDIDATES
    # --------------------------------------------------------

    records.sort(
        key=lambda item:
        item["score"],
        reverse=True
    )

    # Add rank
    for index, record in enumerate(
        records,
        start=1
    ):

        record["rank"] = index

    # --------------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------------

    json_path = (

        output_folder
        /
        "ranked_candidates.json"

    )

    json_path.write_text(

        json.dumps(
            records,
            indent=2
        ),

        encoding="utf-8"

    )

    # --------------------------------------------------------
    # PREPARE CSV
    # --------------------------------------------------------

    csv_records = []

    for record in records:

        csv_record = record.copy()

        csv_record["matched_skills"] = (
            ", ".join(
                record["matched_skills"]
            )
        )

        csv_record["missing_skills"] = (
            ", ".join(
                record["missing_skills"]
            )
        )

        csv_records.append(
            csv_record
        )

    dataframe = pd.DataFrame(
        csv_records
    )

    # --------------------------------------------------------
    # PROFESSIONAL COLUMN ORDER
    # --------------------------------------------------------

    column_order = [

        "rank",

        "candidate",

        "score",

        "skill_match",

        "semantic_similarity",

        "experience_score",

        "education_score",

        "years_experience",

        "matched_skills",

        "missing_skills",

        "reasoning"

    ]

    dataframe = dataframe[
        [
            column

            for column
            in column_order

            if column
            in dataframe.columns
        ]
    ]

    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    csv_path = (

        output_folder
        /
        "ranked_candidates.csv"

    )

    dataframe.to_csv(
        csv_path,
        index=False
    )

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "RESUME SCREENING RESULTS"
    )

    print(
        "=" * 60
    )

    for record in records:

        print(

            f"{record['rank']:>2}. "
            f"{record['candidate']:<20} "
            f"{record['score']:>6.2f}/100"

        )

    print(
        "\nResults saved:"
    )

    print(
        csv_path
    )

    print(
        json_path
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    main()