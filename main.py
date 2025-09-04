import streamlit as st
import requests
import time
import re
import threading
from upload import show_upload_ui
from langgraph_monitor import show_langgraph_monitor

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
    # .stApp > div:first-child {display: none !important;}
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

    .stTextArea > div > div > textarea:disabled {
        background: rgba(248, 249, 250, 0.9) !important;
        border-color: #e8eaed !important;
        color: #9aa0a6 !important;
        cursor: not-allowed !important;
    }

    .stTextArea > div > div > textarea:disabled::placeholder {
        color: #bdc1c6 !important;
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

    /* Progress bar styling */
    .progress-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.08);
    }

    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e8f0fe;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4285f4, #1a73e8, #4285f4);
        background-size: 200% 100%;
        animation: progressShimmer 2s infinite;
        border-radius: 4px;
        transition: width 0.3s ease;
    }

    .progress-text {
        text-align: center;
        color: #1a73e8;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .progress-status {
        text-align: center;
        color: #5f6368;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    @keyframes progressShimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Loading button animation */
    .loading-button {
        position: relative;
        overflow: hidden;
    }

    .loading-button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid transparent;
        border-top: 2px solid #ffffff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Typing effect for AI responses */
    .typing-text {
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid #4285f4;
        animation: typing 0.05s steps(1, end), blink-caret 0.75s step-end infinite;
    }

    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }

    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #4285f4; }
    }

    /* Enhanced loading dots */
    .enhanced-loading-dots {
        display: inline-flex;
        gap: 6px;
        align-items: center;
        margin: 0 8px;
    }

    .enhanced-loading-dots span {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #4285f4;
        animation: enhancedBounce 1.4s ease-in-out infinite both;
    }

    .enhanced-loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .enhanced-loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    .enhanced-loading-dots span:nth-child(3) { animation-delay: 0s; }

    @keyframes enhancedBounce {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1.2);
            opacity: 1;
        }
    }

    /* Pulsing effect for active elements */
    .pulse-effect {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    /* Enhanced message animations */
    .message-typing {
        position: relative;
        overflow: hidden;
    }

    .message-typing::after {
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 2px;
        height: 1.2em;
        background: #4285f4;
        animation: blink 1s infinite;
    }

    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }

    /* Enhanced button states */
    .stButton > button:disabled {
        background: linear-gradient(135deg, #9aa0a6, #5f6368) !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }

    .stButton > button:disabled:hover {
        transform: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }

    /* Success animation for completed actions */
    .success-animation {
        animation: successPulse 0.6s ease-out;
    }

    @keyframes successPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    /* Enhanced progress bar with glow effect */
    .progress-fill {
        box-shadow: 0 0 10px rgba(66, 133, 244, 0.3);
    }

    /* Smooth transitions for all interactive elements */
    .stButton > button, .stTextArea > div > div > textarea, .stTextInput > div > div > input {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Enhanced focus states */
    .stTextArea > div > div > textarea:focus, .stTextInput > div > div > input:focus {
        transform: scale(1.01);
        box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1), 0 4px 20px rgba(66, 133, 244, 0.15) !important;
    }

    /* Loading state for the entire chat area */
    .chat-loading {
        opacity: 0.7;
        pointer-events: none;
    }

    /* Enhanced message bubbles with better shadows */
    .chat-message.user-message {
        box-shadow: 0 6px 20px rgba(66, 133, 244, 0.25) !important;
    }

    .chat-message.ai-message {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08) !important;
    }

    /* Dynamic dots animation */
    .dynamic-dots {
        display: inline-block;
        position: relative;
        width: 20px;
        text-align: left;
    }

    .dynamic-dots::after {
        content: '';
        animation: dynamicDots 1.8s infinite;
        font-weight: bold;
    }

    @keyframes dynamicDots {
        0%, 16.66% { content: ''; }
        33.33% { content: '.'; }
        50% { content: '..'; }
        66.66% { content: '...'; }
        83.33%, 100% { content: ''; }
    }

    /* Enhanced progress status with dynamic dots */
    .progress-status-dynamic {
        text-align: center;
        color: #5f6368;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        min-height: 1.2em;
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
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'typing_text' not in st.session_state:
    st.session_state.typing_text = ""

# Enhanced tabs with Gemini styling
tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "⬆️ Document Upload", "🔗 LangGraph 모니터링"])

