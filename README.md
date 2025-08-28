# Quantum Chemistry Energy Estimator

A Python backend using **FastAPI** and **PennyLane** to estimate the **ground state energy** of small molecules (like H₂ or LiH) using **quantum simulation** methods such as **VQE (Variational Quantum Eigensolver)**.

---

## Features

- Find the Ground State of small molecule.
- Playground where you can simulate the Ground State of different small molecule with different configuration.

---

## Installation

### 1. Clone the Project

```bash
git clone <your_repo_url>
```

---

## 2. Backend Setup

1. Go to the backend folder:

```bash
cd backend
```

2. Create a `.env` file and set your GenAI API key:

```
GENAI_API_KEY=your_api_key_here
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

> The backend will run on: `http://localhost:8000`

---

## 3. Frontend Setup

1. Go to the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the frontend:

```bash
npm start
```

> The frontend will run on: `http://localhost:3000`

