import groq
import os, json
from dotenv import load_dotenv

load_dotenv()

# Configure Groq
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = groq.Groq(api_key=api_key)
else:
    client = None


def generate_transactions(contract_summary: str, count: int = 1000) -> list:
    """
    Generate mass interaction patterns with high speed via Groq.
    Returns: [{from: addr, to: addr, function: name, args: [val], value: ether}, ...]
    The simulation engine executes these.
    """
    if not client:
        # Fallback to simple random patterns
        return []

    prompt = f"""
    You are an expert user behavior simulator for Ethereum.
    The Celo smart contract has these features:
    {contract_summary}

    Generate {count} realistic transaction patterns for mass interaction testing.
    Return ONLY a JSON list of objects. Each object must have:
    - from: address (e.g., "user1", "user2", "attacker1", "whaler1")
    - function: function name to call
    - args: list of arguments (integers, addresses, or strings)
    - value: amount of ether in wei (string)

    Vary the patterns: some users stake small, some withdrawal early, some try to exploit.
    Return only the JSON list of {count} items.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        # Handle cases where LLM returns a wrapped object like {"transactions": [...]}
        if isinstance(data, dict):
            for k in data.keys():
                if isinstance(data[k], list):
                    return data[k]
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"Groq Generation Failed: {e}")
        return []

if __name__ == "__main__":
    # Test
    pass
    # print(generate_transactions("Contract: VulnToken\nFunctions: stake, withdraw, transfer", count=5))
