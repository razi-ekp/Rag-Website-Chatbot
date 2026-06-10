# Contributing to RAG Website Chatbot

Thank you for your interest in contributing! Here's how you can help.

##  Reporting Bugs

1. Go to [Issues](https://github.com/razi-ekp/Rag-Website-Chatbot/issues)
2. Click **New Issue**
3. Describe the bug clearly
4. Include steps to reproduce it
5. Add screenshots if possible

##  Suggesting Features

1. Go to [Issues](https://github.com/razi-ekp/Rag-Website-Chatbot/issues)
2. Click **New Issue**
3. Start the title with `[Feature Request]`
4. Describe what you want and why

##  Setting Up for Development

```bash
# Clone the repo
git clone https://github.com/razi-ekp/Rag-Website-Chatbot.git
cd Rag-Website-Chatbot

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Add your GROQ_API_KEY to .env

# Frontend setup
cd ../frontend
npm install
npm start
```

##  Making Changes

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write clear commit messages
5. Push and open a Pull Request

##  Code Style

- Python: follow PEP8
- JavaScript: use consistent formatting
- Write clear, descriptive commit messages
- Add comments where needed

##  Author

Mohammed Razi — [GitHub](https://github.com/razi-ekp)