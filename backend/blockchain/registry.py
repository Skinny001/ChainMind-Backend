from web3 import Web3
import os, json
from dotenv import load_dotenv

load_dotenv()

# Web3 Configuration
CELO_RPC = os.getenv("RPC_URL", "https://alfajores-forno.celo-testnet.org")
PRIV_KEY = os.getenv("PRIVATE_KEY", "")
REG_ADDR = os.getenv("REGISTRY_ADDRESS", "")

# Registry ABI
REGISTRY_ABI = json.loads('[{"inputs":[{"internalType":"string","name":"contractHash","type":"string"},{"internalType":"uint8","name":"riskScore","type":"uint8"},{"internalType":"uint16","name":"vulnCount","type":"uint16"},{"internalType":"uint32","name":"txCount","type":"uint32"},{"internalType":"string","name":"ipfsReport","type":"string"}],"name":"recordSimulation","outputs":[{"internalType":"uint256","name":"simulationId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"getSimulation","outputs":[{"components":[{"internalType":"address","name":"submitter","type":"address"},{"internalType":"string","name":"contractHash","type":"string"},{"internalType":"uint8","name":"riskScore","type":"uint8"},{"internalType":"uint16","name":"vulnerabilities","type":"uint16"},{"internalType":"uint32","name":"txSimulated","type":"uint32"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"ipfsReport","type":"string"},{"internalType":"bool","name":"exists","type":"bool"}],"internalType":"struct SimulationRegistry.SimulationResult","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}]')

def record_on_chain(contract_hash: str, risk_score: int, vuln_count: int, tx_count: int, ipfs_report: str = "") -> str:
    """
    Record simulation results on Celo Sepolia.
    Returns: transaction hash or error string.
    """
    if not PRIV_KEY or not REG_ADDR:
        return "blockchain_not_configured"

    try:
        w3       = Web3(Web3.HTTPProvider(CELO_RPC))
        account  = w3.eth.account.from_key(PRIV_KEY)
        registry = w3.eth.contract(address=Web3.to_checksum_address(REG_ADDR), abi=REGISTRY_ABI)

        # Build transaction
        tx = registry.functions.recordSimulation(
            contract_hash[:66],  # Hash length limit
            min(risk_score, 100),
            min(vuln_count, 65535),
            min(tx_count,   4294967295),
            ipfs_report or "ChainMind Audit Report"
        ).build_transaction({
            "from":     account.address,
            "nonce":    w3.eth.get_transaction_count(account.address),
            "gas":      250_000,
            "gasPrice": w3.eth.gas_price,
            "chainId":  11142220  # Celo Sepolia
        })

        # Sign and send
        signed   = w3.eth.account.sign_transaction(tx, PRIV_KEY)
        tx_hash  = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        # In a real app we might wait_for_transaction_receipt
        # But for speed in the audit flow, return the hash
        return tx_hash.hex()

    except Exception as e:
        print(f"On-chain record failed: {e}")
        return f"error: {str(e)[:100]}"

if __name__ == "__main__":
    # Test (mock)
    pass
    # print(record_on_chain("0xABCD", 85, 4, 1000))
