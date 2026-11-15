import sys
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from assistant import answer_question

st.set_page_config(
    page_title="Ask Your Floor Plan",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Ask Your Floor Plan")
st.write(
    "Ask questions about rooms, doors, windows and floor plans. "
    "Answers are grounded in the SQLite database."
)

st.info(
    "Example questions: How many rooms does plan 12 have? "
    "What is the largest room in plan 7? "
    "Which plans have more than 3 doors?"
)

with st.form("question_form"):
    question = st.text_input(
        "Enter your question",
        placeholder="e.g. Which room in plan 4 has no windows?"
    )
    submitted = st.form_submit_button("Ask Question")

if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing your question..."):
            try:
                result = answer_question(question.strip())

                st.subheader("Answer")
                st.success(result["answer"])

                st.subheader("SQL Query")
                st.code(result["sql"], language="sql")

                st.subheader("Database Evidence")
                st.code(repr(result["evidence"]), language="python")

            except Exception as error:
                st.error(f"An error occurred: {error}")

st.divider()
st.caption(
    "Ashian Tech Intern Assignment | "
    "SQLite • Python • Gemini • Streamlit"
)
