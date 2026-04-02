from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import csv
import os
from datetime import date
from llm import ask_llm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = "expenses.csv"
FIELDNAMES = ["id", "date", "category", "amount", "note"]

CATEGORIES = [
    "Food", "Transport", "Entertainment", "Shopping",
    "Health", "Utilities", "Education", "Other"
]


class Expense(BaseModel):
    date: str
    category: str
    amount: float
    note: Optional[str] = ""


class ChatRequest(BaseModel):
    question: str


def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_expenses():
    init_csv()
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_next_id(expenses):
    if not expenses:
        return 1
    return max(int(e["id"]) for e in expenses) + 1


@app.get("/expenses")
def get_expenses():
    return read_expenses()


@app.post("/expenses")
def add_expense(expense: Expense):
    init_csv()
    expenses = read_expenses()
    new_id = get_next_id(expenses)

    new_expense = {
        "id": new_id,
        "date": expense.date,
        "category": expense.category,
        "amount": expense.amount,
        "note": expense.note,
    }

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(new_expense)

    return {"message": "Expense added", "expense": new_expense}


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    expenses = read_expenses()
    updated = [e for e in expenses if int(e["id"]) != expense_id]

    if len(updated) == len(expenses):
        raise HTTPException(status_code=404, detail="Expense not found")

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(updated)

    return {"message": "Expense deleted"}


@app.get("/categories")
def get_categories():
    return CATEGORIES


@app.post("/chat")
def chat(req: ChatRequest):
    expenses = read_expenses()
    if not expenses:
        return {"response": "No expenses found. Please add some expenses first."}

    # Format CSV data as a readable string for the LLM
    lines = ["id,date,category,amount,note"]
    for e in expenses:
        lines.append(f"{e['id']},{e['date']},{e['category']},{e['amount']},{e['note']}")
    csv_text = "\n".join(lines)

    response = ask_llm(req.question, csv_text)
    return {"response": response}


@app.get("/summary")
def get_summary():
    expenses = read_expenses()
    if not expenses:
        return {"total": 0, "by_category": {}, "by_date": {}}

    total = sum(float(e["amount"]) for e in expenses)

    by_category = {}
    for e in expenses:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + float(e["amount"])

    by_date = {}
    for e in expenses:
        d = e["date"]
        by_date[d] = by_date.get(d, 0) + float(e["amount"])

    return {
        "total": round(total, 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "by_date": {k: round(v, 2) for k, v in sorted(by_date.items())},
    }