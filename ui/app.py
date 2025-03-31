"""FinanceGPT - A Streamlit-based AI Financial Assistant Dashboard."""
import requests
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="FinanceGPT",
    page_icon="ð � � °",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced Custom CSS
st.markdown("""
<style>
    body {
        background-color: #f9fafb;
    }
    .sidebar .sidebar-content {
        background-color: #1a202c;
        color: white;
        padding: 20px;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .main {
        background-color: #ffffff;
        border-radius: 0;
        padding: 0;
        margin: 0;
        height: 100vh;
    }
    .main-header {
        font-size: 22px;
        font-weight: bold;
        color: #1a56db;
        margin-top: 5px;
    }
    .sub-header {
        font-size: 12px;
        color: #6b7280;
        margin-top: -5px;
    }
    .nav-item {
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        color: white;
    }
    .nav-item-active {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
    }
    .nav-circle {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 15px;
        display: inline-block;
    }
    .nav-circle-active {
        background-color: white;
    }
    .nav-circle-inactive {
        background-color: #4b5563;
    }
    .sidebar-footer {
        color: white;
        margin-top: 240px;
    }
    .chat-container {
        background-color: #f9fafb;
        border-radius: 10px;
        padding: 20px;
        height: calc(100vh - 200px);
        overflow-y: auto;
        position: relative;
        margin: 0;
    }
    .ai-message {
        background-color: #dbeafe;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        color: #1e40af;
        max-width: 70%;
    }
    .user-message {
        background-color: #e5e7eb;
        border-radius: 20px;
        padding: 10px;
        margin-bottom: 15px;
        margin-left: auto;
        color: #374151;
        max-width: 50%;
    }
    .suggestion-pill {
        background-color: #e5e7eb;
        border-radius: 15px;
        padding: 5px 15px;
        color: #4b5563;
        border: 1px solid #d1d5db;
        cursor: pointer;
        text-align: center;
        width: 100%;
    }
    .header-container {
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
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

# API URLs - Updated to ensure they are correct
FASTAPI_URL = "http://localhost:8000/query"  # Changed from 127.0.0.1 to localhost
BENTOML_URL = "http://localhost:3000/query"  # Changed from 127.0.0.1 to localhost

SUCCESS_STATUS_CODE = 200  # Define a constant for the magic number 200

def get_api_url() -> str:
    """Get the current API URL based on the selected API type."""
    return FASTAPI_URL if st.session_state.api_type == "FastAPI" else BENTOML_URL

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": (
            "Welcome to your Financial Dashboard! How can I help you today? "
            "*Try asking about stocks, spending analysis, or investment advice.*"
        )},
    ]

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
            timeout=100,  # Reduced timeout for faster error feedback
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

# Sidebar
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(
            '<div style="background-color: #1a56db; border-radius: 8px; '
            'width: 40px; height: 40px; display: flex; justify-content: center; '
            'align-items: center; color: white; font-weight: bold;">F</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<p class="main-header">FinanceGPT</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub-header">Your AI Financial Assistant</p>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    # API Type Selection
    st.subheader("Backend Selection")
    api_type = st.radio(
        "Choose API Backend:",
        ["FastAPI", "BentoML"],
        index=0,
        key="api_type_radio",
    )
    st.session_state.api_type = api_type
    st.markdown("---")
    nav_items = [
        ("Dashboard", True),
        ("Stock Analysis", False),
        ("Crypto Tracker", False),
        ("Spending Insights", False),
        ("Investment Advice", False),
        ("History", False),
    ]
    for item, is_active in nav_items:
        circle_class = "nav-circle-active" if is_active else "nav-circle-inactive"
        item_class = "nav-item-active" if is_active else ""
        st.markdown(
            f'<div class="nav-item {item_class}">'
            f'<span class="nav-circle {circle_class}"></span>{item}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("""
    <div class="sidebar-footer">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #dbeafe; border-radius: 50%; width: 50px;
                height: 50px;display:flex;justify-content:center;align-items:center;
                margin-right: 10px;">
                <span style="color: #1a56db;font-weight:bold;font-size: 20px;">JD</span>
            </div>
            <div>
                <div style="font-weight: bold; color: white;">John Doe</div>
                <div style="color: #6b7280; font-size: 12px;">Premium Plan</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<div class="header-container">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown(
        '<h1 style="font-size: 22px; font-weight: bold; color: #1a56db;">'
        'Financial Assistant</h1>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="tools-indicator"><span class="green-dot"></span>'
        f'Backend: {st.session_state.api_type}</div>',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# Chat container
container = st.container(border=True)
with container:
    # Display chat messages
    for message in st.session_state.messages:
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

# Suggested prompts (clickable)
st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

# Function to handle suggestion clicks
def handle_suggestion(suggestion: str) -> None:
    """Handle user interaction with suggested prompts.

    Args:
        suggestion (str): The suggested prompt clicked by the user.

    """
    st.session_state.messages.append({"role": "user", "content": suggestion})
    response = query_financial_api(suggestion)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

with col1:
    if st.button("Check crypto prices", key="crypto_button"):
        handle_suggestion("Check crypto prices")

with col2:
    if st.button("Analyze my spending", key="spending_button"):
        handle_suggestion("Analyze my spending")

with col3:
    if st.button("Investment recommendations", key="investment_button"):
        handle_suggestion("Investment recommendations")

st.markdown("</div>", unsafe_allow_html=True)

# Chat input
prompt = st.chat_input("Ask a financial question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Query the API and get response
    response = query_financial_api(prompt)
    # Add response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
