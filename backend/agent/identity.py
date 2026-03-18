from web3 import Web3
import os, json
from dotenv import load_dotenv

load_dotenv()

CELO_RPC   = os.getenv("RPC_URL", "https://alfajores-forno.celo-testnet.org")
PRIV_KEY   = os.getenv("PRIVATE_KEY", "")
ID_REG     = os.getenv("ERC8004_IDENTITY_REGISTRY", "")
AGENT_NAME = os.getenv("AGENT_NAME", "ChainMind")
AGENT_DESC = os.getenv("AGENT_DESCRIPTION", "Autonomous AI smart contract security auditor on Celo")

# ERC-8004 Identity Registry ABI (mint function)
IDENTITY_ABI = json.loads('[{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"string","name":"metadataURI","type":"string"}],"name":"registerAgent","outputs":[{"internalType":"uint256","name":"agentId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"agentId","type":"uint256"}],"name":"getAgent","outputs":[{"components":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"metadataURI","type":"string"},{"internalType":"bool","name":"exists","type":"bool"}],"internalType":"struct AgentInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}]')


def register_agent(metadata_uri: str = "") -> dict:
    """
    Register ChainMind as an on-chain agent on ERC-8004 Identity Registry on Celo.
    Returns: {agent_id, tx_hash, owner_address}
    """
    if not PRIV_KEY or not ID_REG:
        return {"error": "ERC-8004 keys not configured", "agent_id": None}

    try:
        w3      = Web3(Web3.HTTPProvider(CELO_RPC))
        account = w3.eth.account.from_key(PRIV_KEY)
        registry = w3.eth.contract(address=Web3.to_checksum_address(ID_REG), abi=IDENTITY_ABI)

        # Agent metadata for the URI (Hackathon alignment)
        agent_metadata = {
            "name": AGENT_NAME,
            "description": AGENT_DESC,
            "type": "security-auditor",
            "capabilities": [
                "vulnerability-detection",
                "attack-simulation",
                "fix-generation",
                "natural-language-qa",
                "economic-agency-cusd"
            ],
            "ai_models": ["gemini-2.0-flash", "llama-3.3-70b", "mistral-large"],
            "chain": "celo-alfajores"
        }

        tx = registry.functions.registerAgent(
            AGENT_NAME,
            AGENT_DESC,
            metadata_uri or json.dumps(agent_metadata)
        ).build_transaction({
            "from":     account.address,
            "nonce":    w3.eth.get_transaction_count(account.address),
            "gas":      300_000,
            "gasPrice": w3.eth.gas_price,
            "chainId":  11142220
        })

        signed  = w3.eth.account.sign_transaction(tx, PRIV_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        # Extract agentId from event logs (standard ERC-8004)
        agent_id = receipt.logs[0].topics[1].hex() if receipt.logs else "unknown"

        return {
            "agent_id":  agent_id,
            "tx_hash":   receipt.transactionHash.hex(),
            "owner":     account.address,
        }

    except Exception as e:
        print(f"Agent registration failed: {e}")
        return {"error": str(e), "agent_id": None}

if __name__ == "__main__":
    # One-time registration script
    print("\n--- ChainMind AI Agent On-Chain Registration (ERC-8004) ---")
    res = register_agent()
    if "error" in res:
        print(f"❌ Registration failed: {res['error']}")
    else:
        print(f"✅ Success! Agent ID: {int(res['agent_id'], 16)}")
        print(f"🔗 Tx Hash: {res['tx_hash']}")
        print(f"👤 Owner: {res['owner']}")
        print("-----------------------------------------------------------\n")
