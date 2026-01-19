import streamlit as st
import os
import tempfile
import shutil
import time
import stat
import uuid
from pathlib import Path
from dotenv import load_dotenv
from rag.loader import load_document
from rag.splitter import split_docs
from rag.embeddings import get_embeddings
from rag.vector_store import create_vector_store
from rag.qa_chain import create_qa_chain, get_llm
from rag.evaluator import evaluate_answer
from rag.logger import log_query, get_stats

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="🎯 Interview Prep RAG Bot",
    page_icon="a",
    layout="wide"
)

# Global CSS Styling
st.markdown("""
<style>
/* Main background */
.main {
    background-color: #0e1117;
}

/* Titles */
h1, h2, h3 {
    color: #f1f5f9;
}

/* Subtle text */
p, label, span {
    color: #cbd5e1;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: 600;
    border: none;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

/* Input boxes */
.stTextInput input, .stTextArea textarea {
    border-radius: 10px;
    background-color: #020617;
    color: #e5e7eb;
}

/* File uploader */
.stFileUploader {
    border-radius: 10px;
}

/* Answer box */
.answer-box {
    background-color: #020617;
    border-left: 5px solid #6366f1;
    padding: 1rem;
    border-radius: 10px;
    color: #e5e7eb;
    line-height: 1.8;
    font-size: 16px;
}

.answer-box strong {
    font-weight: 700;
    color: #f1f5f9;
}

.answer-box p {
    margin: 0.8rem 0;
}

/* Yellow border boxes for input sections */
.input-section-box {
    border: 3px solid #fbbf24;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    background-color: #1e293b;
}

/* Text area styling */
.stTextArea textarea {
    border: 2px solid #fbbf24 !important;
    border-radius: 10px;
    background-color: #020617;
    color: #e5e7eb;
}

/* File uploader styling */
.uploadedFile {
    border: 2px solid #fbbf24 !important;
    border-radius: 10px;
}

/* File uploader container */
[data-testid="stFileUploader"] {
    border: 2px solid #fbbf24 !important;
    border-radius: 12px;
    padding: 1rem;
    background-color: #1e293b;
}

/* Evaluation metrics */
[data-testid="stMetricValue"] {
    color: #10b981;
    font-weight: 700;
}

/* Chat history */
.chat-history-box {
    background-color: #1e293b;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Hero Header Section
st.markdown("""
<h1>🎯 Interview Prep RAG Assistant</h1>
<p style="font-size:18px; color:#cbd5e1;">
AI-powered interview preparation using <b>Retrieval-Augmented Generation (RAG)</b>.
Upload job descriptions and interview questions to receive 
<b>structured, role-specific answers</b>.
</p>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.caption("Configure your AI model securely")
    st.divider()
    
    # LLM Provider selection
    provider = st.selectbox(
        "Choose LLM Provider",
        ["groq", "openai"],
        help="Groq is free and fast. OpenAI requires API key."
    )
    
    # API Key input (with .env fallback)
    env_key = os.getenv(f"{provider.upper()}_API_KEY")
    default_key = env_key if env_key else ""
    
    if provider == "groq":
        api_key = st.text_input(
            "Groq API Key",
            value=default_key,
            type="password",
            help="Get your free API key from https://console.groq.com/ or set GROQ_API_KEY in .env"
        )
    else:
        api_key = st.text_input(
            "OpenAI API Key",
            value=default_key,
            type="password",
            help="Get your API key from https://platform.openai.com/ or set OPENAI_API_KEY in .env"
        )
    
    st.divider()
    
    # Answer Mode Selection
    st.markdown("### 🎨 Answer Format")
    answer_mode = st.selectbox(
        "Answer Style",
        ["default", "star", "bullet"],
        index=["default", "star", "bullet"].index(st.session_state.get("answer_mode", "default")),
        help="STAR: Situation-Task-Action-Result format | Bullet: Clear bullet points"
    )
    st.session_state.answer_mode = answer_mode
    
    answer_length = st.selectbox(
        "Answer Length",
        ["short", "medium", "long"],
        index=["short", "medium", "long"].index(st.session_state.get("answer_length", "medium")),
        help="Control the detail level of answers"
    )
    st.session_state.answer_length = answer_length
    
    # Evaluation Toggle
    enable_eval = st.checkbox(
        "Enable Answer Evaluation",
        value=st.session_state.get("enable_evaluation", True),
        help="Get AI feedback on answer quality (relevance, clarity, STAR completeness)"
    )
    st.session_state.enable_evaluation = enable_eval
    
    # Semantic Search Preview Toggle
    show_semantic = st.checkbox(
        "Show Semantic Search Details",
        value=st.session_state.get("show_semantic_search", False),
        help="Display retrieved chunks and similarity scores"
    )
    st.session_state.show_semantic_search = show_semantic
    
    st.divider()
    st.markdown("### 📚 How it works:")
    st.markdown("""
    1. Upload Job Description (PDF/TXT)
    2. Upload Interview Questions (PDF/TXT)
    3. (Optional) Upload CV for CV-to-JD matching
    4. Ask questions about how to answer
    5. Get structured, role-specific answers!
    """)
    
    # Usage Stats
    try:
        stats = get_stats()
        if stats["total_queries"] > 0:
            st.divider()
            st.caption(f"📊 Total queries logged: {stats['total_queries']}")
    except:
        pass

# Initialize session state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "answer_mode" not in st.session_state:
    st.session_state.answer_mode = "default"
if "answer_length" not in st.session_state:
    st.session_state.answer_length = "medium"
if "cv_documents" not in st.session_state:
    st.session_state.cv_documents = []
if "cv_mode" not in st.session_state:
    st.session_state.cv_mode = False
if "enable_evaluation" not in st.session_state:
    st.session_state.enable_evaluation = True
if "show_semantic_search" not in st.session_state:
    st.session_state.show_semantic_search = False

# ===============================
# 📄 Knowledge Input Section
# ===============================
st.markdown("## 📄 Knowledge Sources")
st.caption("Provide job-specific context for accurate, role-aligned answers")

# CV Mode Toggle
cv_mode_col1, cv_mode_col2 = st.columns([3, 1])
with cv_mode_col1:
    st.session_state.cv_mode = st.checkbox(
        "🎯 Enable CV-to-JD Matching Mode",
        value=st.session_state.get("cv_mode", False),
        help="Upload your CV to get answers tailored to your actual experience"
    )

# Side-by-side layout container
with st.container():
    # Create two columns for side-by-side layout
    col_left, col_right = st.columns(2)
    
    # Left Column: Paste Text Section with yellow border
    with col_left:
        st.markdown("### 📝 Paste Text")
        st.caption("Paste job descriptions, interview questions, or any relevant text directly here")
        pasted_text = st.text_area(
            " ",
            height=200,
            placeholder="Paste your job description, interview questions, or any relevant text here...",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Right Column: Upload Files Section with yellow border
    with col_right:
        st.markdown("### 📎 Upload Source Files")
        st.caption("Upload PDF or TXT documents containing job descriptions or interview materials")
        uploaded_files = st.file_uploader(
            " ",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CV Upload Section (if CV mode enabled)
    if st.session_state.get("cv_mode", False):
        st.markdown("---")
        st.markdown("### 📄 Upload Your CV (Optional)")
        st.caption("Upload your CV/Resume to get answers tailored to your actual experience")
        cv_files = st.file_uploader(
            "Upload CV",
            type=["pdf", "txt"],
            accept_multiple_files=False,
            key="cv_uploader",
            help="Your CV will be included in the knowledge base for personalized answers"
        )
        if cv_files:
            st.session_state.cv_documents = [cv_files]
        else:
            st.session_state.cv_documents = []
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Centered Process Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_clicked = st.button(
            "🚀 Process Documents",
            type="primary",
            use_container_width=True
        )

# Process documents if button clicked and content provided
if process_clicked and (pasted_text.strip() or uploaded_files):
    with st.spinner("Processing documents..."):
            try:
                # Close existing vectorstore if it exists
                if st.session_state.vectorstore is not None:
                    try:
                        # Try to delete the persistent directory
                        if hasattr(st.session_state.vectorstore, '_persist_directory'):
                            persist_dir = st.session_state.vectorstore._persist_directory
                        else:
                            persist_dir = "db"
                        
                        # Clear session state first
                        st.session_state.vectorstore = None
                        st.session_state.qa_chain = None
                        
                        # Wait a moment for file handles to release
                        time.sleep(0.5)
                        
                        # Try to delete the database folder
                        if os.path.exists(persist_dir):
                            # Use a more robust deletion method for Windows
                            def remove_readonly(func, path, exc):
                                os.chmod(path, stat.S_IWRITE)
                                func(path)
                            
                            shutil.rmtree(persist_dir, onerror=remove_readonly)
                            st.info("🗑️ Cleared previous documents")
                    except Exception as e:
                        # If deletion fails, use a new unique folder name instead
                        st.warning(f"⚠️ Could not clear old database (using new one): {str(e)}")
                
                # Reset session state
                st.session_state.documents_loaded = False
                st.session_state.qa_chain = None
                
                all_docs = []
                
                # Process pasted text if provided
                if pasted_text.strip():
                    from langchain_core.documents import Document
                    # Create a document from pasted text
                    text_doc = Document(page_content=pasted_text.strip(), metadata={"source": "pasted_text"})
                    all_docs.append(text_doc)
                    st.success(f"✅ Loaded pasted text ({len(pasted_text)} characters)")
                
                # Process uploaded files if provided
                if uploaded_files:
                    # Create temporary directory for uploaded files
                    temp_dir = tempfile.mkdtemp()
                    
                    for uploaded_file in uploaded_files:
                        # Save uploaded file temporarily
                        temp_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Load document
                        docs = load_document(temp_path)
                        all_docs.extend(docs)
                        st.success(f"✅ Loaded {uploaded_file.name} ({len(docs)} pages)")
                
                # Process CV if CV mode is enabled
                if st.session_state.get("cv_mode", False) and st.session_state.get("cv_documents", []):
                    cv_temp_dir = tempfile.mkdtemp()
                    for cv_file in st.session_state.cv_documents:
                        cv_temp_path = os.path.join(cv_temp_dir, cv_file.name)
                        with open(cv_temp_path, "wb") as f:
                            f.write(cv_file.getbuffer())
                        
                        cv_docs = load_document(cv_temp_path)
                        # Add CV prefix to metadata
                        for doc in cv_docs:
                            doc.metadata["source"] = f"CV: {doc.metadata.get('source', cv_file.name)}"
                        all_docs.extend(cv_docs)
                        st.success(f"✅ Loaded CV: {cv_file.name} ({len(cv_docs)} pages)")
                
                # Split documents
                st.info("📝 Splitting documents into chunks...")
                chunks = split_docs(all_docs)
                st.success(f"✅ Created {len(chunks)} chunks")
                
                # Create embeddings
                st.info("🔢 Generating embeddings...")
                embeddings = get_embeddings()
                
                # Create vector store with unique name to avoid conflicts
                db_name = f"db_{uuid.uuid4().hex[:8]}"
                st.info("💾 Creating vector database...")
                vectorstore = create_vector_store(chunks, embeddings, persist_directory=db_name)
                st.session_state.vectorstore = vectorstore
                st.session_state.documents_loaded = True
                # Reset chat history when new documents are loaded
                st.session_state.chat_history = []
                
                st.progress(100)
                st.success("🎉 Knowledge base ready! You can now ask questions.")
                
            except Exception as e:
                st.error(f"❌ Error processing documents: {str(e)}")
                st.exception(e)

# Q&A Section
if st.session_state.documents_loaded:
    st.divider()
    st.markdown("## 💬 Ask Interview Questions")
    st.caption("Get AI-powered, role-specific interview answers")
    
    # Initialize QA chain if API key is provided (recreate if answer mode/length changed)
    if api_key:
        # Check if we need to recreate the chain
        chain_key = f"{provider}_{st.session_state.answer_mode}_{st.session_state.answer_length}"
        if (st.session_state.qa_chain is None or 
            st.session_state.get("chain_key") != chain_key):
            try:
                with st.spinner("Initializing AI model..."):
                    llm = get_llm(provider=provider, api_key=api_key)
                    qa_chain = create_qa_chain(
                        llm, 
                        st.session_state.vectorstore,
                        answer_mode=st.session_state.answer_mode,
                        length=st.session_state.answer_length
                    )
                    st.session_state.qa_chain = qa_chain
                    st.session_state["chain_key"] = chain_key
                    st.success("✅ AI model ready!")
            except Exception as e:
                st.error(f"❌ Error initializing model: {str(e)}")
                st.info("Please check your API key and try again.")
    
    # Chat History Display
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        with st.expander("View Chat History", expanded=False):
            for i, (q, a) in enumerate(st.session_state.chat_history[-5:], 1):  # Show last 5
                st.markdown(f"**Q{i}:** {q}")
                st.markdown(f"**A{i}:** {a[:150]}...")
                st.divider()
        
        # Clear history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Question input
    if st.session_state.qa_chain:
        # Initialize example question in session state
        if "example_question" not in st.session_state:
            st.session_state.example_question = ""
        
        # Example questions
        st.markdown("### 💡 Try sample questions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Tell me about yourself"):
                st.session_state.example_question = "How should I answer 'Tell me about yourself'?"
                st.rerun()
        with col2:
            if st.button("Why this role?"):
                st.session_state.example_question = "How should I answer 'Why are you interested in this role?'?"
                st.rerun()
        with col3:
            if st.button("Your strengths"):
                st.session_state.example_question = "How should I answer 'What are your strengths?'?"
                st.rerun()
        
        # Question input with example question as default
        question = st.text_input(
            "Ask a question:",
            value=st.session_state.example_question,
            placeholder="e.g., How should I answer 'Tell me about yourself'? Or ask a follow-up question...",
            key="question_input"
        )
        
        # Clear example question after using it
        if st.session_state.example_question:
            st.session_state.example_question = ""
        
        # Get answer
        if question:
            with st.spinner("🤔 Generating answer..."):
                try:
                    # Build chat history context
                    chat_context = ""
                    if st.session_state.chat_history:
                        recent_qas = st.session_state.chat_history[-3:]  # Last 3 Q&As
                        chat_context = "\n".join([f"Q: {q}\nA: {a[:200]}..." for q, a in recent_qas])
                    
                    # Get LLM for evaluation if needed
                    llm_for_eval = None
                    if st.session_state.enable_evaluation:
                        llm_for_eval = get_llm(provider=provider, api_key=api_key)
                    
                    result = st.session_state.qa_chain({
                        "query": question,
                        "chat_history": chat_context
                    })
                    answer = result["result"]
                    sources = result.get("source_documents", [])
                    similarity_scores = result.get("similarity_scores", [])
                    
                    # Add to chat history
                    st.session_state.chat_history.append((question, answer))
                    
                    # Log the query
                    try:
                        log_query(
                            question=question,
                            answer=answer,
                            sources_count=len(sources),
                            answer_mode=st.session_state.answer_mode
                        )
                    except:
                        pass
                    
                    # Display answer with elegant styling
                    st.markdown("### 📝 Suggested Answer")
                    # Clean and format the answer
                    import html
                    import re
                    answer_text = str(answer)
                    
                    # Remove markdown bold formatting (**text**) and convert to HTML bold
                    answer_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', answer_text)
                    
                    # Convert newlines to paragraphs for better spacing
                    paragraphs = answer_text.split('\n')
                    formatted_paragraphs = []
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            # Escape HTML but preserve our strong tags
                            para = html.escape(para)
                            # Restore strong tags after escaping
                            para = para.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
                            formatted_paragraphs.append(f'<p>{para}</p>')
                    
                    formatted_answer = ''.join(formatted_paragraphs)
                    
                    st.markdown(
                        f"<div class='answer-box'>{formatted_answer}</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Answer Evaluation
                    if st.session_state.enable_evaluation and llm_for_eval:
                        with st.spinner("📊 Evaluating answer quality..."):
                            try:
                                context_text = "\n\n".join([doc.page_content[:300] for doc in sources[:2]])
                                evaluation = evaluate_answer(llm_for_eval, question, answer, context_text)
                                
                                st.markdown("### 📊 Answer Evaluation")
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Relevance", f"{evaluation['relevance']:.1f}/10")
                                with col2:
                                    st.metric("Clarity", f"{evaluation['clarity']:.1f}/10")
                                with col3:
                                    st.metric("STAR", f"{evaluation['star']:.1f}/10")
                                with col4:
                                    st.metric("Overall", f"{evaluation['overall']:.1f}/10", 
                                            delta=f"{evaluation['overall'] - 7:.1f}" if evaluation['overall'] >= 7 else None)
                                
                                st.markdown("**Feedback:**")
                                st.info(evaluation['feedback'])
                            except Exception as e:
                                st.warning(f"Evaluation unavailable: {str(e)}")
                    
                    # Semantic Search Preview
                    if st.session_state.show_semantic_search and sources:
                        st.markdown("### 🔍 Semantic Search Details")
                        with st.expander("View Retrieved Chunks & Similarity Scores"):
                            for i, (doc, score) in enumerate(zip(sources, similarity_scores), 1):
                                st.markdown(f"**Chunk {i}** (Similarity: {score:.2%})")
                                st.text(doc.page_content[:300] + "...")
                                if doc.metadata.get("source"):
                                    st.caption(f"Source: {doc.metadata['source']}")
                                st.divider()
                    
                    # Display sources
                    if sources:
                        with st.expander("📚 Source Documents"):
                            for i, doc in enumerate(sources[:3], 1):
                                st.markdown(f"**Source {i}:**")
                                if similarity_scores and i <= len(similarity_scores):
                                    st.caption(f"Similarity: {similarity_scores[i-1]:.2%}")
                                st.text(doc.page_content[:200] + "...")
                                
                except Exception as e:
                    st.error(f"❌ Error generating answer: {str(e)}")
                    st.exception(e)
    else:
        st.warning("⚠️ Please enter your API key in the sidebar to ask questions.")
else:
    st.info("👆 Please upload documents first to get started!")

# Footer
st.divider()
st.markdown("""
<div style="text-align:center; font-size:14px; color:#94a3b8; padding: 2rem 0;">
Built with ❤️ using <b>LangChain</b>, <b>ChromaDB</b>, and <b>Streamlit</b><br>
Interview Prep RAG Bot • 2026
</div>
""", unsafe_allow_html=True)
