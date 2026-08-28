# AI Resume Screening Agent

An AI-powered resume screening and candidate ranking system that evaluates multiple candidate resumes against a given job description.

The system combines rule-based scoring, NLP-based semantic similarity, skill matching, experience analysis, education relevance, and optional LLM-based reasoning to generate a ranked list of candidates.

---

## Features

- Process multiple resumes automatically
- Supports TXT, PDF, and DOCX resumes
- Extract relevant technical skills
- Identify matched and missing skills
- Calculate semantic similarity between the job description and resumes
- Estimate candidate experience
- Evaluate education relevance
- Calculate an overall candidate score
- Rank candidates from highest to lowest score
- Generate candidate reasoning
- Generate CSV and JSON reports
- Optional OpenAI-powered reasoning
- Deterministic fallback reasoning when the LLM is unavailable
- Secure API key handling using environment variables

---

## How It Works

The application follows a resume screening pipeline:

```text
Job Description
       |
       v
Resume Collection
       |
       v
Text Extraction
       |
       v
Skill Extraction & Matching
       |
       +----------------------+
       |                      |
       v                      v
Skill Match           Semantic Similarity
       |                      |
       +----------+-----------+
                  |
                  v
        Experience Analysis
                  |
                  v
        Education Evaluation
                  |
                  v
        Overall Candidate Score
                  |
                  v
          Candidate Ranking
                  |
          +-------+-------+
          |               |
          v               v
        CSV             JSON
       Report           Report
```

---

## Scoring Methodology

Each candidate is evaluated using multiple factors.

### Skill Match

Measures how closely the candidate's skills match the skills required by the job description.

### Semantic Similarity

Uses an NLP embedding model to compare the overall meaning and context of the resume with the job description.

### Experience Score

Estimates the candidate's relevant professional experience based on the available resume information.

### Education Score

Evaluates the relevance of the candidate's educational background to the role.

### Overall Score

The individual evaluation factors are combined to calculate an overall candidate score out of 100.

Candidates are then ranked from the highest score to the lowest score.

---

## LLM-Based Reasoning

The application can optionally use the OpenAI API to generate natural-language reasoning for each candidate.

Example:

```text
The candidate demonstrates strong alignment with the required
technical skills and has relevant experience in Python and NLP.
The candidate is therefore a strong match for the role.
```

If the OpenAI API is unavailable because of quota, billing, network, or other API-related issues, the application uses deterministic fallback reasoning.

This allows candidate scoring, ranking, and report generation to continue even when the LLM is unavailable.

---

## Project Structure

```text
airesume-screening-system/
|
+-- app.py
+-- requirements.txt
+-- README.md
+-- .gitignore
|
+-- data/
|   +-- job_description.txt
|   |
|   +-- resumes/
|       +-- candidate_01.txt
|       +-- candidate_02.txt
|       +-- candidate_03.txt
|       +-- candidate_04.txt
|       +-- ...
|
+-- outputs/
    +-- ranked_candidates.csv
    +-- ranked_candidates.json
```

---

## Technologies Used

- Python
- Pandas
- NumPy
- Sentence Transformers
- NLP
- Semantic Similarity
- OpenAI API
- PyMuPDF
- python-docx
- python-dotenv
- JSON
- CSV

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/7855043409/airesume-screening-system.git
```

### 2. Navigate to the Project

```bash
cd airesume-screening-system
```

### 3. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Create a `.env` file in the project root directory.

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Do not upload your real API key to GitHub.

The `.env` file is excluded from version control using `.gitignore`.

For sharing the project, you can create a `.env.example` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## Input Data

### Job Description

Place the job description inside:

```text
data/job_description.txt
```

### Resumes

Place candidate resumes inside:

```text
data/resumes/
```

The application supports:

- `.txt`
- `.pdf`
- `.docx`

Example:

```text
data/resumes/
├── candidate_01.txt
├── candidate_02.txt
├── candidate_03.pdf
└── candidate_04.docx
```

---

## Running the Application

Run the following command from the project root:

```bash
python app.py --jd data/job_description.txt --resumes data/resumes --output outputs
```

The application will:

1. Load the job description
2. Load candidate resumes
3. Extract resume text
4. Extract relevant skills
5. Compare candidate skills with job requirements
6. Calculate semantic similarity
7. Estimate experience
8. Evaluate education relevance
9. Calculate an overall score
10. Generate candidate reasoning
11. Rank candidates
12. Save the results

---

## Output

After successful execution, the application generates:

```text
outputs/
├── ranked_candidates.csv
└── ranked_candidates.json
```

### CSV Report

The CSV report contains structured candidate evaluation information such as:

```text
rank
candidate
score
skill_match
semantic_similarity
experience_score
education_score
years_experience
matched_skills
missing_skills
reasoning
```

### JSON Report

The JSON report contains structured candidate evaluation data including:

- Candidate name
- Overall score
- Skill match
- Semantic similarity
- Experience score
- Education score
- Years of experience
- Matched skills
- Missing skills
- Candidate reasoning
- Rank

---

## Example Result

Example candidate ranking:

```text
============================================================
RESUME SCREENING RESULTS
============================================================

 1. candidate_01          89.93/100
 2. candidate_02          70.54/100
 3. candidate_03          57.34/100
 4. candidate_04          56.13/100
 5. candidate_07          55.91/100
 6. candidate_06          54.17/100
 7. candidate_05          47.06/100
 8. candidate_09          44.24/100
 9. candidate_08          42.59/100
10. candidate_10          31.61/100
```

The exact scores depend on the job description and resumes provided as input.

---

## Fallback Behaviour

The application is designed to continue processing even when the OpenAI API is unavailable.

### When LLM is available

```text
Resume
  |
  v
Candidate Scoring
  |
  v
OpenAI Reasoning
  |
  v
Final Candidate Report
```

### When LLM is unavailable

```text
Resume
  |
  v
Candidate Scoring
  |
  v
Deterministic Fallback Reasoning
  |
  v
Final Candidate Report
```

This ensures that candidate ranking and report generation can continue without depending completely on external LLM availability.

---

## Security

Sensitive information such as API keys must be stored using environment variables.

The following files and directories are excluded from Git:

```text
.env
.venv/
venv/
env/
__pycache__/
.cache/
```

Never commit:

- API keys
- Passwords
- Access tokens
- Private credentials
- Other sensitive information

---

## Limitations

- Resume quality affects the accuracy of extracted information.
- Experience and education scoring are based on the implemented screening logic.
- Semantic similarity measures contextual similarity but does not replace human evaluation.
- LLM reasoning depends on API availability and account quota.
- The system should be used as a recruitment assistance tool rather than an autonomous hiring decision-maker.
- Candidate ranking should be reviewed by a human recruiter before making final hiring decisions.

---

## Future Improvements

Possible future improvements include:

- Web-based recruiter dashboard
- Resume upload interface
- Advanced skill taxonomy
- Improved experience extraction
- Candidate comparison dashboard
- Interactive scoring visualization
- Database integration
- Batch processing optimization
- Additional resume formats
- Advanced LLM-based candidate analysis
- Human-in-the-loop recruiter feedback
- Automated interview recommendation
- Explainable AI scoring

---

## Project Goal

The goal of this project is to demonstrate how NLP, semantic similarity, rule-based scoring, and optional LLM reasoning can be combined to build an automated resume screening and candidate ranking system.

The project focuses on making resume screening faster, more structured, and easier to analyze while keeping human decision-making in the final hiring process.

---

## Author

**Durga Raula**

GitHub Repository:

https://github.com/7855043409/airesume-screening-system