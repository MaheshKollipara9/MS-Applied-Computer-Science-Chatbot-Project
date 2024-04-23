import streamlit as st

from feedback_form import display_feedback_form
from main import genai_engine
from PIL import Image
import os
import sqlite3

# Set title
#st.title("MS-Applied Computer Science Chatbot Project")

# Open the image
#image = Image.open('/content/chatbot.png')
image = Image.open('C:/Users/s559891/OneDrive - nwmissouri.edu/Documents/Z_GDP 02/GPT3/chatbot.png')

# Resize the image
image_resized = image.resize((150, 150))  # Adjust the size as needed

# Create a layout with two columns
col1, col2 = st.columns([2, 5])  # Adjust column ratios as needed

# Display the image in the first column
with col1:
    st.image(image_resized, use_column_width=True)

# Display the title in the second column
with col2:
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
    # Display user input
    st.text("User: " + prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = genai_engine(prompt)
    # Display bot response
    st.text("Assistant: " + response)
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

display_feedback_form()

# Save chat history to a SQLite database
def save_chat_history_to_db(messages):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()

    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (role TEXT, content TEXT)''')

    # Get the last index in the database
    c.execute("SELECT MAX(rowid) FROM chat_history")
    last_index = c.fetchone()[0]

    # Insert new messages into the table
    if last_index is None:
        start_index = 0
    else:
        start_index = last_index + 1

    for i in range(start_index, len(messages)):
        message = messages[i]
        c.execute("INSERT INTO chat_history VALUES (?, ?)", (message["role"], message["content"]))

    conn.commit()
    conn.close()

# Save chat history to SQLite database
save_chat_history_to_db(st.session_state.messages)