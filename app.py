import streamlit as st
import fitz 
import requests
from google.cloud import bigquery
from langchain.llms import Gemini
from langchain.chains import FactChecker

# Initialize BigQuery client
client = bigquery.Client()

# Function to extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to call the Gemini API for summarization
def summarize_text_with_gemini(text):
    url = "https://api.gemini.com/v1/summarize"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["summary"]
    else:
        st.error("Failed to summarize the text")
        return None

# Function to call the Gemini API for Q&A generation
def generate_qa_with_gemini(text):
    url = "https://api.gemini.com/v1/generate_qa"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["qa_pairs"]
    else:
        st.error("Failed to generate Q&A pairs")
        return None

# Function to call the Gemini API for personalized learning recommendations and resources
def get_recommendations_with_gemini(user_profile):
    url = "https://api.gemini.com/v1/recommendations"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "profile": user_profile
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch recommendations")
        return None

# Function to perform fact-checking using BigQuery and LangChain
def fact_check_with_bigquery(text):
    query = f"""
    SELECT fact, source
    FROM `your_project.your_dataset.your_table`
    WHERE CONTAINS_SUBSTR('{text}', fact)
    """
    query_job = client.query(query)
    results = query_job.result()
    facts = []
    for row in results:
        facts.append({"fact": row.fact, "source": row.source})
    return facts

# Streamlit application
st.title("LearnSphere")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    st.write("Extracting text from PDF...")
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.write("Text extracted successfully!")

    st.subheader("Summary")
    summary = summarize_text_with_gemini(pdf_text)
    if summary:
        st.write(summary)

    st.subheader("Question and Answer")
    qa_pairs = generate_qa_with_gemini(pdf_text)
    if qa_pairs:
        for qa in qa_pairs:
            st.write(f"**Question:** {qa['question']}")
            st.write(f"**Answer:** {qa['answer']}")

    st.subheader("Take a Quiz")
    quiz_questions = [
        {"question": "What is the main topic of the document?", "options": ["Option 1", "Option 2", "Option 3"], "correct": 0},
        {"question": "Explain the key points.", "options": ["Option 1", "Option 2", "Option 3"], "correct": 1},
    ]

    user_answers = []
    for idx, q in enumerate(quiz_questions):
        st.write(q["question"])
        options = q["options"]
        user_answers.append(st.radio(f"Select an answer for question {idx + 1}", options, key=f"quiz_{idx}"))

    if st.button("Submit Quiz"):
        correct_answers = 0
        for idx, answer in enumerate(user_answers):
            if answer == quiz_questions[idx]["options"][quiz_questions[idx]["correct"]]:
                correct_answers += 1
        
        st.write(f"You got {correct_answers} out of {len(quiz_questions)} correct!")

        st.subheader("Tell us about your learning preferences")
        learning_preferences = st.multiselect(
            "Select your learning preferences",
            ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"]
        )

        user_profile = {
            "name": "John Doe",
            "quiz_score": correct_answers,
            "total_questions": len(quiz_questions),
            "learning_preferences": learning_preferences
        }

        recommendations = get_recommendations_with_gemini(user_profile)
        if recommendations:
            st.write("Based on your quiz results and preferences, we recommend:")
            for recommendation in recommendations.get("recommendations", []):
                st.write(f"- {recommendation['description']}")

            st.write("Here are some learning resources for you:")
            for resource in recommendations.get("resources", []):
                st.write(f"- [{resource['title']}]({resource['link']})")

    st.subheader("Fact Checker")
    if st.button("Check Facts"):
        facts = fact_check_with_bigquery(pdf_text)
        if facts:
            st.write("Found the following facts in the document:")
            for fact in facts:
                st.write(f"- **Fact:** {fact['fact']} | **Source:** {fact['source']}")
        else:
            st.write("No facts found in the document.")
