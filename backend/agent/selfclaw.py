import os, json, requests
from dotenv import load_dotenv

load_dotenv()

SELFCLAW_URL = os.getenv("SELFCLAW_API_URL", "https://api.ai.self.xyz")


def verify_agent_with_selfclaw(agent_wallet_address: str) -> dict:
    """
    Verify ChainMind agent via SelfClaw.
    Links the agent's public key to a verified human identity using ZK proofs.
    """
    try:
        # SelfClaw is verified on-chain, this endpoint checks public status
        response = requests.get(
            f"{SELFCLAW_URL}/v1/verify/{agent_wallet_address}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "verified":    data.get("verified", False),
                "agent_address": agent_wallet_address,
                "proof_hash":  data.get("proofHash", ""),
                "verified_at": data.get("verifiedAt", ""),
            }
        else:
            return {
                "verified": False,
                "message": "Agent not yet verified. Visit https://app.ai.self.xyz to verify.",
                "agent_address": agent_wallet_address,
            }
    except Exception as e:
        return {
            "verified": False,
            "error": str(e),
            "message": "Could not reach SelfClaw API. Ensure Self AI is available in your region."
        }


def get_verification_status(agent_address: str) -> bool:
    """Quick boolean check for verified status."""
    result = verify_agent_with_selfclaw(agent_address)
    return result.get("verified", False)
