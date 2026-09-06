# PatraAI - Intelligent Full-Stack RAG Application

PatraAI is a production-ready, full-stack Retrieval-Augmented Generation (RAG) web application that allows users to upload PDF documents and interact with an intelligent AI assistant to query and extract insights from their content.

---

## Architecture & Tech Stack

- **Frontend**: Next.js (App Router), React, Tailwind CSS, Lucide Icons, React Markdown
- **Backend**: FastAPI (Python), Uvicorn
- **Vector Database**: Pinecone (384-dimensional index: `patra-ai`)
- **Embeddings & LLM**: Hugging Face Embeddings (`all-MiniLM-L6-v2`) via LangChain
- **Deployment**: 
  - Backend hosted on **Railway**
  - Frontend hosted on **Vercel**

---

## Project Structure

```text
PatraAI--RAG-Project/
├── api.py                  # FastAPI backend server & RAG pipeline
├── requirements.txt        # Python backend dependencies
├── rag-ui/                 # Next.js frontend application
│   ├── src/app/            # App router pages and components
│   ├── public/             # Static assets (logos, icons)
│   ├── package.json        # Node.js dependencies
│   └── ...
└── README.md
```

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/suminyol/PatraAI--RAG-Project.git
cd PatraAI--RAG-Project
```

### 2. Backend Setup (FastAPI)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
HF_TOKEN=your_huggingface_token
PINECONE_API_KEY=your_pinecone_api_key
```

Run the backend server:
```bash
uvicorn api:app --reload --port 8000
```

### 3. Frontend Setup (Next.js)
Open a new terminal window:
```bash
cd rag-ui
npm install
```

Create a `.env.local` file inside `rag-ui/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the frontend development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Production Deployment

### Backend (Railway)
1. Connect your GitHub repository to Railway.
2. Set the root directory to the project root.
3. Configure environment variables in the Railway dashboard:
   - `HF_TOKEN`
   - `PINECONE_API_KEY`
4. Railway will automatically build and deploy using `requirements.txt`.

### Frontend (Vercel)
1. Import your GitHub repository into Vercel.
2. Set the **Root Directory** to `rag-ui`.
3. Add the production environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://<your-railway-backend-url>`
4. Deploy!
