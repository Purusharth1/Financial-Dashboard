"""FinanceGPT - A Streamlit-based AI Financial Assistant Dashboard."""
import datetime
import uuid

import requests
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="FinanceGPT",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

FIRST_USER_MESSAGE_COUNT = 2
MAX_TITLE_LENGTH = 20
# Clean, high-contrast CSS with clear readability
st.markdown("""
<style>
    /* Base styles with good contrast */
    body {
        background-color: #ffffff;
        color: #333333;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: #ffffff;
    }

    /* Headers */
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #2980b9;
        margin-top: 5px;
    }

    .sub-header {
        font-size: 14px;
        color: #7f8c8d;
        margin-top: -5px;
    }

    /* Chat history items */
    .chat-item {
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 5px;
        color: #ffffff;
    }

    /* Message styling */
    .ai-message {
        background-color: #d4e6f1;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 15px;
        color: #2c3e50;
        max-width: 70%;
        border-left: 4px solid #3498db;
    }

    .user-message {
        background-color: #eaeded;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 15px;
        margin-left: auto;
        color: #2c3e50;
        max-width: 50%;
        border-right: 4px solid #95a5a6;
    }

    /* Loading indicator */
    .loading-message {
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 15px;
    }

    /* Buttons and controls */
    .stButton>button {
        border-radius: 4px;
        font-weight: 500;
    }

    /* Header container */
    .header-container {
        padding: 15px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
    }

    /* Suggestions area */
    .suggestions-container {
        position: fixed;
        bottom: 80px;
        left: 300px;
        right: 20px;
        padding: 0 20px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
if "api_type" not in st.session_state:
    st.session_state.api_type = "FastAPI"

# API URLs
FASTAPI_URL = "http://localhost:8000/query"
BENTOML_URL = "http://localhost:3000/query"

SUCCESS_STATUS_CODE = 200

def get_api_url() -> str:
    """Get the current API URL based on the selected API type."""
    return FASTAPI_URL if st.session_state.api_type == "FastAPI" else BENTOML_URL

# Session state initialization
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if "chats" not in st.session_state:
    st.session_state.chats = {
        st.session_state.current_chat_id: {
            "timezone-aware title": f"""New Chat
            {datetime.datetime.now(datetime.UTC).strftime('%H:%M')}""",
            "messages": [
                {"role": "assistant", "content": (
                    "Welcome to your Financial Dashboard! How can I help you today? "
                    "Try asking about stocks, spending analysis, or investment advice."
                )},
            ],
        },
    }

if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

# Function to query the API
def query_financial_api(prompt: str) -> str:
    """Send a query to the financial API and get the response."""
    api_url = get_api_url()
    try:
        # Debug information
        st.session_state.last_request_url = api_url
        response = requests.post(
            api_url,
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"},
            timeout=10000,
        )
        # Store the response for debugging
        st.session_state.last_response = {
            "status_code": response.status_code,
            "text": (
                response.text
                if response.status_code != SUCCESS_STATUS_CODE
                else "Success"
            ),
        }

        if response.status_code == SUCCESS_STATUS_CODE:
            return response.json()["response"]

        # Handle non-200 status codes
        error_message = f"API Error: {response.status_code} - {response.text}"
        st.error(error_message)
        exception_message = f"API Error: Status code {response.status_code}"
        raise ValueError(exception_message)

    except requests.exceptions.RequestException as e:
        error_message = f"Connection Error: {e}"
        st.error(error_message)
        return """Sorry, I couldn't connect to the financial API.
        Please check if the server is running."""

def create_new_chat() -> None:
    """Create a new chat and set it as the current chat."""
    new_chat_id = str(uuid.uuid4())
    st.session_state.chats[new_chat_id] = {
        "timezone-aware title": f"""New Chat
        {datetime.datetime.now(datetime.UTC).strftime('%H:%M')}""",
        "messages": [
            {"role": "assistant", "content": (
                "Welcome to your Financial Dashboard! How can I help you today? "
                "Try asking about stocks, spending analysis, or investment advice."
            )},
        ],
    }
    st.session_state.current_chat_id = new_chat_id
    st.session_state.waiting_for_response = False

def switch_to_chat(chat_id: str) -> None:
    """Switch to an existing chat."""
    st.session_state.current_chat_id = chat_id
    st.session_state.waiting_for_response = False

# Sidebar
with st.sidebar:
    # Logo and title
    st.title("FinanceGPT")
    st.markdown("Your AI Financial Assistant")
    st.markdown("---")

    # New Chat Button
    if st.button("+ New Chat", key="new_chat", use_container_width=True):
        create_new_chat()

    st.markdown("---")

    # Chat History
    st.subheader("Chat History")
    for chat_id, chat_data in st.session_state.chats.items():
        is_active = chat_id == st.session_state.current_chat_id
        if st.button(
            chat_data["timezone-aware title"],
            key=f"chat_{chat_id}",
            use_container_width=True,
            type="secondary" if is_active else "primary",
        ):
            switch_to_chat(chat_id)

    st.markdown("---")

    # API Type Selection
    st.subheader("Backend Selection")
    api_type = st.radio(
        "Choose API Backend:",
        ["FastAPI", "BentoML"],
        index=0 if st.session_state.api_type == "FastAPI" else 1,
        key="api_type_radio",
    )
    st.session_state.api_type = api_type

# Main content
st.header("Financial Assistant")
st.write(f"**Current Backend:** {st.session_state.api_type}")

# Get current chat messages
current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

# Chat container
container = st.container(border=True)
with container:
    # Display chat messages
    for message in messages:
        if message["role"] == "assistant":
            st.markdown(
                f'<div class="ai-message">{message["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="user-message">{message["content"]}</div>',
                unsafe_allow_html=True,
            )

    # Show loading message if waiting for response
    if st.session_state.waiting_for_response:
        st.info("FinanceGPT is thinking...")

# Suggested prompts (clickable)
st.markdown("### Suggested Questions")
col1, col2, col3 = st.columns([1, 1, 1])

# Function to handle suggestion clicks
def handle_suggestion(suggestion: str) -> None:
    """Handle user interaction with suggested prompts."""
    # Add user message immediately
    st.session_state.chats[st.session_state.current_chat_id]["messages"].append(
        {"role": "user", "content": suggestion},
    )

    # Update chat title if it's the first user message
    if (
        len(st.session_state.chats[st.session_state.current_chat_id]["messages"])
        == FIRST_USER_MESSAGE_COUNT
    ):
        st.session_state.chats[st.session_state.current_chat_id][
            "timezone-aware title"
        ] = (
            suggestion[:MAX_TITLE_LENGTH] + "..."
            if len(suggestion) > MAX_TITLE_LENGTH
            else suggestion
        )

    # Set waiting state
    st.session_state.waiting_for_response = True
    st.rerun()

with col1:
    if st.button("Check crypto prices", key="crypto_button", use_container_width=True):
        handle_suggestion("Check crypto prices")

with col2:
    if st.button(
        "Analyze my spending",
        key="spending_button",
        use_container_width=True,
    ):
        handle_suggestion("Analyze my spending")

with col3:
    if st.button(
        "Investment recommendations",
        key="investment_button",
        use_container_width=True,
    ):
        handle_suggestion("Investment recommendations")

# Chat input
prompt = st.chat_input("Ask a financial question...")
if prompt:
    # Add user message immediately
    st.session_state.chats[st.session_state.current_chat_id]["messages"].append(
        {"role": "user", "content": prompt},
    )

    # Update chat title if it's the first user message
    if (
        len(st.session_state.chats[st.session_state.current_chat_id]["messages"])
        == FIRST_USER_MESSAGE_COUNT
    ):
        st.session_state.chats[st.session_state.current_chat_id][
            "timezone-aware title"
        ] = (
            prompt[:MAX_TITLE_LENGTH] + "..."
            if len(prompt) > MAX_TITLE_LENGTH
            else prompt
        )

    # Set waiting state
    st.session_state.waiting_for_response = True
    st.rerun()

# Process API request if waiting for response
if st.session_state.waiting_for_response:
    # Get the last user message
    last_user_message = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        None,
    )

    if last_user_message:
        # Query the API
        response = query_financial_api(last_user_message)

        # Add response to chat
        st.session_state.chats[st.session_state.current_chat_id]["messages"].append(
            {"role": "assistant", "content": response},
        )

        # Reset waiting state
        st.session_state.waiting_for_response = False
        st.rerun()
