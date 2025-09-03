import streamlit as st
import requests


def show_upload_ui():
    API_URL = "http://localhost:8080/api/rag/upload-file"

    # Enhanced file uploader with Gemini styling
    st.markdown("""
    <style>
    /* File uploader Gemini styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        border: 2px dashed #e8f0fe !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #4285f4 !important;
        box-shadow: 0 12px 40px rgba(66, 133, 244, 0.2) !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        color: #5f6368 !important;
        border: none !important;
        border-radius: 16px !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #4285f4, #1a73e8) !important;
        color: white !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3) !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4) !important;
    }

    /* File info cards */
    .file-info-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    .file-info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }

    /* Input fields styling */
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

    /* File type badges */
    .file-type-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4285f4, #1a73e8);
        color: white;
        padding: 0.375rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.2);
    }

    /* Progress and status */
    .upload-status {
        background: linear-gradient(135deg, #34a853, #2e7d32);
        color: white;
        padding: 1rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(52, 168, 83, 0.2);
    }

    .upload-error {
        background: linear-gradient(135deg, #ea4335, #d33b2c);
        color: white;
        padding: 1rem;
        border-radius: 16px;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(234, 67, 53, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "📎 Drop your documents here or click to browse",
        type=["pdf", "txt", "csv", "doc", "docx"],
        accept_multiple_files=True,
        help="Supported formats: PDF, TXT, CSV, DOC, DOCX"
    )

    if uploaded_files:
        st.markdown("### 📋 Selected Files")
        for f in uploaded_files:
            file_size_kb = f.size / 1024
            file_type = f.name.split('.')[-1].upper() if '.' in f.name else 'UNKNOWN'

            st.markdown(f"""
            <div class="file-info-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong style="color: #1a73e8; font-size: 1.1rem;">📄 {f.name}</strong>
                    <span class="file-type-badge">{file_type}</span>
                </div>
                <div style="color: #5f6368; font-size: 0.9rem;">
                    📏 Size: {file_size_kb:.2f} KB
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Enhanced input fields with Gemini styling
    col1, col2 = st.columns(2)

    with col1:
        category = st.text_input(
            "📂 Category *",
            placeholder="e.g., documentation, reports, manuals",
            help="Required: Organize your documents by category"
        )

    with col2:
        tags = st.text_input(
            "🏷️ Tags (optional)",
            placeholder="e.g., aws, tutorial, guide",
            help="Optional: Add tags separated by commas for better organization"
        )

    # Enhanced upload button and logic
    if st.button("🚀 Start Upload", key="upload_button", use_container_width=True):
        if not uploaded_files:
            st.markdown('<div class="upload-error">⚠️ Please select files to upload</div>', unsafe_allow_html=True)
        elif not category.strip():
            st.markdown('<div class="upload-error">⚠️ Please enter a category</div>', unsafe_allow_html=True)
        else:
            with st.spinner("🔄 Processing files..."):
                success, fail = 0, 0
                for file in uploaded_files:
                    files = {"file": (file.name, file, file.type)}
                    data = {"category": category}
                    if tags.strip():
                        data["tags"] = tags
                    try:
                        response = requests.post(API_URL, files=files, data=data)
                        if response.ok:
                            success += 1
                        else:
                            fail += 1
                    except Exception:
                        fail += 1

                if success > 0 and fail == 0:
                    st.markdown(f'<div class="upload-status">✅ All {success} files uploaded successfully!</div>',
                                unsafe_allow_html=True)
                elif success > 0:
                    st.markdown(
                        f'<div class="upload-status">⚠️ Upload completed: {success} successful, {fail} failed</div>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="upload-error">❌ Upload failed: {fail} files could not be processed</div>',
                                unsafe_allow_html=True)

    # Enhanced supported formats section
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h4 style="color: #1a73e8; margin-bottom: 1rem; font-weight: 600;">📋 Supported File Formats</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
            <div class="file-type-badge">📕 PDF</div>
            <div class="file-type-badge">📄 TXT</div>
            <div class="file-type-badge">📊 CSV</div>
            <div class="file-type-badge">📝 DOC</div>
            <div class="file-type-badge">📑 DOCX</div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: rgba(232, 240, 254, 0.5); border-radius: 12px; border-left: 4px solid #4285f4;">
            <p style="margin: 0; color: #5f6368; font-size: 0.9rem;">
                💡 <strong>Tip:</strong> Upload documents to build your knowledge base. The AI will analyze and learn from your content to provide intelligent answers.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
