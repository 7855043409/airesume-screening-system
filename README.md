# AI Resume Screening Agent

An AI-powered resume screening and ranking system that evaluates multiple candidate resumes against a given job description and produces a ranked candidate list with skill matching, semantic similarity, experience analysis, education scoring, and candidate reasoning.

---

## Features

- Process multiple resumes automatically
- Supports TXT, PDF, and DOCX resumes
- Extract relevant technical skills
- Identify matched and missing skills
- Calculate semantic similarity between the job description and resumes
- Estimate candidate experience
- Evaluate education relevance
- Generate an overall candidate score
- Rank candidates from highest to lowest score
- Generate CSV and JSON reports
- Use OpenAI for candidate reasoning when API quota is available
- Provide deterministic fallback reasoning when the LLM is unavailable

---

## Project Structure

```text
resume-screening-agent/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── data/
│   ├── job_description.txt
│   └── resumes/
│       ├── candidate_01.txt
│       ├── candidate_02.txt
│       ├── candidate_03.txt
│       └── ...
│
└── outputs/
    ├── ranked_candidates.csv
    └── ranked_candidates.json
```

---

## Technologies Used

- Python
- Pandas
- Sentence Transformers
- PyMuPDF
- python-docx
- OpenAI API
- python-dotenv
- Semantic Embeddings
- Rule-based Skill Matching

---

## How It Works

The system follows the pipeline below:

```text
Job Description
       │
       ▼
Resume Collection
       │
       ▼
Text Extraction
       │
       ▼
Skill Extraction
       │
       ▼
Skill Matching
       │
       ▼
Semantic Similarity
       │
       ▼
Experience Analysis
       │
       ▼
Education Analysis
       │
       ▼
Weighted Score
       │
       ▼
Candidate Ranking
       │
       ▼
LLM Reasoning / Fallback Reasoning
       │
       ▼
CSV + JSON Reports
```

---

## Scoring Methodology

The final candidate score is calculated using a weighted scoring approach.

| Component | Weight |
|---|---:|
| Skill Match | 55% |
| Semantic Similarity | 25% |
| Experience | 10% |
| Education | 10% |

### Final Score

```text
Final Score =
    Skill Match × 0.55
  + Semantic Similarity × 0.25
  + Experience × 0.10
  + Education × 0.10
```

The final score is calculated on a scale of 0–100.

---

## Skill Matching

The system checks the job description and resumes for relevant skills such as:

- Python
- NLP
- Machine Learning
- LLM
- Generative AI
- Prompt Engineering
- Semantic Similarity
- APIs
- Git/GitHub
- SQL
- RAG
- FastAPI
- Streamlit
- AI Agents

The system reports both:

- Matched skills
- Missing or unmatched skills

---

## Semantic Similarity

The system uses the Sentence Transformers model:

```text
all-MiniLM-L6-v2
```

The job description and each resume are converted into embeddings.

The similarity between the embeddings is used to estimate how closely each resume matches the job description.

---

## Candidate Reasoning

When a valid OpenAI API quota is available, the system uses an LLM to generate concise candidate reasoning based on the job description, resume, and computed screening result.

If the OpenAI API is unavailable, the system automatically uses deterministic fallback reasoning based on:

- Overall score
- Matched skills
- Missing skills
- Experience

This allows the screening pipeline to continue even when the LLM service is unavailable.

---

## Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

Never commit your actual API key to GitHub.

The `.gitignore` file excludes `.env`.

---

## Input Data

Place the job description here:

```text
data/job_description.txt
```

Place candidate resumes inside:

```text
data/resumes/
```

Supported formats:

```text
.txt
.pdf
.docx
```

---

## Running the Application

Run the following command:

```bash
python app.py --jd data/job_description.txt --resumes data/resumes --output outputs
```

Example output:

```text
Found 10 resumes.

Processing: candidate_01.txt
Processing: candidate_02.txt
Processing: candidate_03.txt
Processing: candidate_04.txt
Processing: candidate_05.txt
Processing: candidate_06.txt
Processing: candidate_07.txt
Processing: candidate_08.txt
Processing: candidate_09.txt
Processing: candidate_10.txt

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

Results saved:
outputs\ranked_candidates.csv
outputs\ranked_candidates.json
```

---

## Output Files

The application generates two reports.

### ranked_candidates.csv

Contains structured candidate ranking information including:

- Rank
- Candidate
- Overall score
- Skill match
- Semantic similarity
- Experience score
- Education score
- Years of experience
- Matched skills
- Missing skills
- Reasoning

### ranked_candidates.json

Contains the same screening information in structured JSON format.

---

## Example Result

```text
Rank: 1
Candidate: candidate_01
Score: 89.93/100

Matched Skills:
Python, NLP, Machine Learning, LLM-Detected from the candidate resume

Missing Skills:
None-Detected against the job description

Experience:
Extracted from resume
```
Reasoning:
Generated using LLM or deterministic fallback reasoning
---

## Error Handling

The application is designed to continue processing candidates even when an individual LLM request fails.

For example, if the OpenAI API returns an insufficient quota error, the system automatically switches to deterministic fallback reasoning instead of terminating the complete screening process.

---

## Security

Sensitive configuration should be stored in `.env`.

Never commit:

```text
.env
```

or any API keys to GitHub.

The `.gitignore` file is configured to prevent accidental exposure of environment variables and other unnecessary files.

---

## Limitations

- Skill extraction is based on predefined skill aliases.
- Experience extraction depends on resume text patterns.
- Semantic similarity does not replace human recruitment judgment.
- LLM reasoning depends on API availability and quota.
- The system is intended as a screening assistant rather than a final hiring decision-maker.

---

## Future Improvements

Possible future enhancements include:

- Web-based recruiter dashboard
- Resume ranking visualization
- Advanced skill taxonomy
- Better experience and date extraction
- Database integration
- Recruiter feedback loop
- Configurable scoring weights
- Explainable candidate comparison
- Batch processing through a web interface
- Authentication and user management

---



```markdown
## Key Design Decision

The system uses a hybrid approach. Deterministic scoring is used for
skill matching, semantic similarity, experience, and education, while
LLM-based reasoning is used for qualitative candidate explanation.

If the LLM service is unavailable, the system automatically falls back
to deterministic reasoning so that candidate screening and ranking
continue without interruption.
## Author

Developed as an AI-powered resume screening and candidate ranking project.