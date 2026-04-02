# 💸 FinSight - Personal Expense Analyzer

FinSight is an AI-powered personal expense analyzer that helps you track, visualize, and understand your spending habits through natural language conversation.

## Features

- Add, view, and delete expenses by category
- Interactive charts — spending by category, pie chart breakdown, spending over time
- Chat with an AI assistant about your expenses using Ollama (Qwen 2.5)
- Data stored locally in CSV format
- Tableau dashboard for advanced data visualization

## Tech Stack

| Layer | Tool |
|-------|------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Charts | Plotly |
| LLM | Ollama (Qwen 2.5 Coder 7B) |
| Storage | CSV |
| Visualization | Tableau |

## Project Structure

```
FinSight/
├── backend/
│   ├── main.py        # FastAPI routes
│   ├── llm.py         # Ollama LLM integration
│   └── expenses.csv   # Local data storage
├── frontend/
│   └── app.py         # Streamlit UI
└── requirements.txt
```

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com) installed and running
- Qwen 2.5 Coder model pulled in Ollama

## Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/Vinamra31/FinSight.git
cd FinSight
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Pull the Ollama model**
```bash
ollama pull qwen2.5-coder:7b
```

## Running the App

Open 3 terminals:

**Terminal 1 — Start Ollama**
```bash
ollama serve
```

**Terminal 2 — Start backend**
```bash
cd backend
python -m uvicorn main:app --reload
```

**Terminal 3 — Start frontend**
```bash
cd frontend
python -m streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## Usage

- Use the **sidebar** to add expenses with date, category, amount, and an optional note
- View **charts** on the dashboard to understand your spending patterns
- Use the **chat box** at the bottom to ask questions like:
  - *"Where am I overspending?"*
  - *"Summarize my expenses this month"*
  - *"Which category costs me the most?"*