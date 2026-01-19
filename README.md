# 🎯 Interview Prep RAG Bot

An AI-powered interview preparation assistant that helps candidates prepare role-specific answers using Retrieval-Augmented Generation (RAG).

## 🧠 Problem Statement

### ❌ Common Problems
- Candidates struggle to structure interview answers effectively
- Answers are generic and not tailored to specific roles
- AI assistants often hallucinate or provide inaccurate information

### ✅ Our Solution
- Uses **RAG** to ground answers in job-specific documents
- Generates structured, role-aligned answers based on actual job descriptions
- Provides clear, actionable guidance using STAR method and bullet points

## 🏗️ Architecture

```
User Uploads JD + Questions
        ↓
Text Extraction (PDF/TXT)
        ↓
Text Chunking (500 chars, 100 overlap)
        ↓
Embeddings (HuggingFace all-MiniLM-L6-v2)
        ↓
Vector Database (ChromaDB)
        ↓
User Question
        ↓
Relevant Context Retrieved (Top 3 chunks)
        ↓
LLM Generates Structured Answer
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.8+ |
| UI Framework | Streamlit |
| RAG Framework | LangChain |
| Embeddings | HuggingFace Sentence Transformers |
| Vector Database | ChromaDB |
| LLM | Groq (llama-3.1-8b-instant) / OpenAI |

## 📁 Project Structure

```
interview-prep-rag/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .env.example          # Environment variables template
│
├── rag/
│   ├── __init__.py       # Package initialization
│   ├── loader.py         # Document loading (PDF/TXT)
│   ├── splitter.py       # Text chunking
│   ├── embeddings.py     # Embedding model setup
│   ├── vector_store.py   # Vector database management
│   └── qa_chain.py       # RAG QA chain with prompts
│
└── db/                   # ChromaDB persistence (auto-created)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Groq API key (free) or OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Rag
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your API key:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```
   - **Groq (Recommended - Free)**: Sign up at [console.groq.com](https://console.groq.com/)
   - **OpenAI**: Get key from [platform.openai.com](https://platform.openai.com/)

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`

## 📖 Usage

1. **Upload Documents**
   - Upload Job Description (PDF or TXT)
   - Upload Interview Questions (PDF or TXT)
   - Click "Process Documents"

2. **Configure**
   - Enter your API key in the sidebar (or set in `.env` file)
   - Select LLM provider (Groq or OpenAI)

3. **Ask Questions**
   - Type your question in the input box
   - Or click example questions
   - Get structured, role-specific answers!

## 🎯 Features

- ✅ PDF and TXT document support
- ✅ Multiple document upload
- ✅ Role-specific answer generation
- ✅ Structured output (STAR method, bullet points)
- ✅ Source document references
- ✅ Multiple LLM provider support
- ✅ Persistent vector database
- ✅ Environment variable support for API keys

## 🧠 How RAG Works

**Retrieval-Augmented Generation** combines:
1. **Retrieval**: Find relevant context from your documents using semantic search
2. **Augmentation**: Add retrieved context to your prompt
3. **Generation**: LLM generates answer based on context

This prevents hallucinations and ensures answers are grounded in your actual documents.

## 📝 CV Bullet Points

- Built a **RAG-based Interview Preparation Assistant** that generates role-specific interview answers grounded in job descriptions and interview materials
- Implemented document ingestion, chunking, embeddings, and vector retrieval using **LangChain and ChromaDB**
- Designed prompt templates to enforce **STAR-method structured responses**
- Developed an interactive **Streamlit UI** with multi-document upload and source-based answers

## 🔜 Future Enhancements

- [ ] STAR template toggle
- [ ] Answer scoring/feedback
- [ ] Chat history persistence
- [ ] Multiple answer format options
- [ ] Deploy on Streamlit Cloud
- [ ] Export answers as PDF

## 🐛 Troubleshooting

### Issue: "No module named 'langchain_community'"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: "API key not found"
**Solution**: Set your API key in `.env` file or enter it in the sidebar

### Issue: "Error loading PDF"
**Solution**: Ensure PDF is not corrupted and is a valid PDF file

### Issue: "Vector database error"
**Solution**: Delete the `db/` folder and reprocess documents

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📧 Contact

_Your contact information_

---

**Built with ❤️ using LangChain, ChromaDB, and Streamlit**
