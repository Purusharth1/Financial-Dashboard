import streamlit as st
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="FinanceGPT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .tools-indicator {
        background-color: #e5e7eb;
        border-radius: 15px;
        padding: 5px 15px;
        color: #374151;
        font-size: 12px;
        float: right;
    }
    .green-dot {
        height: 8px;
        width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
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

# Session state initialization
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to your Financial Dashboard! How can I help you today? *Try asking about stocks, spending analysis, or investment advice.*"}
    ]
if 'portfolio_value' not in st.session_state:
    st.session_state.portfolio_value = 124567
    st.session_state.portfolio_growth = 8.2
    st.session_state.portfolio_history = [110000, 112000, 118000, 116000, 121000, 123000, 124567]
    st.session_state.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    st.session_state.asset_allocation = {"Stocks": 45, "Bonds": 25, "Real Estate": 20, "Crypto": 10}

# Chart functions
def create_portfolio_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.months, y=st.session_state.portfolio_history, mode='lines+markers', line=dict(color='#1a56db', width=2), fill='tozeroy', fillcolor='rgba(219, 234, 254, 0.5)'))
    fig.update_layout(title=f"Portfolio Value: ${st.session_state.portfolio_value:,} (+{st.session_state.portfolio_growth}% YTD)", title_font=dict(size=12, color='#4b5563'), paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=20, r=20, t=30, b=20), height=180, xaxis=dict(showgrid=False, title=None), yaxis=dict(title=None, tickprefix='$', ticksuffix='k', showgrid=True, gridcolor='#e5e7eb'))
    return fig

def create_asset_allocation_chart():
    labels = list(st.session_state.asset_allocation.keys())
    values = list(st.session_state.asset_allocation.values())
    colors = ['#1a56db', '#2563eb', '#3b82f6', '#60a5fa']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker=dict(colors=colors))])
    fig.update_layout(title="Asset Allocation", title_font=dict(size=12, color='#4b5563'), legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1, font=dict(size=14, color='#374151')), margin=dict(l=20, r=120, t=30, b=20), height=200)
    fig.update_traces(textinfo='percent', textposition='inside')
    return fig

# Sidebar
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div style="background-color: #1a56db; border-radius: 8px; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">F</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<p class="main-header">FinanceGPT</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Your AI Financial Assistant</p>', unsafe_allow_html=True)
    st.markdown("---")
    nav_items = [("Dashboard", True), ("Stock Analysis", False), ("Crypto Tracker", False), ("Spending Insights", False), ("Investment Advice", False), ("History", False)]
    for item, is_active in nav_items:
        circle_class = "nav-circle-active" if is_active else "nav-circle-inactive"
        item_class = "nav-item-active" if is_active else ""
        st.markdown(f'<div class="nav-item {item_class}"><span class="nav-circle {circle_class}"></span>{item}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-footer">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #dbeafe; border-radius: 50%; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; margin-right: 10px;">
                <span style="color: #1a56db; font-weight: bold; font-size: 20px;">JD</span>
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
    st.markdown('<h1 style="font-size: 22px; font-weight: bold; color: #1a56db;">Financial Assistant</h1>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="tools-indicator"><span class="green-dot"></span>Tools: stock_tools.py • visualization.py</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Chat container
container = st.container(border=True)
with container:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Display charts based on user queries
    if len(st.session_state.messages) == 1:
        st.plotly_chart(create_portfolio_chart(), use_container_width=True)
    elif len(st.session_state.messages) > 1 and "portfolio" in st.session_state.messages[-1]["content"].lower() and st.session_state.messages[-1]["role"] == "user":
        st.markdown('<div class="ai-message">Here\'s your portfolio performance over the last 6 months:</div>', unsafe_allow_html=True)
        st.plotly_chart(create_portfolio_chart(), use_container_width=True)
        if st.session_state.messages[-1]["role"] != "assistant":
            st.session_state.messages.append({"role": "assistant", "content": "Here's your portfolio performance over the last 6 months."})
    elif len(st.session_state.messages) > 1 and "asset allocation" in st.session_state.messages[-1]["content"].lower() and st.session_state.messages[-1]["role"] == "user":
        st.markdown('<div class="ai-message">Here\'s your current asset allocation:</div>', unsafe_allow_html=True)
        st.plotly_chart(create_asset_allocation_chart(), use_container_width=True)
        if st.session_state.messages[-1]["role"] != "assistant":
            st.session_state.messages.append({"role": "assistant", "content": "Here's your current asset allocation."})

# Suggested prompts
st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.markdown('<div class="suggestion-pill">Check crypto prices</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="suggestion-pill">Analyze my spending</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="suggestion-pill">Investment recommendations</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Chat input with Streamlit's native component
prompt = st.chat_input(
    "Ask a financial question...",
    accept_file=True,
    file_type=["csv"],
)
if prompt and prompt.text:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate appropriate response
    if "portfolio" in prompt.text.lower():
        response = "Here's your portfolio performance over the last 6 months."
    elif "asset" in prompt.text.lower() or "allocation" in prompt.text.lower():
        response = "Here's your current asset allocation."
    elif "stock" in prompt.text.lower():
        response = "Let me fetch the latest stock information for you."
    elif "crypto" in prompt.text.lower():
        response = "Here are the current cryptocurrency prices."
    elif "spend" in prompt.text.lower():
        response = "I'll analyze your spending patterns right away."
    elif "invest" in prompt.text.lower():
        response = "Based on your risk profile, here are some investment recommendations."
    else:
        response = "I'll need to process that request. Let me get back to you soon."
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()