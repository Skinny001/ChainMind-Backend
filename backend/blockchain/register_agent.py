from web3 import Web3
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Web3 Configuration
CELO_RPC = os.getenv("RPC_URL", "https://alfajores-forno.celo-testnet.org")
PRIV_KEY = os.getenv("PRIVATE_KEY", "")
IDENTITY_REGISTRY_ADDR = os.getenv("ERC8004_IDENTITY_REGISTRY", "")

# Identity Registry ABI (Simplified for registration)
IDENTITY_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "description", "type": "string"},
            {"internalType": "string", "name": "metadataURI", "type": "string"}
        ],
        "name": "registerAgent",
        "outputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "name": "getAgent",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "name", "type": "string"},
                    {"internalType": "string", "name": "description", "type": "string"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "string", "name": "metadataURI", "type": "string"},
                    {"internalType": "bool", "name": "exists", "type": "bool"}
                ],
                "internalType": "struct AgentIdentityRegistry.AgentInfo",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def register_ai_agent(name: str, description: str, metadata_uri: str = "https://chainmind.ai") -> str:
    """
    Register the AI agent on Celo Sepolia using ERC-8004.
    """
    if not PRIV_KEY or not IDENTITY_REGISTRY_ADDR:
        return "Error: Blockchain credentials or contract address not found in .env"

    try:
        w3 = Web3(Web3.HTTPProvider(CELO_RPC))
        if not w3.is_connected():
            return "Error: Could not connect to Celo RPC"

        account = w3.eth.account.from_key(PRIV_KEY)
        registry = w3.eth.contract(address=Web3.to_checksum_address(IDENTITY_REGISTRY_ADDR), abi=IDENTITY_ABI)

        print(f"Registering agent '{name}' from account: {account.address}...")

        # Build transaction
        tx = registry.functions.registerAgent(
            name,
            description,
            metadata_uri
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 300_000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 11142220  # Celo Sepolia Testnet
        })

        # Sign and send
        signed = w3.eth.account.sign_transaction(tx, PRIV_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"Transaction sent! Hash: {tx_hash.hex()}")
        print("Waiting for confirmation...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"Successfully registered! TX: {tx_hash.hex()}")
            return tx_hash.hex()
        else:
            return "Error: Transaction failed on-chain"

    except Exception as e:
        print(f"Registration failed: {e}")
        return f"error: {str(e)}"

if __name__ == "__main__":
    name = os.getenv("AGENT_NAME", "ChainMind")
    description = os.getenv("AGENT_DESCRIPTION", "AI Security Auditor")
    register_ai_agent(name, description)
