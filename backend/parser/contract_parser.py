import re

def parse_contract(source_code: str) -> dict:
    """
    Simple regex-based Solidity parser to extract contract structure.
    Returns: {contract_name, functions, state_variables, summary}
    """
    # 1. Extract contract name
    name_match = re.search(r"contract\s+(\w+)", source_code)
    contract_name = name_match.group(1) if name_match else "UnknownContract"

    # 2. Extract functions
    # Matches: function name(...) modifiers {
    function_pattern = r"function\s+(\w+)\s*\((.*?)\)\s*(.*?)\{"
    functions = []
    for match in re.finditer(function_pattern, source_code):
        functions.append({
            "name":      match.group(1),
            "args":      match.group(2).strip(),
            "modifiers": match.group(3).strip(),
        })

    # 3. Extract state variables (simple)
    # Matches: type visibility name; (ignores initialized ones)
    var_pattern = r"(uint256|address|uint8|string|bool)\s+(public|private|internal|external)?\s*(\w+)\s*;"
    state_vars = []
    for match in re.finditer(var_pattern, source_code):
        state_vars.append({
            "type":       match.group(1),
            "visibility": match.group(2) if match.group(2) else "internal",
            "name":       match.group(3),
        })

    # 4. Generate summary for AI
    summary = f"Contract: {contract_name}\n"
    summary += f"Functions: {', '.join([f['name'] for f in functions])}\n"
    summary += f"State Vars: {', '.join([v['name'] for v in state_vars])}\n"

    return {
        "contract_name": contract_name,
        "functions":     functions,
        "state_vars":    state_vars,
        "summary":       summary
    }

if __name__ == "__main__":
    # Test
    test_code = "contract Test { uint256 public balance; function stake() public { } }"
    print(parse_contract(test_code))
