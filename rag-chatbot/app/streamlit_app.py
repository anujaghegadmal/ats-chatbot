import streamlit as st
import requests

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"

# Function to register a new user
def register_user(user_id, user_name, user_password):
    url = f"{BASE_URL}/register"
    payload = {
        "user_id": user_id,
        "user_name": user_name,
        "user_password": user_password
    }
    response = requests.post(url, json=payload)
    return response.json()

# Function to login a user
def login_user(user_id, password):
    url = f"{BASE_URL}/login"
    params = {
        "user_id": user_id,
        "password": password
    }
    response = requests.post(url, params=params)
    return response.json()

# Function to create a new chat
def create_chat(user_id, access_token):
    url = f"{BASE_URL}/chats"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {"user_id": user_id}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Function to get all chats for a user
def get_all_chats(user_id, access_token):
    url = f"{BASE_URL}/chats/{user_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to add a message to a chat
def add_message_to_chat(chat_id, user_id, role, content, access_token):
    url = f"{BASE_URL}/chats/{chat_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "user_id": user_id,
        "role": role,
        "content": content
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Function to get all messages for a chat
def get_all_messages_for_chat(chat_id, access_token):
    url = f"{BASE_URL}/chats/{chat_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Streamlit login page
def login_page():
    st.title("Login")
    form = st.form("login_form")
    user_id = form.text_input("User ID")
    password = form.text_input("Password", type="password")
    submit_button = form.form_submit_button("Login")

    if submit_button:
        login_response = login_user(user_id, password)
        if "access_token" in login_response:
            st.session_state['access_token'] = login_response['access_token']
            st.session_state['user_id'] = user_id
            st.session_state['page'] = "chat"
            st.rerun()
        else:
            st.error("Login failed. Please check your credentials.")

    if st.button("Don't have an account? Sign Up"):
        st.session_state['page'] = "signup"
        st.rerun()

# Streamlit signup page
def signup_page():
    st.title("Sign Up")
    form = st.form("signup_form")
    new_user_id = form.text_input("New User ID")
    new_user_name = form.text_input("New User Name")
    new_password = form.text_input("New Password", type="password")
    register_button = form.form_submit_button("Register")

    if register_button:
        register_response = register_user(new_user_id, new_user_name, new_password)
        if "user_id" in register_response:
            st.success("Registration successful! Please login.")
            st.session_state['page'] = "login"
            st.rerun()
        else:
            st.error("Registration failed. Please try again.")

    if st.button("Already have an account? Login"):
        st.session_state['page'] = "login"
        st.rerun()

# Streamlit chat interface
def chat_interface():
    st.title("Chat Interface")
    user_id = st.session_state['user_id']
    access_token = st.session_state['access_token']

    with st.sidebar:
        st.header("Your Chats")
        chats = get_all_chats(user_id, access_token)
        if chats:
            for chat in chats:
                if st.button(f"Chat {chat['chat_id']}"):
                    st.session_state['selected_chat_id'] = chat['chat_id']
                    st.rerun()
        if st.button("Create New Chat"):
            chat_response = create_chat(user_id, access_token)
            if "chat_id" in chat_response:
                st.session_state['selected_chat_id'] = chat_response['chat_id']
                st.rerun()

    if 'selected_chat_id' in st.session_state:
        chat_id = st.session_state['selected_chat_id']
        messages = get_all_messages_for_chat(chat_id, access_token)
        if messages:
            for message in messages:
                if message['role'] == "user":
                    st.markdown(f"""
                    <div style='background-color: #333333; color: white; padding: 15px; border-radius: 10px; margin-bottom: 5px; width: 60%; text-align: right; margin-left: auto;'>
                    <b>User:</b> {message['content']}<br><i>{message['timestamp']}</i></div>
                    """, unsafe_allow_html=True)
                else:
                    
                    st.markdown(f"""
                    <div style='background-color: #333333; color: white; padding: 15px; border-radius: 10px; margin-bottom: 5px; width: 60%; text-align: left;'>
                    <b>Assistant:</b> {message['content']}<br><i>{message['timestamp']}</i></div>
                    """, unsafe_allow_html=True)
        
        new_message = st.text_input("Type your message:")
        if st.button("Send"):
            if new_message:
                add_message_response = add_message_to_chat(chat_id, user_id, "user", new_message, access_token)
                if "message_id" in add_message_response:
                    st.rerun()

def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = "login"

    if st.session_state['page'] == "login":
        login_page()
    elif st.session_state['page'] == "signup":
        signup_page()
    elif st.session_state['page'] == "chat":
        chat_interface()

if __name__ == "__main__":
    main()
