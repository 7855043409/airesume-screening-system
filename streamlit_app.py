import streamlit as st
import tempfile
import subprocess
import sys
from pathlib import Path
import pandas as pd


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume Screening Agent",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📄 AI Resume Screening Agent")

st.write(
    "AI-powered resume screening and candidate ranking system "
    "using NLP, semantic similarity, skill matching, and LLM reasoning."
)

st.divider()


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.subheader("📋 Job Description")

job_description = st.text_area(
    "Paste the job description here:",
    height=250,
    placeholder="Paste the complete job description here..."
)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.subheader("📂 Upload Resumes")

uploaded_resumes = st.file_uploader(
    "Upload candidate resumes",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_resumes:

    st.success(
        f"✅ {len(uploaded_resumes)} resume(s) uploaded successfully."
    )

    with st.expander("📄 View uploaded resumes"):

        for resume in uploaded_resumes:

            st.write(f"• {resume.name}")


# ============================================================
# SCREEN RESUMES
# ============================================================

if st.button("🚀 Screen Resumes", type="primary"):

    if not job_description.strip():

        st.warning("⚠️ Please enter a job description.")

    elif not uploaded_resumes:

        st.warning("⚠️ Please upload at least one resume.")

    else:

        with st.spinner(
            "🔍 Screening resumes using the AI resume screening engine..."
        ):

            try:

                # ====================================================
                # TEMPORARY WORKING DIRECTORY
                # ====================================================

                with tempfile.TemporaryDirectory() as temp_dir:

                    temp_path = Path(temp_dir)

                    jd_path = temp_path / "job_description.txt"

                    resumes_path = temp_path / "resumes"

                    output_path = temp_path / "outputs"

                    resumes_path.mkdir()

                    output_path.mkdir()


                    # ====================================================
                    # SAVE JOB DESCRIPTION
                    # ====================================================

                    jd_path.write_text(
                        job_description,
                        encoding="utf-8"
                    )


                    # ====================================================
                    # SAVE UPLOADED RESUMES
                    # ====================================================

                    for uploaded_file in uploaded_resumes:

                        file_path = resumes_path / uploaded_file.name

                        file_path.write_bytes(
                            uploaded_file.getbuffer()
                        )


                    # ====================================================
                    # LOCATE EXISTING SCREENING ENGINE
                    # ====================================================

                    project_root = Path(__file__).resolve().parent

                    app_path = project_root / "app.py"

                    if not app_path.exists():

                        st.error(
                            "❌ app.py was not found in the project directory."
                        )

                        st.stop()


                    # ====================================================
                    # RUN EXISTING SCREENING ENGINE
                    # ====================================================

                    command = [
                        sys.executable,
                        str(app_path),
                        "--jd",
                        str(jd_path),
                        "--resumes",
                        str(resumes_path),
                        "--output",
                        str(output_path)
                    ]

                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace"
                    )


                    # ====================================================
                    # ENGINE LOGS
                    # ====================================================

                    if result.stdout:

                        with st.expander("🔎 Screening Engine Logs"):

                            st.code(
                                result.stdout,
                                language="text"
                            )


                    # ====================================================
                    # HANDLE ERRORS
                    # ====================================================

                    if result.returncode != 0:

                        st.error(
                            "❌ Resume screening failed."
                        )

                        if result.stderr:

                            with st.expander("❌ Error Details"):

                                st.code(
                                    result.stderr,
                                    language="text"
                                )

                        st.stop()


                    # ====================================================
                    # RESULT FILES
                    # ====================================================

                    csv_file = output_path / "ranked_candidates.csv"

                    json_file = output_path / "ranked_candidates.json"


                    # ====================================================
                    # DISPLAY CSV RESULTS
                    # ====================================================

                    if csv_file.exists():

                        df = pd.read_csv(csv_file)

                        st.success(
                            "✅ Resume screening completed successfully!"
                        )

                        st.divider()

                        st.subheader("🏆 Candidate Ranking")

                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )


                        # ====================================================
                        # TOP CANDIDATE
                        # ====================================================

                        if len(df) > 0:

                            top_candidate = df.iloc[0]

                            st.divider()

                            st.subheader("🥇 Top Candidate")

                            col1, col2, col3 = st.columns(3)


                            # ------------------------------------------------
                            # Candidate Name
                            # ------------------------------------------------

                            with col1:

                                candidate_name = top_candidate.get(
                                    "candidate",
                                    "N/A"
                                )

                                st.metric(
                                    "Candidate",
                                    str(candidate_name)
                                )


                            # ------------------------------------------------
                            # Overall Score
                            # ------------------------------------------------

                            with col2:

                                # FIX:
                                # CSV uses overall_score, not score

                                score = top_candidate.get(
                                    "overall_score",
                                    top_candidate.get("score", 0)
                                )

                                try:

                                    score = float(score)

                                except (ValueError, TypeError):

                                    score = 0.0

                                st.metric(
                                    "Overall Score",
                                    f"{score:.2f}/100"
                                )


                            # ------------------------------------------------
                            # Rank
                            # ------------------------------------------------

                            with col3:

                                rank = top_candidate.get(
                                    "rank",
                                    1
                                )

                                st.metric(
                                    "Rank",
                                    str(rank)
                                )


                            # ====================================================
                            # TOP CANDIDATE ANALYSIS
                            # ====================================================

                            with st.expander(
                                "🔍 View Top Candidate Analysis"
                            ):

                                for column in df.columns:

                                    value = top_candidate[column]

                                    st.write(
                                        f"**{column.replace('_', ' ').title()}:**"
                                    )

                                    st.write(value)


                        # ====================================================
                        # DOWNLOAD RESULTS
                        # ====================================================

                        st.divider()

                        st.subheader("📥 Download Results")


                        # ------------------------------------------------
                        # CSV
                        # ------------------------------------------------

                        csv_data = df.to_csv(index=False)

                        st.download_button(
                            label="⬇️ Download CSV Report",
                            data=csv_data,
                            file_name="ranked_candidates.csv",
                            mime="text/csv"
                        )


                    else:

                        st.warning(
                            "⚠️ Screening completed, but the CSV result "
                            "file was not generated."
                        )


                    # ====================================================
                    # JSON DOWNLOAD
                    # ====================================================

                    if json_file.exists():

                        try:

                            json_data = json_file.read_text(
                                encoding="utf-8"
                            )

                            st.download_button(
                                label="⬇️ Download JSON Report",
                                data=json_data,
                                file_name="ranked_candidates.json",
                                mime="application/json"
                            )

                        except Exception as e:

                            st.warning(
                                f"Could not load JSON report: {e}"
                            )


                    # ====================================================
                    # ENGINE WARNINGS
                    # ====================================================

                    if result.stderr:

                        with st.expander("⚠️ Engine Warnings"):

                            st.code(
                                result.stderr,
                                language="text"
                            )


            except Exception as e:

                st.error(
                    f"❌ Unexpected error: {str(e)}"
                )

                st.info(
                    "Please check that app.py and all required "
                    "dependencies are installed correctly."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Resume Screening Agent | NLP + Semantic Similarity + "
    "Skill Matching + LLM Reasoning"
)