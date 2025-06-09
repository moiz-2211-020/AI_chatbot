# 🤖 AI Chatbot for Hydrogen

This is an AI-powered chatbot built using FastAPI and containerized using Docker. The chatbot is accessible via a REST API and is designed to answer queries related to Hydrogen.

---

## 🚀 Features

- FastAPI-based backend
- Dockerized for easy deployment
- REST endpoint to interact with the chatbot
- Simple and scalable design

---

## 🐳 Getting Started with Docker

### Prerequisites

- Docker
- Docker Compose

### 📦 How to Run

Clone the repository:

```bash
git clone https://github.com/moiz-2211-020/AI_chatbot.git
cd AI_chatbot_for_hydrogen/Final_Ai_project

Make a .env file and set the  following environment variables

GEMINI_API_KEY=AIzaSyAhSYlaJhQAVzkYPXwUSUOfBEg2DVyxlxI
COLLECTION_NAME=pdf_chunks
MYSQL_HOST=ec2-54-162-117-48.compute-1.amazonaws.com
MYSQL_PORT=5556
MYSQL_USER=root
MYSQL_PASSWORD=fusiontestingdb
MYSQL_DATABASE=Fusion
JWT_SECRET=JSON
JWT_ALGORITHM=HS256


Then start the application using Docker Compose:

bash
Copy
Edit
sudo docker compose up -d
This will:

Build the Docker image

Start the FastAPI app

Start any required services (e.g., Qdrant if configured)

🌐 Chatbot Endpoint
Once running, you can send requests to the chatbot via the following endpoint:

POST http://0.0.0.0:8000/ask

Sample Request

{
  "question": "How much hydrogen can FAB-doped LiAlH₄ release below 60°C?"
}

Sample Response

{
  "question": "How much hydrogen can FAB-doped LiAlH₄ release below 60°C?",
  "answer": "LiAlH₄-30FAB released 6.11 wt% hydrogen below 60°C."
}


📄 API Docs
Interactive documentation is available at:

http://0.0.0.0:8000/docs



