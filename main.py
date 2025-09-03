import streamlit as st
import requests
import time
import re
from upload import show_upload_ui

API_BASE = "http://localhost:8080/api/chat"
LANGCHAIN_ENDPOINT = "http://localhost:8080/api/chat/ask-langchain"


def add_newline_before_numbered_list(text):
    # "1. ", "2. ", ... 앞에 개행 추가 (이미 줄 시작이면 중복 방지)
    return re.sub(r'(?<!^)(?<!\n)(\d+\.)\s', r'\n\1 ', text)


# Gemini-inspired CSS styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Completely hide ALL Streamlit header elements */
    header {display: none !important;}
    .stAppHeader {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    .stDeployButton {display: none !important;}
    .stApp > header {display: none !important;}
    .stApp > div:first-child {display: none !important;}
    iframe[title="streamlit_analytics"] {display: none !important;}

    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important; }

    /* Main container styling */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        font-family: 'Inter', sans-serif;
    }

    /* Header styling */
    .gemini-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
    }

    .gemini-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a73e8;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #4285f4, #1a73e8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .gemini-subtitle {
        font-size: 1.1rem;
        color: #5f6368;
        font-weight: 400;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: none;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 0.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        border: none !important;
        color: #5f6368 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        padding: 0.75rem 1.5rem !important;
        margin: 0 0.25rem !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(26, 115, 232, 0.1) !important;
        color: #1a73e8 !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4285f4, #1a73e8) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3) !important;
    }

    /* Card styling */
    .gemini-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    .gemini-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }

    /* Input styling - Text Input */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #e8f0fe !important;
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        color: #202124 !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #4285f4 !important;
        box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #9aa0a6 !important;
    }

    /* Text Area styling - Multi-line input */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #e8f0fe !important;
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        color: #202124 !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.5 !important;
        resize: vertical !important;
        min-height: 120px !important;
        max-height: 300px !important;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #4285f4 !important;
        box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1) !important;
        outline: none !important;
    }

    .stTextArea > div > div > textarea::placeholder {
        color: #9aa0a6 !important;
    }

    /* Custom scrollbar for textarea */
    .stTextArea > div > div > textarea::-webkit-scrollbar {
        width: 6px;
    }

    .stTextArea > div > div > textarea::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
    }

    .stTextArea > div > div > textarea::-webkit-scrollbar-thumb {
        background: #4285f4;
        border-radius: 3px;
    }

    .stTextArea > div > div > textarea::-webkit-scrollbar-thumb:hover {
        background: #3367d6;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4285f4, #1a73e8) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3) !important;
        font-family: 'Inter', sans-serif !important;
        text-transform: none !important;
        letter-spacing: 0.025em !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4) !important;
        background: linear-gradient(135deg, #3367d6, #1557b0) !important;
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.3) !important;
    }

    /* Answer box styling */
    .answer-box {
        background: #ffffff !important;
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1.5rem;
        font-size: 1.1rem;
        color: #202124;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.08);
        line-height: 1.7;
        word-break: keep-all;
        font-family: 'Inter', sans-serif;
        opacity: 0;
        animation: slideInUp 0.6s ease-out forwards;
        position: relative;
        overflow: hidden;
    }

    .answer-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4285f4, #1a73e8, #4285f4);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
    }

    /* Spinner styling */
    .stSpinner > div > div {
        border-color: #4285f4 !important;
        border-top-color: transparent !important;
    }

    /* Error/Success messages */
    .stAlert {
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }

    /* Animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Loading animation for answer */
    .loading-dots {
        display: inline-flex;
        gap: 4px;
    }

    .loading-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4285f4;
        animation: bounce 1.4s ease-in-out infinite both;
    }

    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }

    /* Enhanced textarea for mobile */
    @media (max-width: 768px) {
        .main-container {
            padding: 1rem;
        }

        .gemini-title {
            font-size: 2rem;
        }

        .gemini-card {
            padding: 1.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }

        .stTextArea > div > div > textarea {
            min-height: 100px !important;
            max-height: 250px !important;
            font-size: 0.95rem !important;
            padding: 0.875rem 1.25rem !important;
        }

        .stTextArea > div > div > textarea::-webkit-scrollbar {
            width: 4px;
        }
    }

    /* Focus animations for better UX */
    .stTextArea > div > div > textarea:focus {
        animation: focusPulse 0.3s ease-out;
    }

    @keyframes focusPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.01); }
        100% { transform: scale(1); }
    }

    /* Prevent text selection on labels and buttons */
    .stTextArea label, .stButton button {
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }
    </style>