with tab1:
    st.markdown("""
    <div class="gemini-card">
        <h3 style="color: #1a73e8; margin-bottom: 1rem; font-weight: 600;">💭 Ask AI Assistant</h3>
        <p style="color: #5f6368; margin-bottom: 1.5rem; font-size: 1rem;">Ask questions about your documents or get AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history with loading state
    chat_container = st.container()
    loading_class = "chat-loading" if st.session_state.is_processing else ""

    with chat_container:
        if st.session_state.chat_messages:
            st.markdown(f'<div class="chat-history-container {loading_class}">', unsafe_allow_html=True)

            for i, message in enumerate(st.session_state.chat_messages):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-content">{message['content']}</div>
                        <div class="message-time">{message['timestamp']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Add typing effect for AI messages
                    typing_class = "message-typing" if i == len(
                        st.session_state.chat_messages) - 1 and st.session_state.is_processing else ""
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <div class="message-content {typing_class}" id="ai-message-{i}">{message['content']}</div>
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

    # Add JavaScript for enhanced UI interactions
    st.markdown("""
    <script>
    // Progress bar animation
    function updateProgress(progress) {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        if (progressFill && progressText) {
            progressFill.style.width = progress + '%';
            progressText.textContent = 'Processing: ' + progress + '%';
        }
    }

    // Typing effect for AI responses
    function typeText(element, text, speed = 30) {
        let i = 0;
        element.innerHTML = '';
        const timer = setInterval(() => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                // Remove typing cursor after completion
                element.classList.remove('message-typing');
            }
        }, speed);
    }

    // Enhanced loading animation
    function showLoadingAnimation(button) {
        button.classList.add('loading-button');
        button.disabled = true;
        button.innerHTML = '<span class="enhanced-loading-dots"><span></span><span></span><span></span></span> Processing...';
    }

    function hideLoadingAnimation(button, originalText) {
        button.classList.remove('loading-button');
        button.disabled = false;
        button.innerHTML = originalText;
    }

    // Simulate progress for better UX
    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            updateProgress(Math.floor(progress));
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
        return interval;
    }
    </script>
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
        help="💡 Press Enter to create new lines. Click Send to submit.",
        disabled=st.session_state.is_processing
    )

    # Send button with enhanced loading state
    button_text = "🚀 Send Message"
    if st.session_state.is_processing:
        button_text = '<span class="enhanced-loading-dots"><span></span><span></span><span></span></span> Processing...'

    send_button_clicked = st.button(button_text, key="send_button", use_container_width=True,
                                    disabled=st.session_state.is_processing)

    if send_button_clicked:
        if question.strip():
            # Set processing state
            st.session_state.is_processing = True
            st.session_state.progress = 0

            # Add user message to chat history
            import datetime

            user_message = {
                'role': 'user',
                'content': question.strip(),
                'timestamp': datetime.datetime.now().strftime("%H:%M")
            }
            st.session_state.chat_messages.append(user_message)

            # Show progress bar (only once)
            progress_placeholder = st.empty()

            # Process AI response with progress simulation
            ai_response = ""

            try:
                # Simulate progress updates
                progress_values = [10, 25, 40, 55, 70, 85, 95, 100]
                progress_statuses = [
                    "🤖 AI is analyzing your question... ",
                    "📚 Searching through documents...",
                    "🧠 Processing information...",
                    "💭 Generating response...",
                    "✨ Almost ready...",
                    "🎯 Finalizing answer..."
                ]

                # Start progress simulation
                for i, progress in enumerate(progress_values[:-1]):
                    status_text = progress_statuses[i % len(progress_statuses)]
                    progress_placeholder.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-text">Processing: {progress}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress}%;"></div>
                        </div>
                        <div class="progress-status-dynamic">
                            {status_text}<span class="dynamic-dots"></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.4)  # Simulate processing time

                # Use langchain endpoint
                resp = requests.post(LANGCHAIN_ENDPOINT, json={"question": question})

                if resp.ok:
                    ai_response = resp.json().get("answer", "").replace("**", "")
                    # Final progress update
                    progress_placeholder.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-text">Processing: 100%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 100%;"></div>
                        </div>
                        <div class="progress-status-dynamic">✅ Response ready!</div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.5)
                else:
                    ai_response = "❌ Failed to process your question. Please try again."
                    progress_placeholder.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-text">Processing: 100%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 100%;"></div>
                        </div>
                        <div class="progress-status-dynamic">❌ Error occurred</div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                ai_response = f"🔌 Connection error: {str(e)}"
                progress_placeholder.markdown(f"""
                <div class="progress-container">
                    <div class="progress-text">Processing: 100%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%;"></div>
                    </div>
                    <div class="progress-status-dynamic">❌ Connection error</div>
                </div>
                """, unsafe_allow_html=True)

            # Add AI response to chat history with typing effect
            ai_message = {
                'role': 'assistant',
                'content': add_newline_before_numbered_list(ai_response),
                'timestamp': datetime.datetime.now().strftime("%H:%M")
            }
            st.session_state.chat_messages.append(ai_message)
            st.session_state.is_processing = False

            # Clear progress container
            progress_placeholder.empty()

            # Add typing effect script for the new message
            st.markdown(f"""
            <script>
            // Apply typing effect to the latest AI message
            setTimeout(() => {{
                const latestMessage = document.querySelector('#ai-message-{len(st.session_state.chat_messages) - 1}');
                if (latestMessage) {{
                    const fullText = latestMessage.textContent;
                    latestMessage.textContent = '';
                    latestMessage.classList.add('message-typing');
                    
                    let i = 0;
                    const timer = setInterval(() => {{
                        if (i < fullText.length) {{
                            latestMessage.textContent += fullText.charAt(i);
                            i++;
                        }} else {{
                            clearInterval(timer);
                            latestMessage.classList.remove('message-typing');
                        }}
                    }}, 30);
                }}
            }}, 100);
            </script>
            """, unsafe_allow_html=True)

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

with tab3:
    show_langgraph_monitor()
