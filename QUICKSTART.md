# 🚀 Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get API Key

### Option A: Groq (Recommended - Free & Fast)
1. Go to https://console.groq.com/
2. Sign up for free account
3. Create API key
4. Copy your API key

### Option B: OpenAI
1. Go to https://platform.openai.com/
2. Sign up/login
3. Create API key
4. Copy your API key

## Step 3: Set Up Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
copy env.example .env
```

Then edit `.env` and add your API key:
```
GROQ_API_KEY=your_actual_key_here
```

## Step 4: Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Step 5: Use the App

1. **Upload Documents**: Upload your Job Description and Interview Questions (PDF or TXT)
2. **Process**: Click "Process Documents" button
3. **Ask Questions**: Enter your API key in sidebar (if not in .env), then ask questions!

## 📝 Example Questions

- "How should I answer 'Tell me about yourself'?"
- "What should I say when asked about my strengths?"
- "How do I answer 'Why are you interested in this role?'"

## 🎯 Tips

- First run will download the embedding model (~80MB) - be patient!
- Use Groq for faster, free responses
- Upload multiple documents for better context
- Check "Source Documents" to see where answers come from

## 🐛 Common Issues

**"Module not found"**: Run `pip install -r requirements.txt` again

**"API key error"**: Make sure your API key is correct in `.env` or sidebar

**"PDF loading error"**: Ensure PDF is not corrupted or password-protected

Happy interviewing! 🎉
