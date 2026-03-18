from mistralai import Mistral
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Mistral
api_key = os.getenv("MISTRAL_API_KEY")
if api_key:
    client = Mistral(api_key=api_key)
else:
    client = None


def answer_question(simulation_data: dict, question: str) -> str:
    """
    Natural Language Q&A: developer asks questions about the audit results.
    Mistral provides clear, developer-friendly answers.
    """
    if not client:
        return "Mistral API key not configured. Cannot answer in natural language."

    # Provide context to Mistral
    context = f"""
    You are ChainMind, an AI security auditor. A developer just audited their contract.
    CONTRACT: {simulation_data.get('contract_name')}
    VULNERABILITIES FOUND: {len(simulation_data.get('vulnerabilities', []))}
    RISK SCORE: {simulation_data.get('risk_score')}/100

    Summarized Vulnerabilities:
    {", ".join([v.get('title') for v in simulation_data.get('vulnerabilities', [])])}

    Answer the developer's question about their audit. Be professional, concise, and helpful.
    """

    try:
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question},
            ]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Mistral Q&A Failed: {e}")
        return f"ChainMind is thinking... but had an error: {str(e)}"

if __name__ == "__main__":
    # Test
    pass
    # print(answer_question({"contract_name": "TestToken", "risk_score": 85}, "What is the most critical issue?"))
