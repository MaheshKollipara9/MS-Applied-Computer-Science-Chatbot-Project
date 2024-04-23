import streamlit as st
import sqlite3
#Function to display the feedback form
def display_feedback_form():
    # Connect to SQLite database
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()

    # Create table for feedback data if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                 id INTEGER PRIMARY KEY,
                 name TEXT,
                 email TEXT,
                 feedback TEXT
                 )''')
    # Flag to indicate whether the feedback form button is clicked
    form_button_clicked = st.sidebar.button("Feedback Form")

    # Toggle the visibility of the feedback form
    if form_button_clicked:
        st.session_state.show_feedback_form = not st.session_state.get("show_feedback_form", False)

    if st.session_state.get("show_feedback_form", False):
        # Display feedback form in the sidebar
        st.sidebar.subheader("Feedback Form")
        
        # Initialize form fields
        if "feedback_form_data" not in st.session_state:
            st.session_state.feedback_form_data = {"name": "", "email": "", "feedback_text": ""}

        # Retrieve form data from session state
        feedback_form_data = st.session_state.feedback_form_data
        
        # Update form fields
        feedback_form_data["name"] = st.sidebar.text_input("Name", value=feedback_form_data["name"])
        feedback_form_data["email"] = st.sidebar.text_input("Email", value=feedback_form_data["email"])
        feedback_form_data["feedback_text"] = st.sidebar.text_area("Feedback", value=feedback_form_data["feedback_text"])
        
        submit_button = st.sidebar.button("Submit Feedback")

        # Submit feedback if all fields are filled
        if submit_button:
            if feedback_form_data["name"] and feedback_form_data["email"] and feedback_form_data["feedback_text"]:
                # Insert feedback data into the database
                c.execute("INSERT INTO feedback (name, email, feedback) VALUES (?, ?, ?)",
                          (feedback_form_data["name"], feedback_form_data["email"], feedback_form_data["feedback_text"]))
                conn.commit()
                st.sidebar.success("Thank you for your feedback!")
                
                # Clear all fields after successful submission
                st.session_state.feedback_form_data = {"name": "", "email": "", "feedback_text": ""}
            else:
                st.sidebar.error("Please fill in all the fields.")

    else:  # Close the feedback form if the button is clicked again or not shown
        st.session_state.feedback_form_data = {"name": "", "email": "", "feedback_text": ""}

    # Close database connection
    conn.close()

# Test the function
if __name__ == "__main__":
    display_feedback_form()
