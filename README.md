![Tests](https://github.com/7855043409/airesume-screening-system/actions/workflows/test.yml/badge.svg)
# AI Resume Screening Agent

An AI-powered resume screening and candidate ranking system that evaluates multiple candidate resumes against a given job description.

The system combines rule-based scoring, NLP-based semantic similarity, skill matching, experience analysis, education relevance, and optional LLM-based reasoning to generate a ranked list of candidates.

---

## Live Demo

Live Application:
https://airesume-screening-agent-kswakbsjeifp55f5tpbkpa.streamlit.app/

GitHub Repository:
https://github.com/7855043409/airesume-screening-agent

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
- Web-based Streamlit interface
- GitHub Actions workflow for automated testing

---

## System Architecture

Job Description
       |
       v
Resume Upload
       |
       v
Text Extraction
       |
       v
Resume Preprocessing
       |
       +----------------------+----------------------+
       |                                             |
       v                                             v
Skill Matching                              Semantic Similarity
       |                                             |
       +----------------------+----------------------+
                              |
                              v
                     Experience Analysis
                              |
                              v
                      Education Analysis
                              |
                              v
                       Candidate Scoring
                              |
                              v
                       Candidate Ranking
                              |
                       +------+------+
                       |             |
                       v             v
                 LLM Reasoning   Fallback Reasoning
                       |             |
                       +------+------+
                              |
                              v
                      Final Candidate Results
                              |
                       +------+------+
                       |             |
                       v             v
                      CSV           JSON
                    Report         Report

---

## How It Works

The application follows a complete resume screening pipeline.

### 1. Job Description

The recruiter enters the job description containing the required skills, experience, education, and other role requirements.

### 2. Resume Upload

Multiple candidate resumes can be uploaded through the Streamlit web interface.

Supported formats:

- TXT
- PDF
- DOCX

### 3. Text Extraction

The system extracts readable text from uploaded resumes.

### 4. Skill Matching

Required skills from the job description are compared against the skills identified in each candidate resume.

The system identifies:

- Matched skills
- Missing skills

### 5. Semantic Similarity

A Sentence Transformer embedding model is used to compare the meaning and context of the job description with each candidate resume.

This helps identify candidates whose overall background is semantically relevant to the role.

### 6. Experience Analysis

The system estimates relevant candidate experience from available resume information.

### 7. Education Evaluation

Candidate educational background is evaluated for relevance to the job requirements.

### 8. Candidate Scoring

The different evaluation factors are combined into an overall candidate score.

### 9. Candidate Ranking

Candidates are automatically ranked from the highest score to the lowest score.

### 10. Candidate Reasoning

The system generates reasoning explaining the candidate's strengths, alignment, and potential gaps.

When the OpenAI API is unavailable, deterministic fallback reasoning is used.

### 11. Report Generation

The system generates structured CSV and JSON reports.

---

## Scoring Methodology

Each candidate is evaluated using multiple factors.

### Skill Match

Measures how closely the candidate's skills match the skills required by the job description.

### Semantic Similarity

Measures contextual similarity between the job description and candidate resume using NLP embeddings.

### Experience Score

Evaluates the candidate's relevant professional experience.

### Education Score

Evaluates the relevance of the candidate's educational background.

### Overall Score

The individual evaluation factors are combined to generate an overall candidate score out of 100.

Candidates are then ranked according to their overall score.

---

## LLM-Based Reasoning

The application can optionally use the OpenAI API to generate natural-language reasoning for candidates.

Example:

The candidate demonstrates strong alignment with the required technical skills and has relevant experience in Python and NLP. The candidate is therefore a strong match for the role.

If the OpenAI API is unavailable because of quota, billing, network, or other API-related issues, the application automatically uses deterministic fallback reasoning.

This ensures that candidate scoring, ranking, and report generation can continue even when the LLM is unavailable.

---

## NLP and Semantic Similarity

The project uses NLP techniques to compare candidate resumes with job descriptions.

A sentence embedding model converts text into numerical representations.

The system then uses semantic similarity to identify how closely the candidate's overall profile matches the job requirements.

This provides a more meaningful comparison than simple keyword matching alone.

---

## Streamlit Web Application

The project includes a Streamlit-based web interface.

The interface allows users to:

1. Enter a job description
2. Upload multiple resumes
3. Start the screening process
4. View candidate rankings
5. View candidate scores
6. View candidate analysis
7. Download CSV results
8. Download JSON results

---

## Example Result

Example screening result:

============================================================
RESUME SCREENING RESULTS
============================================================

 1. candidate_01         90.04/100
 2. candidate_07         84.18/100
 3. candidate_02         82.52/100
 4. candidate_03         75.87/100
 5. candidate_09         75.73/100

Example top candidate analysis:

Candidate: candidate_01

Overall Score: 90.04/100
Semantic Similarity: 82.61/100
Skill Match: 100/100
Experience Score: 100/100
Education Score: 70/100

Estimated Experience: 1.8 years

Matched Skills:
AI, FastAPI, Generative AI, Git, GitHub, Machine Learning, NLP, Python, SQL

The exact results depend on the job description and resumes provided as input.

---

## Output Reports

After successful execution, the application generates:

outputs/
├── ranked_candidates.csv
└── ranked_candidates.json

### CSV Report

The CSV report contains structured candidate evaluation information such as:

rank
candidate
overall_score
skill_match
semantic_similarity
experience_score
education_score
estimated_experience
required_experience
matched_skills
missing_skills
reasoning

### JSON Report

The JSON report contains structured candidate evaluation data including:

- Candidate name
- Overall score
- Skill match
- Semantic similarity
- Experience score
- Education score
- Estimated experience
- Required experience
- Matched skills
- Missing skills
- Candidate reasoning
- Rank

---

## Project Structure

airesume-screening-agent/
|
├── .github/
|   └── workflows/
|       └── test.yml
|
├── data/
|   ├── job_description.txt
|   └── resumes/
|
├── outputs/
|   ├── ranked_candidates.csv
|   └── ranked_candidates.json
|
├── .env.example
├── .gitattributes
├── .gitignore
├── README.md
├── app.py
├── requirements.txt
└── streamlit_app.py

---

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Sentence Transformers
- NLP
- Semantic Similarity
- Machine Learning
- OpenAI API
- PyMuPDF
- python-docx
- python-dotenv
- Git
- GitHub
- GitHub Actions

---

## Installation

### 1. Clone the Repository

git clone https://github.com/7855043409/airesume-screening-agent.git

### 2. Navigate to the Project

cd airesume-screening-agent

### 3. Create a Virtual Environment

Windows:

python -m venv .venv

### 4. Activate the Virtual Environment

Windows:

.venv\Scripts\activate

### 5. Install Dependencies

pip install -r requirements.txt

---

## Environment Setup

Create a .env file in the project root directory.

OPENAI_API_KEY=your_openai_api_key_here

Do not upload the real API key to GitHub.

The .env file should remain excluded from version control through .gitignore.

For sharing the project, use the same placeholder inside .env.example:

OPENAI_API_KEY=your_openai_api_key_here

---

## Input Data

### Job Description

Place the job description inside:

data/job_description.txt

### Resumes

Place candidate resumes inside:

data/resumes/

Supported formats:

- .txt
- .pdf
- .docx

---

## Running the Command-Line Application

Run the following command from the project root:

python app.py --jd data/job_description.txt --resumes data/resumes --output outputs

The application will:

1. Load the job description
2. Load candidate resumes
3. Extract resume text
4. Extract relevant skills
5. Compare candidate skills with job requirements
6. Calculate semantic similarity
7. Estimate experience
8. Evaluate education relevance
9. Calculate the overall candidate score
10. Generate candidate reasoning
11. Rank candidates
12. Save CSV and JSON reports

---

## Running the Streamlit Application

Start the web interface with:

streamlit run streamlit_app.py

The application will open in the browser.

Users can then:

1. Paste the job description
2. Upload candidate resumes
3. Click Screen Resumes
4. View the candidate ranking
5. Review candidate analysis
6. Download CSV and JSON reports

---

## Deployment

The Streamlit application is deployed using Streamlit Community Cloud.

Live Demo:
https://airesume-screening-agent-kswakbsjeifp55f5tpbkpa.streamlit.app/

GitHub Repository:
https://github.com/7855043409/airesume-screening-agent

The application is connected to the GitHub repository so that updates can be deployed from the source code.

---

## GitHub Actions

The project includes a GitHub Actions workflow for automated testing.

Workflow location:

.github/workflows/test.yml

The workflow helps verify that the project continues to build and run correctly after repository changes.

---

## Fallback Behaviour

The application is designed to continue processing even when the OpenAI API is unavailable.

### When LLM is Available

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

### When LLM is Unavailable

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

This makes the core screening pipeline more reliable and less dependent on external LLM availability.

---

## Security

Sensitive information such as API keys must be stored using environment variables.

The following files and directories should be excluded from Git:

.env
.venv/
venv/
env/
__pycache__/
.cache/

Never commit:

- API keys
- Passwords
- Access tokens
- Private credentials
- Other sensitive information

---

## Limitations

- Resume quality affects the accuracy of extracted information.
- Experience and education scoring depend on the implemented screening logic.
- Semantic similarity measures contextual similarity but does not replace human evaluation.
- LLM reasoning depends on API availability and account quota.
- The system should be used as a recruitment assistance tool rather than an autonomous hiring decision-maker.
- Candidate rankings should be reviewed by a human recruiter before making final hiring decisions.

---

## Future Improvements

Possible future improvements include:

- Advanced skill taxonomy
- Improved experience extraction
- Better missing-skill detection
- Candidate comparison dashboard
- Interactive score visualization
- Recruiter dashboard
- Database integration
- Batch processing optimization
- Advanced LLM-based candidate analysis
- Human-in-the-loop recruiter feedback
- Automated interview recommendation
- Explainable AI scoring
- Authentication and recruiter access control

---

## Project Goal

The goal of this project is to demonstrate how NLP, semantic similarity, rule-based scoring, and optional LLM reasoning can be combined to build an automated resume screening and candidate ranking system.

The project focuses on making resume screening faster, more structured, and easier to analyze while keeping human decision-making in the final hiring process.

---

## Author

Durga Raula

GitHub:
https://github.com/7855043409/airesume-screening-agent

Live Demo:
https://airesume-screening-agent-kswakbsjeifp55f5tpbkpa.streamlit.app/

---

## License

This project is intended for educational, demonstration, and portfolio purposes.

## Tradeoff Notes

### Approach
The system combines semantic similarity, skill matching, experience evaluation, education scoring, and rule-based reasoning to rank candidates against a given job description.

### Why this approach
- Semantic similarity helps identify candidates whose resumes are relevant even when exact keywords differ.
- Skill matching provides an interpretable measure of required skill coverage.
- Experience and education scores add structured candidate evaluation.
- Rule-based reasoning keeps the screening process transparent and reproducible.
- Streamlit provides a simple interface for end-to-end demonstration.

### Tradeoffs
- The current system prioritizes explainability and fast execution over using a large, expensive LLM for every candidate.
- Resume parsing and scoring are primarily rule-based, so unusual resume formats or highly implicit skills may not be detected perfectly.
- Semantic similarity depends on the quality of the underlying NLP embeddings.
- The current experience extraction is approximate and may not handle every resume wording pattern.

### Future Improvements
With more development time, I would:
- Improve PDF/DOCX parsing for complex resume layouts.
- Add stronger skill normalization and synonym detection.
- Use an LLM-based reasoning layer for deeper candidate analysis.
- Add configurable scoring weights for different job requirements.
- Add automated evaluation using labeled resume-job-description datasets.
- Improve handling of missing or ambiguous information.
- Add authentication and persistent storage for production deployment.
