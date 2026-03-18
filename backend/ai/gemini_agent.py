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


def analyze_with_groq(source_code: str) -> list:
    """
    Fallback analysis using Groq's Llama-3.3-70b.
    """
    if not groq_client:
        return [{"title": "Critical Error", "severity": "ERROR", "description": "Both Gemini and Groq AI providers are unavailable."}]
    
    prompt = f"""
    You are an expert Solidity security researcher named ChainMind.
    Analyze the following Solidity contract for security vulnerabilities.
    Return ONLY a JSON list of objects. Each object must have:
    - title: short name (e.g., "Reentrancy")
    - severity: CRITICAL, HIGH, MEDIUM, LOW, or INFO
    - description: clear explanation of the bug
    - line: approximate line number (integer or 0)
    - impact: how an attacker could exploit this
    - fix_suggestion: one-sentence code-level fix

    CONTRACT CODE:
    {source_code}
    """

    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        # Handle cases where LLM returns a wrapped object like {"vulnerabilities": [...]}
        if isinstance(data, dict):
            for k in data.keys():
                if isinstance(data[k], list):
                    return data[k]
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"Groq Fallback Analysis Failed: {e}")
        return [{"title": "System Overload", "severity": "ERROR", "description": "AI analysis is temporarily unavailable on all providers. Please try again in 1 minute."}]


def analyze_contract(source_code: str) -> list:
    """
    Main analysis endpoint: source code → JSON list of vulnerabilities.
    Returns: [{title, severity, description, line, impact, fix_suggestion}, ...]
    """
    if not model:
        return analyze_with_groq(source_code)

    prompt = f"""
    You are an expert Solidity security researcher named ChainMind.
    Analyze the following Solidity contract for security vulnerabilities.
    Return ONLY a JSON list of objects. Each object must have:
    - title: short name (e.g., "Reentrancy")
    - severity: CRITICAL, HIGH, MEDIUM, LOW, or INFO
    - description: clear explanation of the bug
    - line: approximate line number (integer or 0)
    - impact: how an attacker could exploit this
    - fix_suggestion: one-sentence code-level fix

    CONTRACT CODE:
    {source_code}
    """

    try:
        response = model.generate_content(prompt)
        text     = response.text.replace("```json", "").replace("```", "").strip()
        data     = json.loads(text)
        return data if isinstance(data, list) else [data]
    except Exception as e:
        # Check specifically for Quota/429 errors
        if "429" in str(e) or "quota" in str(e).lower():
            print("Gemini Quota Exceeded. Falling back to Groq Llama-3.3...")
            return analyze_with_groq(source_code)
        
        print(f"Gemini Analysis Failed: {e}")
        # Fallback for other generic Gemini failures
        return analyze_with_groq(source_code)


def generate_fixes(source_code: str, vulnerabilities: list) -> list:
    """
    Generate patched code snippets for each vulnerability.
    """
    if not model and not groq_client:
        return []

    fixes = []
    for vuln in vulnerabilities:
        prompt = f"""
        Provide a patched version of the code snippet for this vulnerability in the contract.
        VULNERABILITY: {vuln.get('title')}
        DESCRIPTION: {vuln.get('description')}

        Return ONLY the corrected code snippet. No explanation.
        """
        try:
            # 1. Try Gemini
            if model:
                try:
                    response = model.generate_content(prompt)
                    fixes.append({
                        "title":   vuln.get("title"),
                        "snippet": response.text.replace("```solidity", "").replace("```", "").replace("```", "").strip()
                    })
                    continue # Success
                except Exception as e:
                    if "429" not in str(e): raise e # If not quota, raise to fallback to Groq below

            # 2. Try Groq Fallback
            if groq_client:
                response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile"
                )
                fixes.append({
                    "title":   vuln.get("title"),
                    "snippet": response.choices[0].message.content.replace("```solidity", "").replace("```", "").strip()
                })
        except Exception as e:
            print(f"Fix Generation Failed for {vuln.get('title')}: {e}")
            pass
    return fixes

if __name__ == "__main__":
    # Test (mock)
    mock_code = "contract Test { function withdraw(uint a) public { msg.sender.call{value:a}(''); staked[msg.sender]=0; } }"
    # print(analyze_contract(mock_code))
