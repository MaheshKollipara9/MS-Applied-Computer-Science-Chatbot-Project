import textwrap
import os
from langchain.document_loaders import TextLoader
import streamlit as st
from PIL import Image
import sqlite3
import faiss
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub

# Set Hugging Face API token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

# Load document
loader = TextLoader("data.txt", encoding='UTF-8')
document = loader.load()

# Preprocessing function
def wrap_text_preserve_newlines(text, width=110):
    lines = text.split('\n')
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
    wrapped_text = '\n'.join(wrapped_lines)
    return wrapped_text

# Text Splitting
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(document)

# Embedding
embeddings = HuggingFaceEmbeddings()
db = FAISS.from_documents(docs, embeddings)

# Initialize question-answering chain
llm = HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.8, "max_length": 512})
chain = load_qa_chain(llm, chain_type="stuff")
queryText = "Tell me about the course overview?"
docsResult = db.similarity_search(queryText)

def genai_engine(query):
    # Run the chain with the query
    response = chain.run(input_documents=docsResult, question=query)
    return response

# Streamlit app
st.set_page_config(page_title="MS-Applied Computer Science Chatbot Project")

# Display title
st.title("MS-Applied Computer Science Chatbot Project")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        st.text("User: " + message["content"])
    elif message["role"] == "assistant":
        st.text("Assistant: " + message["content"])

# React to user input
if prompt := st.text_input("Enter your query"):
    st.text("User: " + prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = genai_engine(prompt)
    st.text("Assistant: " + response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Function to display the feedback form
def display_feedback_form():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                 id INTEGER PRIMARY KEY,
                 name TEXT,
                 email TEXT,
                 feedback TEXT
                 )''')
    form_button_clicked = st.sidebar.button("Feedback Form")
    if form_button_clicked:
        st.session_state.show_feedback_form = not st.session_state.get("show_feedback_form", False)
    if st.session_state.get("show_feedback_form", False):
        st.sidebar.subheader("Feedback Form")
        if "feedback_form_data" not in st.session_state:
            st.session_state.feedback_form_data = {"name": "", "email": "", "feedback_text": ""}
        feedback_form_data = st.session_state.feedback_form_data
        feedback_form_data["name"] = st.sidebar.text_input("Name", value=feedback_form_data["name"])
        feedback_form_data["email"] = st.sidebar.text_input("Email", value=feedback_form_data["email"])
        feedback_form_data["feedback_text"] = st.sidebar.text_area("Feedback", value=feedback_form_data["feedback_text"])
        submit_button = st.sidebar.button("Submit Feedback")
        if submit_button:
            if feedback_form_data["name"] and feedback_form_data["email"] and feedback_form_data["feedback_text"]:
                c.execute("INSERT INTO feedback (name, email, feedback) VALUES (?, ?, ?)",
                          (feedback_form_data["name"], feedback_form_data["email"], feedback_form_data["feedback_text"]))
                conn.commit()
                st.sidebar.success("Thank you for your feedback!")
                st.session_state.feedback_form_data = {"name": "", "email": "", "feedback_text": ""}
            else:
                st.sidebar.error("Please fill in all the fields.")
    else:
        st.session_state.feedback_form_data = {"name": "", "email": "", "feedback_text": ""}
    conn.close()

# Display feedback form
if __name__ == "__main__":
    display_feedback_form()

# Save chat history to a SQLite database
def save_chat_history_to_db(messages):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (role TEXT, content TEXT)''')
    c.execute("SELECT MAX(rowid) FROM chat_history")
    last_index = c.fetchone()[0]
    if last_index is None:
        start_index = 0
    else:
        start_index = last_index + 1
    for i in range(start_index, len(messages)):
        message = messages[i]
        c.execute("INSERT INTO chat_history VALUES (?, ?)", (message["role"], message["content"]))
    conn.commit()
    conn.close()

save_chat_history_to_db(st.session_state.messages)
