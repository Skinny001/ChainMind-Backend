import google.generativeai as genai
import os, json, groq
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

# Configure Groq Fallback
groq_key = os.getenv("GROQ_API_KEY")
groq_client = groq.Groq(api_key=groq_key) if groq_key else None


def analyze_with_groq(source_code: str, vulnerabilities: list) -> list:
    """Fallback attack generation via Groq."""
    if not groq_client: return []
    
    vulnerability_list = ", ".join([v.get('title') for v in vulnerabilities])
    prompt = f"""
    You are an expert offensive security researcher or 'white-hat' attacker.
    A developer just ran an audit on their contract and found these vulnerabilities:
    {vulnerability_list}

    CONTRACT CODE:
    {source_code}

    Create 7 distinct attack scenarios that can be executed on this contract.
    Return ONLY a JSON list of objects. Each object must have:
    - title: name of the attack
    - description: clear explanation of the attack
    - impact_estimate: text description of damage
    - probability: HIGH, MEDIUM, or LOW
    - exploit_steps: list of 3-5 numbered steps
    - vulnerability_id: title of the vulnerable part this exploit hits
    """

    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        if isinstance(data, dict):
            for k in data.keys():
                if isinstance(data[k], list): return data[k]
        return data if isinstance(data, list) else [data]
    except:
        return []


def generate_attack_scenarios(source_code: str, vulnerabilities: list) -> list:
    """
    Generate 7 realistic attack scenarios based on vulnerabilities.
    These are the 'cards' shown in the UI.
    Returns: [{title, description, impact_estimate, probability, exploit_steps}, ...]
    """
    if not model:
        return analyze_with_groq(source_code, vulnerabilities)

    vulnerability_list = ", ".join([v.get('title') for v in vulnerabilities])
    prompt = f"""
    You are an expert offensive security researcher or 'white-hat' attacker.
    A developer just ran an audit on their contract and found these vulnerabilities:
    {vulnerability_list}

    CONTRACT:
    {source_code}

    Create 7 distinct attack scenarios that can be executed on this contract.
    Return ONLY a JSON list of objects. Each object must have:
    - title: name of the attack (e.g., "Reentrancy Drain", "Flash Loan Mint Glitch")
    - description: clear explanation of the attack
    - impact_estimate: text description of the damage (e.g., "Drains all staked ether")
    - probability: HIGH, MEDIUM, or LOW
    - exploit_steps: a list of 3-5 numbered steps to reproduce the attack
    - vulnerability_id: title of the vulnerable part this exploit hits

    Be creative and realistic. Return ONLY JSON.
    """

    try:
        response = model.generate_content(prompt)
        text     = response.text.replace("```json", "").replace("```", "").strip()
        data     = json.loads(text)
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"Attack Gen Failed on Gemini. Falling back to Groq: {e}")
        return analyze_with_groq(source_code, vulnerabilities)

def run_attacks(source_code: str, vulnerabilities: list) -> list:
    """
    Main entry point for building attack scenarios for the frontend.
    """
    if not vulnerabilities:
        return []
    return generate_attack_scenarios(source_code, vulnerabilities)

if __name__ == "__main__":
    # Test (mock)
    pass
    # mock_code = "contract Test { function withdraw(uint a) public { msg.sender.call{value:a}(''); staked[msg.sender]=0; } }"
    # mock_vulns = [{"title": "Reentrancy", "severity": "HIGH", "description": "State change after call."}]
    # print(run_attacks(mock_code, mock_vulns))
