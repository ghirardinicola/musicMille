import streamlit as st
import requests
import json
from datetime import datetime

# Set page config
st.set_page_config(page_title="Chat API Client", page_icon="💬", layout="wide")

# API Configuration
API_URL = "http://localhost:8080/v1/chat/completions"
DEFAULT_MODEL = "test-model"

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False

# Function to call the chat API
def query_chat_api(messages, model=DEFAULT_MODEL, temperature=0.7):
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for 4XX/5XX errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling API: {str(e)}")
        return None

# Page title and description
st.title("Chat API Client")
st.markdown("Connect to your local FastAPI chat service to test its functionality.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    api_url = st.text_input("API URL", value=API_URL)
    model = st.text_input("Model", value=DEFAULT_MODEL)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    if st.button("Test Connection"):
        try:
            health_response = requests.get(api_url.replace("/v1/chat/completions", "/health"))
            if health_response.status_code == 200:
                st.success("Connection successful! API is healthy.")
            else:
                st.error(f"Connection failed with status code: {health_response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection failed: {str(e)}")
    
    # System message
    st.subheader("System Message")
    system_message = st.text_area(
        "Set the behavior of the assistant",
        value=st.session_state.messages[0]["content"],
        height=100
    )
    
    if st.button("Update System Message"):
        st.session_state.messages[0]["content"] = system_message
        st.success("System message updated!")
    
    st.subheader("Conversation")
    if st.button("Clear Conversation"):
        st.session_state.messages = [{"role": "system", "content": system_message}]
        st.session_state.conversation_started = False
        st.success("Conversation cleared!")

# Display chat messages
st.subheader("Chat")

# Display existing messages
for message in st.session_state.messages:
    if message["role"] != "system":  # Don't show system messages in the chat
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
# Handle user input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    with st.chat_message("user"):
        st.write(prompt)
    
    # Add message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_started = True
    
    # Call API with updated messages
    with st.spinner("Thinking..."):
        response_data = query_chat_api(
            st.session_state.messages,
            model=model,
            temperature=temperature
        )
    
    if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
        assistant_message = response_data["choices"][0]["message"]["content"]
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(assistant_message)
        
        # Add to message history
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    
# Display debug information in expander
with st.expander("Debug Information"):
    st.subheader("Current Messages")
    st.json(st.session_state.messages)
    
    st.subheader("Last API Response")
    if "response_data" in locals() and response_data:
        st.json(response_data)