""", unsafe_allow_html=True)

# Gemini-inspired header
st.markdown("""
<div class="gemini-header">
    <div class="gemini-title">🤖 Gemini RAG Assistant</div>
    <div class="gemini-subtitle">Powered by AI - Smart Document Analysis & Chat</div>
</div>
""", unsafe_allow_html=True)

# Initialize chat messages in session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'current_response' not in st.session_state:
    st.session_state.current_response = ""

# Enhanced tabs with Gemini styling
tab1, tab2 = st.tabs(["💬 AI Chat", "⬆️ Document Upload"])

with tab1:
    st.markdown("""
    <div class="gemini-card">
        <h3 style="color: #1a73e8; margin-bottom: 1rem; font-weight: 600;">💭 Ask AI Assistant</h3>
        <p style="color: #5f6368; margin-bottom: 1.5rem; font-size: 1rem;">Ask questions about your documents or get AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    chat_container = st.container()

    with chat_container:
        if st.session_state.chat_messages:
            st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)

            for i, message in enumerate(st.session_state.chat_messages):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-content">{message['content']}</div>
                        <div class="message-time">{message['timestamp']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <div class="message-content">{message['content']}</div>
                        <div class="message-time">{message['timestamp']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # Add CSS for chat messages
    st.markdown("""
    <style>
    .chat-history-container {
        max-height: 60vh;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        margin-bottom: 2rem;
    }

    .chat-message {
        margin-bottom: 1.5rem;
        padding: 1rem 1.5rem;
        border-radius: 20px;
        position: relative;
        animation: messageSlideIn 0.4s ease-out;
    }

    .chat-message.user-message {
        background: linear-gradient(135deg, #4285f4, #1a73e8);
        color: white;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
        max-width: 80%;
    }
c
    .chat-message.ai-message {
        background: #ffffff;
        color: #202124;
        margin-left: 0;
        margin-right: auto;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.08);
        max-width: 80%;
    }

    .message-content {
        line-height: 1.6;
        word-wrap: break-word;
        margin-bottom: 0.5rem;
    }

    .message-time {
        font-size: 0.8rem;
        opacity: 0.7;
        text-align: right;
    }

    .user-message .message-time {
        color: rgba(255, 255, 255, 0.8);
    }

    .ai-message .message-time {
        color: #9aa0a6;
    }

    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .chat-history-container::-webkit-scrollbar {
        width: 6px;
    }

    .chat-history-container::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
    }

    .chat-history-container::-webkit-scrollbar-thumb {
        background: #4285f4;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Always show input form at the bottom
    st.markdown("---")

    # Input section
    # Use dynamic key to force refresh after sending message
    input_key = f"question_input_{len(st.session_state.chat_messages)}"

    question = st.text_area(
        "",
        placeholder="💡 Ask me anything about your documents...\n\n📝 Press Enter for new lines",
        height=100,
        key=input_key,
        label_visibility="collapsed",
        help="💡 Press Enter to create new lines. Click Send to submit."
    )

    # Send button
    if st.button("🚀 Send Message", key="send_button", use_container_width=True):
        if question.strip():
            # Add user message to chat history
            import datetime

            user_message = {
                'role': 'user',
                'content': question.strip(),
                'timestamp': datetime.datetime.now().strftime("%H:%M")
            }
            st.session_state.chat_messages.append(user_message)

            # Process AI response
            displayed_text = ""
            ai_response = ""

            with st.spinner("🤖 AI is thinking..."):
                try:
                    # Use langchain endpoint
                    resp = requests.post(LANGCHAIN_ENDPOINT, json={"question": question})

                    if resp.ok:
                        ai_response = resp.json().get("answer", "").replace("**", "")
                        displayed_text = ai_response
                    else:
                        ai_response = "❌ Failed to process your question. Please try again."

                except Exception as e:
                    ai_response = f"🔌 Connection error: {str(e)}"

            # Add AI response to chat history
            ai_message = {
                'role': 'assistant',
                'content': add_newline_before_numbered_list(ai_response),
                'timestamp': datetime.datetime.now().strftime("%H:%M")
            }
            st.session_state.chat_messages.append(ai_message)

            # Refresh to show new messages
            st.rerun()

    # Clear chat button
    if st.session_state.chat_messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.chat_messages = []
                st.rerun()

with tab2:
    st.markdown("""
    <div class="gemini-card">
        <h3 style="color: #1a73e8; margin-bottom: 1rem; font-weight: 600;">📚 Document Upload</h3>
        <p style="color: #5f6368; margin-bottom: 1.5rem; font-size: 1rem;">Upload documents to build your knowledge base for AI-powered conversations</p>
    </div>
    """, unsafe_allow_html=True)
    show_upload_ui()
