# 💼 AI Interviewer

Practice technical and behavioral interviews with an AI that actually evaluates your answers — scores them, gives detailed feedback, and generates a full hiring report at the end.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Claude](https://img.shields.io/badge/Claude-API-orange?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🎯 What It Does

- 🎭 **7 job roles** — SDE, ML Engineer, Data Scientist, Frontend, Backend, PM, DevOps
- 🎚️ **3 difficulty levels** — Junior, Mid-Level, Senior
- 🎤 **5 dynamic questions** — mix of technical and behavioral, difficulty increases
- 📊 **Per-answer scoring** — 1-10 score, verdict, strengths, improvements, ideal answer points
- 📋 **Final hiring report** — overall score, hiring verdict, top strength/weakness, recommendations
- 🔄 **Restart anytime** — try different roles and levels

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Claude API (Anthropic) | Question generation + answer evaluation |
| Streamlit | Web app + session state management |

---

## 🚀 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/Navld14/ai-interviewer.git
cd ai-interviewer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```

Get your free API key at [console.anthropic.com](https://console.anthropic.com)

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🎭 Available Roles

| Role | Focus Areas |
|------|------------|
| 🧑‍💻 Software Engineer | DSA, system design, OOP |
| 🤖 ML Engineer | ML, deep learning, MLOps |
| 📊 Data Scientist | Statistics, SQL, visualization |
| 🎨 Frontend Developer | React, CSS, web performance |
| ⚙️ Backend Developer | APIs, databases, scalability |
| 📦 Product Manager | Roadmaps, metrics, user stories |
| ☁️ DevOps Engineer | Docker, Kubernetes, CI/CD |

---

## 💡 How It Works

```
User selects role + level
        ↓
Claude generates question (avoids repeats, scales difficulty)
        ↓
User types answer
        ↓
Claude evaluates: score 1-10, verdict, strength, improvement
        ↓
Repeat for 5 questions
        ↓
Claude generates final hiring report
```

---

## 📁 Project Structure

```
ai-interviewer/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
└── README.md
```

---

## 🙋 Author

**Naveen Ladha**
[GitHub](https://github.com/Navld14)

---

## 📄 License

MIT License — free to use and modify.
