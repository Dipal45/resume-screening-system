import streamlit as st
import pandas as pd
from utils import (
    extract_text_from_pdf,
    clean_text,
    rank_resumes,
    get_matching_keywords,
    interpret_score
)

# Page config
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 AI Resume Screening System")
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Upload resumes and get intelligent ranking</p>', unsafe_allow_html=True)
st.markdown("### Match resumes with job descriptions using NLP")

# Input
job_desc = st.text_area(
    "🧾 Enter Job Description",
    height=500,
    placeholder="Paste full job description here..."
)

if job_desc:
    with st.expander("📖 View Full Job Description"):
        st.write(job_desc)

uploaded_files = st.file_uploader(
    "📂 Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("📂 Upload resumes to begin analysis")

# Button
if st.button("🚀 Rank Candidates"):

    status = st.empty()
    status.info("🔍 Analyzing resumes using NLP...")
    
    if not job_desc or not uploaded_files:
        st.warning("⚠️ Please provide job description and upload resumes.")

    else:
        resumes = []
        names = []

        with st.spinner("Processing resumes..."):

            for file in uploaded_files:
                text = extract_text_from_pdf(file)

                if not text:
                    st.warning(f"⚠️ Could not read {file.name}")
                    continue

                cleaned = clean_text(text)

                resumes.append(cleaned)
                names.append(file.name)

            job_clean = clean_text(job_desc)

            scores = rank_resumes(job_clean, resumes)

        # Combine results
        results = list(zip(names, scores, resumes))
        results = sorted(results, key=lambda x: x[1], reverse=True)

        if not results:
            st.error("❌ No valid resumes to process.")
            st.stop()

        status.empty()

        st.success("✅ Ranking Complete!")

        # 🏆 Best candidate
        best_name, best_score, _ = results[0]
        display_score = min(best_score, 0.95)

        st.success(f"🏆 Best Candidate: {best_name}")
        st.write(f"Score: `{display_score:.2f}` — {interpret_score(display_score)}")

        # 📊 Chart
        df = pd.DataFrame(
            [(name, score) for name, score, _ in results],
            columns=["Resume", "Score"]
        )

        csv = df.to_csv(index=False)

        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="resume_ranking.csv",
            mime="text/csv"
        )

        st.markdown("## 📊 Candidate Ranking Overview")
        st.bar_chart(df.set_index("Resume"))

        # 🥇 Top 3
        st.markdown("## 🏆 Top 3 Candidates")

        for i, (name, score, _) in enumerate(results[:3], start=1):
            display_score = min(score, 0.95)
            st.write(f"{i}. **{name}** — Score: `{display_score:.2f}`")

        # 📋 Detailed results
        st.markdown("---")
        st.subheader("📋 Detailed Analysis")

        for name, score, resume_text in results:
            display_score = min(score, 0.95)

            keywords = get_matching_keywords(job_clean, resume_text)

            st.write(f"### {name}")
            st.write(f"Score: `{display_score:.2f}` — {interpret_score(display_score)}")

            if keywords:
                st.write("Matching Skills:", ", ".join(keywords[:10]))
            else:
                st.write("No strong keyword match")

            st.write("---")

        # 📈 Summary
        st.info(f"📊 Total Resumes Processed: {len(results)}")

        st.markdown("---")
        st.caption("📌 Built using NLP (TF-IDF + Cosine Similarity) | Streamlit App")