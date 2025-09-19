# RAG Chatbot

A web-based AI assistant that uses a Retrieval-Augmented Generation (RAG) system to answer questions by retrieving information directly from uploaded PDF documents.
---

## How to Run

### 1. Clone the Repository
git clone https://github.com/cadelxd/RAG-Chatbot.git<br>
cd RAG-Chatbot<br>

### 2. Create and Activate Virtual Environment
python -m venv venv<br>
venv\Scripts\activate<br>

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Set your Gemini API Key
create a .env file in the root directory:<br>
GEMINI_API_KEY=your_gemini_api_key_here

### 5. Apply Migrations
python manage.py makemigrations<br>
python manage.py migrate

### 6. Run the Development Server
python manage.py runserver

### 7. Access the App
visit: http://localhost:8000