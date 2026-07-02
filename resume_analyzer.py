import streamlit as st
import pdfplumber
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords

# Initialize NLTK resource safely inside Streamlit
@st.cache_resource
def load_nltk():
    nltk.download('stopwords')
    return set(stopwords.words('english'))

STOPWORDS = load_nltk()

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded Streamlit file buffer."""
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text) 
    words = text.split()
    filtered_words = [word for word in words if word not in STOPWORDS]
    return " ".join(filtered_words)

# UI Architecture
st.set_page_config(page_title="Smart Resume Analyzer", page_icon="📄", layout="wide")

st.title("🚀 Smart Resume Analyzer with ATS Score")
st.subheader("Optimize your resume for applicant tracking systems instantly.")
st.markdown("---")

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.header("📥 Upload Documents")
    uploaded_file = st.file_uploader("Upload your Resume (PDF format only)", type=["pdf"])
    job_description = st.text_area("Paste the Target Job Description Here", height=250)

with col2:
    st.header("📊 ATS Analysis Results")
    
    if uploaded_file and job_description:
        with st.spinner("Analyzing your profile..."):
            # Execute processing pipelines
            resume_text = extract_text_from_pdf(uploaded_file)
            
            cleaned_resume = clean_text(resume_text)
            cleaned_jd = clean_text(job_description)
            
            resume_words = set(cleaned_resume.split())
            jd_words = set(cleaned_jd.split())
            
            matched_skills = resume_words.intersection(jd_words)
            missing_skills = jd_words.difference(resume_words)
            
            # Metric Calculation
            if len(jd_words) > 0:
                score = int((len(matched_skills) / len(jd_words)) * 100)
            else:
                score = 0
                
            # Visual Feedback Callouts
            if score >= 75:
                st.success(f"**Excellent Match Score: {score}%**")
            elif score >= 50:
                st.warning(f"**Average Match Score: {score}%** — Consider adding missing keywords.")
            else:
                st.error(f"**Low Match Score: {score}%** — Needs significant optimization.")
                
            st.progress(score / 100)
            
            # Structural breakdown using interactive elements
            tab1, tab2 = st.tabs(["✅ Matched Keywords", "⚠️ Missing Competencies"])
            
            with tab1:
                if matched_skills:
                    st.write(", ".join(list(matched_skills)))
                else:
                    st.info("No matching structural keywords located.")
                    
            with tab2:
                if missing_skills:
                    st.write(", ".join(list(missing_skills)))
                    # Prepare data frame for download functionality
                    report_df = pd.DataFrame(list(missing_skills), columns=["Missing Keywords"])
                    csv_data = report_df.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📥 Download Improvement Report",
                        data=csv_data,
                        file_name="ats_improvement_report.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("Brilliant! You've captured all fundamental keys.")
    else:
        st.info("Please complete both inputs (Upload PDF + Paste Job Description) to initialize processing.")