import streamlit as st
import pandas as pd
import tempfile, os, io, datetime
from src.parser import extract_text_from_pdf_bytes
from src.matcher import load_skill_list, extract_candidate_skills, match_skills, suggest_bullets, build_report_md

st.set_page_config(page_title="AI-Powered Resume Analyzer", layout="wide")
st.title("AI-Powered Resume Analyzer")

with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. Upload a **resume PDF**.

    2. Paste a **job description**.

    3. Click **Analyze**.

    4. Review **Matched/Missing skills** and **Score**.

    5. **Download report** (Markdown).

    """)
    st.caption("Tip: Edit `skills/skill_list.json` to tune detection.")

col1, col2 = st.columns([1, 2], gap="large")

# State
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

with col1:
    st.subheader("Inputs")
    uploaded_file = st.file_uploader("Upload resume PDF", type=["pdf"])

    # Sample JD presets
    jd_presets = {
        "— choose a sample —": "",
        "ML Engineer (product)": "We seek an ML Engineer with Python, Scikit-learn, PyTorch/TensorFlow, data pipelines (Pandas), Docker, AWS, and experience deploying REST APIs. Knowledge of NLP/transformers and CI/CD is a plus.",
        "Data Scientist": "Looking for a Data Scientist skilled in Python, SQL, Pandas, NumPy, Scikit-learn, statistics, A/B testing, visualization (Matplotlib/Seaborn), and cloud (GCP/AWS). Experience with MLflow, Airflow is preferred.",
        "Backend + ML": "Hiring a backend engineer with experience in Python, FastAPI/Flask, REST API design, Docker, PostgreSQL, Redis, AWS, and exposure to ML models with Scikit-learn or TensorFlow."
    }
    jd_choice = st.selectbox("Use a sample JD (optional)", list(jd_presets.keys()), index=0)
    jd_text = st.text_area("Paste job description", value=jd_presets[jd_choice], height=180)

    analyze = st.button("Analyze", type="primary", use_container_width=True)

with col2:
    st.subheader("Results")

    if uploaded_file is not None:
        # Read bytes once
        file_bytes = uploaded_file.getvalue()
        with st.spinner("Extracting text from PDF..."):
            try:
                resume_text = extract_text_from_pdf_bytes(file_bytes)
                st.session_state.resume_text = resume_text
            except Exception as e:
                st.error(f"Failed to parse PDF: {e}")
                st.stop()

        with st.expander("Preview resume text (first 800 chars)"):
            preview = st.session_state.resume_text[:800]
            if len(st.session_state.resume_text) > 800:
                preview += "..."
            st.code(preview)

    if analyze:
        if not uploaded_file:
            st.warning("Please upload a resume PDF.")
            st.stop()
        if not jd_text.strip():
            st.warning("Please paste a job description or pick a sample.")
            st.stop()

        skills = load_skill_list()
        resume_text = st.session_state.resume_text

        with st.spinner("Analyzing skills..."):
            resume_skills = extract_candidate_skills(resume_text, skills)
            jd_skills = extract_candidate_skills(jd_text, skills)
            res = match_skills(resume_skills, jd_skills)
            st.session_state.resume_skills = resume_skills

        m1, m2, m3 = st.columns(3)
        m1.metric("Match score", f"{res['score']}%")
        m2.metric("Resume skills", len(resume_skills))
        m3.metric("JD skills", len(jd_skills))

        st.markdown("### Matched skills")
        if res["matched"]:
            st.write(", ".join(f"`{s}`" for s in res["matched"]))
        else:
            st.write("None")

        st.markdown("### Missing skills")
        if res["missing"]:
            for s in res["missing"]:
                st.markdown(f"- ❌ **{s}**")
        else:
            st.success("No missing skills — great match!")

        with st.expander("Extra / resume-only skills"):
            if res["extra"]:
                st.write(", ".join(f"`{s}`" for s in res["extra"]))
            else:
                st.write("—")

        # Suggestions & report
        st.markdown("### Suggestions")
        bullets = suggest_bullets(res["missing"])
        if bullets:
            for b in bullets:
                st.markdown(f"- {b}")
        else:
            st.write("Looks solid — consider quantifying impact in your bullets!")

        report_md = build_report_md(
            score=res["score"],
            matched=res["matched"],
            missing=res["missing"],
            extra=res["extra"],
            bullets=bullets,
            jd_excerpt=jd_text[:400]
        )
        st.download_button(
            label="Download Markdown report",
            data=report_md.encode("utf-8"),
            file_name=f"resume_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
