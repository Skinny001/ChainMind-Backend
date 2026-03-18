import subprocess
import os
import json
import uuid

def run_simulation(source_code: str, transactions: list) -> dict:
    """
    Core Foundry simulation engine. This:
    1. Writes uploaded .sol file to foundry/src/VulnerableToken.sol
    2. Runs 'forge test -vvv --match-path test/SimulationTest.t.sol'
    3. Parses output for specific failures or attack successes
    4. Returns a dictionary of results for the frontend

    Actually runs mass transactions in SimulationTest.t.sol.
    """
    # Point to the smartcontract folder relative to THIS script
    # backend/simulation/engine.py -> ../../smartcontract
    foundry_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../smartcontract"))
    if not os.path.exists(foundry_root):
        return {"error": "Foundry project root not found at " + foundry_root}

    # 1. Write current contract to be audited
    target_path = os.path.join(foundry_root, "src/VulnerableToken.sol")
    with open(target_path, "w") as f:
        f.write(source_code)

    # 2. Exec forge test
    try:
        # We use forge test --json for cleaner parsing if available, or just -vvv and regex
        process = subprocess.run(
            ["forge", "test", "-vvv", "--match-path", "test/SimulationTest.t.sol"],
            cwd=foundry_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = process.stdout
    except Exception as e:
        return {"error": f"Forge execution failed: {str(e)}", "output": ""}

    # 3. Simple parser for test results
    results = []
    lines   = output.split("\n")
    for line in lines:
        if "[PASS]" in line:
            results.append({"test": line.split(" ")[1], "status": "passed", "details": ""})
        elif "[FAIL]" in line:
            results.append({"test": line.split(" ")[1], "status": "failed", "details": "Potential exploit detected!"})
        elif "log:" in line or "emit" in line:
            # Capture logs from tests (e.g., profit from attacks)
            if results:
                results[-1]["details"] += line.strip() + "\n"

    # 4. Filter for specific attack tests
    attacks_results = [r for r in results if "Attack" in r["test"]]
    pass_count      = sum(1 for r in results if r["status"] == "passed")
    fail_count      = sum(1 for r in results if r["status"] == "failed")

    return {
        "summary": {
            "total_tests":  len(results),
            "passed":       pass_count,
            "failed":       fail_count,
            "success_rate": f"{(pass_count/len(results)*100):.1f}%" if results else "0%",
        },
        "all_tests": results,
        "attack_status": attacks_results,
        "raw_output": output if len(output) < 5000 else output[:5000] + "...truncated" # type: ignore
    }

if __name__ == "__main__":
    # Test (mock)
    mock_code = "contract Test { function stake() public { } }"
    # print(run_simulation(mock_code, []))
