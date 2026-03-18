from web3 import Web3
import os, json
from dotenv import load_dotenv

load_dotenv()

# Web3 Configuration
CELO_RPC     = os.getenv("RPC_URL", "https://alfajores-forno.celo-testnet.org")
GATEWAY_ADDR = os.getenv("PAYMENT_GATEWAY_ADDRESS", "")
CUSD_ADDR    = os.getenv("CUSD_TOKEN_ADDRESS", "0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1")

# AuditPaymentGateway ABI (verification + balance functions)
GATEWAY_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"paymentId","type":"uint256"}],"name":"verifyPayment","outputs":[{"internalType":"bool","name":"paid","type":"bool"},{"internalType":"address","name":"payer","type":"address"},{"internalType":"string","name":"contractHash","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getAgentBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalEarned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalAudits","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"auditFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')


def verify_payment_on_chain(payment_id: int) -> dict:
    """
    Verify that a developer has paid the cUSD audit fee.
    Called by the backend before running the AI simulation.
    Returns: {paid: bool, payer: str, contract_hash: str}
    """
    if not GATEWAY_ADDR:
        # Fallback to free audits during development if gateway not configured
        return {"paid": True, "payer": "free_mode", "contract_hash": ""}

    try:
        w3 = Web3(Web3.HTTPProvider(CELO_RPC))
        gateway = w3.eth.contract(address=Web3.to_checksum_address(GATEWAY_ADDR), abi=GATEWAY_ABI)
        
        # Call verifyPayment(id) view function
        paid, payer, contract_hash = gateway.functions.verifyPayment(payment_id).call()
        
        return {
            "paid":          paid,
            "payer":         payer,
            "contract_hash": contract_hash,
        }
    except Exception as e:
        print(f"Payment verification failed: {e}")
        return {"paid": False, "payer": "", "contract_hash": "", "error": str(e)}


def get_agent_earnings() -> dict:
    """
    Get the agent's current cUSD balance and total statistics.
    """
    if not GATEWAY_ADDR:
        return {"balance_cusd": 0, "total_earned_cusd": 0, "total_audits": 0, "fee_cusd": 0}

    try:
        w3 = Web3(Web3.HTTPProvider(CELO_RPC))
        gateway = w3.eth.contract(address=Web3.to_checksum_address(GATEWAY_ADDR), abi=GATEWAY_ABI)
        
        balance       = gateway.functions.getAgentBalance().call()
        total_earned  = gateway.functions.totalEarned().call()
        total_audits  = gateway.functions.totalAudits().call()
        fee           = gateway.functions.auditFee().call()

        return {
            "balance_cusd":       balance / 1e18,
            "total_earned_cusd":  total_earned / 1e18,
            "total_audits":       total_audits,
            "fee_cusd":           fee / 1e18,
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test (mock)
    pass
    # print(verify_payment_on_chain(1))
