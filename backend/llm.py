import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"


def ask_llm(question: str, expenses_data: str) -> str:
    prompt = f"""You are a personal finance assistant. Analyze the user's expense data and answer their question clearly and concisely.

Expense Data (CSV format):
{expenses_data}

User Question: {question}

Provide a helpful, specific answer based on the data. If you notice any spending patterns or can give useful advice, include that too. Keep your response concise (3-5 sentences max unless a breakdown is needed).
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("response", "No response from model.")

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running with `ollama serve`."
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out. Try again."
    except Exception as e:
        return f"Error: {str(e)}"