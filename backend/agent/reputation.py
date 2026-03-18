from web3 import Web3
import os, json
from dotenv import load_dotenv

load_dotenv()

CELO_RPC  = os.getenv("RPC_URL", "https://alfajores-forno.celo-testnet.org")
PRIV_KEY  = os.getenv("PRIVATE_KEY", "")
REP_REG   = os.getenv("ERC8004_REPUTATION_REGISTRY", "")

# ERC-8004 Reputation Registry ABI
REPUTATION_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"},{"internalType":"uint8","name":"score","type":"uint8"},{"internalType":"string","name":"feedback","type":"string"}],"name":"submitFeedback","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"}],"name":"getReputation","outputs":[{"internalType":"uint256","name":"totalScore","type":"uint256"},{"internalType":"uint256","name":"feedbackCount","type":"uint256"}],"stateMutability":"view","type":"function"}]')


def submit_audit_reputation(
    agent_id: int,
    score: int,
    contract_name: str,
    vuln_count: int
) -> str:
    """
    Submits a reputation signal to ERC-8004 based on audit quality.
    Score 1-10 (higher is better).
    Returns tx_hash or error string.
    """
    if not PRIV_KEY or not REP_REG:
        return "reputation_not_configured"

    try:
        w3      = Web3(Web3.HTTPProvider(CELO_RPC))
        account = w3.eth.account.from_key(PRIV_KEY)
        registry = w3.eth.contract(address=Web3.to_checksum_address(REP_REG), abi=REPUTATION_ABI)

        feedback = f"Audited {contract_name}: found {vuln_count} vulnerabilities"

        tx = registry.functions.submitFeedback(
            agent_id,
            min(score, 10),
            feedback
        ).build_transaction({
            "from":     account.address,
            "nonce":    w3.eth.get_transaction_count(account.address),
            "gas":      150_000,
            "gasPrice": w3.eth.gas_price,
            "chainId":  11142220
        })

        signed  = w3.eth.account.sign_transaction(tx, PRIV_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

        return tx_hash.hex()

    except Exception as e:
        print(f"Reputation update failed: {e}")
        return f"error: {str(e)[:100]}"
