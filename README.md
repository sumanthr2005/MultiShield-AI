# 🛡️ MultiShield AI

> A Multimodal Multi-Agent Hate Speech Detection Platform with Explainable AI

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-MultiAgent-orange)
![Docker](https://img.shields.io/badge/Docker-Deployment-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Overview

MultiShield AI is a production-ready multimodal moderation platform that detects harmful and hateful content across multiple content types including:

* 📝 Text
* 🖼️ Images & Memes
* 🎙️ Audio
* 🎥 Video

The platform uses specialized AI agents to analyze content, combine their outputs, generate explanations, and assist moderators in making transparent decisions.

---

## 🎯 Problem Statement

Modern online communities face challenges such as:

* Hate speech
* Toxic behavior
* Cyberbullying
* Harmful memes
* Voice abuse in gaming communities

Most moderation systems:

* Analyze only text.
* Provide black-box decisions.
* Lack explainability.
* Cannot process multimodal content.

MultiShield AI addresses these challenges through explainable multi-agent AI.

---

## 🏗️ System Architecture

```text
Discord / Telegram / Forums / Gaming Communities
                    │
                    ▼
              API Gateway
                    │
                    ▼
              Router Agent
        ┌────────┼────────┐
        ▼        ▼        ▼
   Text Agent Image Agent Audio Agent
        │        │        │
        └────────┼────────┘
                 ▼
            Fusion Agent
                 ▼
          Explainability Agent
                 ▼
          Moderation Agent
                 ▼
         Moderator Dashboard
```

---

## 🤖 Multi-Agent Architecture

### Router Agent

Routes incoming content to specialized agents.

### Text Agent

Detects:

* Hate speech
* Toxic language
* Offensive content

### Image Agent

Detects:

* Harmful memes
* Hate symbols
* Offensive imagery

### Audio Agent

Analyzes:

* Voice toxicity
* Abusive speech

### Fusion Agent

Combines multimodal predictions.

### Explainability Agent

Provides:

* SHAP explanations
* Confidence scores
* Reasoning

### Moderation Agent

Suggests:

* Allow
* Warn
* Review
* Remove

---

## ✨ Features

✅ Multimodal Content Analysis
✅ Multi-Agent Architecture
✅ Explainable AI (XAI)
✅ Real-Time Moderation APIs
✅ Discord Integration
✅ Telegram Integration
✅ Moderator Dashboard
✅ Human-in-the-Loop Review
✅ Analytics & Reporting
✅ Cloud Deployment Support

---

## 🖥️ Dashboard Features

* Upload text and images.
* View confidence scores.
* Toxic word highlighting.
* Image heatmaps.
* Moderator queue.
* Analytics dashboard.
* Review history.

---

## 🛠️ Tech Stack

### Backend

* FastAPI
* Python
* Pydantic

### Frontend

* React
* TypeScript
* Material UI

### AI/ML

* Transformers
* LangGraph
* SHAP
* OpenCV

### Database

* PostgreSQL
* Redis

### Deployment

* Docker
* Docker Compose
* AWS

### Monitoring

* Prometheus
* Grafana

---

## 📂 Project Structure

```text
MultiShield-AI/
│
├── backend/
│   ├── agents/
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── package.json
│
├── discord-bot/
│
├── docker/
│
├── deployment/
│
├── docs/
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/MultiShield-AI.git
cd MultiShield-AI
```

---

### Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## 🌐 API Example

### Request

```json
POST /analyze

{
    "text": "sample text",
    "image_url": "image.jpg"
}
```

### Response

```json
{
    "label": "hate",
    "confidence": 0.92,
    "explanation": "Harmful text combined with offensive imagery.",
    "action": "Human Review"
}
```

---

## 🎮 Real-World Applications

* Discord communities
* Gaming servers
* Telegram groups
* Social media moderation
* Educational platforms
* Enterprise communication systems
* Community forums

---

## 📊 Explainable AI

MultiShield AI provides:

* Confidence scores
* Feature importance
* Highlighted toxic words
* Visual heatmaps
* Natural language explanations

This helps moderators understand why content was flagged.

---

## ☁️ Deployment

Supported environments:

* Docker
* AWS EC2
* Azure
* Render
* Railway

---

## 👨‍💻 Future Enhancements

* Video moderation
* Multilingual support
* Active learning
* Real-time streaming analysis
* Kubernetes deployment
* LLM-powered reasoning

---


## 📜 License

MIT License

---

## 👤 Author

**Sumanth R**

B.Tech CSE (AI & ML)
SRM Institute of Science and Technology

---

⭐ If you found this project useful, consider giving it a star.
