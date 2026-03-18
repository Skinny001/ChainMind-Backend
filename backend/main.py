from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn, os, uuid, json, hashlib, traceback
from dotenv import load_dotenv

load_dotenv()

# --- BACKEND MODULES ---
from parser.contract_parser     import parse_contract
from ai.gemini_agent             import analyze_contract, generate_fixes
from ai.groq_agent               import generate_transactions
from ai.mistral_agent            import answer_question
from simulation.engine           import run_simulation
from simulation.attack_gen       import run_attacks
from blockchain.registry         import record_on_chain
from agent.reputation            import submit_audit_reputation
from agent.payments              import verify_payment_on_chain, get_agent_earnings
from agent.selfclaw              import get_verification_status

app = FastAPI(title="ChainMind AI Agent API", version="1.0.0")

# Note: allow_credentials=True + allow_origins=["*"] is restricted by browsers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"DEBUG: Incoming {request.method} request to {request.url.path}")
    try:
        response = await call_next(request)
        print(f"DEBUG: Response status code: {response.status_code}")
        return response
    except Exception as e:
        print(f"DEBUG: Unhandled exception in request: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})

# In-memory session store (Reset on restart)
simulations: dict = {}

# --- SCHEMAS ---
class QuestionRequest(BaseModel):
    simulation_id: str
    question:      str

# --- ROUTES ---

@app.get("/")
async def health_check():
    return {"status": "ChainMind AI Agent is online", "agent": "ChainMind", "chain": "Celo Alfajores"}

@app.post("/api/simulate")
async def simulate_contract(
    file: UploadFile = File(...),
    payment_id: int = Form(...)
):
    """
    Main Endpoint: 
    1. Verify cUSD payment (Economic Agency)
    2. Parse contract
    3. AI Vulnerability Detection (Gemini)
    4. Fast Simulation Pattern Generation (Groq)
    5. Foundry Execution
    6. Generate Attacks & Fixes
    7. Record Result on Celo (Audit Trail)
    8. Update Reputation (ERC-8004)
    """
    # 1. Verify Payment
    payment_status = verify_payment_on_chain(payment_id)
    if not payment_status.get("paid", True): # Allow True for dev if not configured
        raise HTTPException(402, "Payment required — ensure cUSD is paid.")

    # 2. Setup simulation ID and read code
    sim_id      = str(uuid.uuid4())[:8]
    source_code = (await file.read()).decode("utf-8")
    
    # 3. Parse Contract
    parsed = parse_contract(source_code)
    
    # 4. AI Vulnerability Analysis (Gemini)
    vulnerabilities = analyze_contract(source_code)
    
    # 5. Fast Transaction Pattern Generation (Groq)
    transactions = generate_transactions(parsed["summary"], count=1000)
    
    # 6. Execute Foundry Simulation (SimulationRegistry)
    sim_results = run_simulation(source_code, transactions)
    
    # 7. Generate Attack Scenarios
    attacks = run_attacks(source_code, vulnerabilities)
    
    # 8. Generate Patched Code (Gemini)
    fixes = generate_fixes(source_code, vulnerabilities)
    
    # 9. Compute Overall Risk Score
    # Simple logic: severity weightage
    sev_weights = {"CRITICAL": 40, "HIGH": 20, "MEDIUM": 10, "LOW": 5, "INFO": 1}
    risk_score = 0
    for vuln in vulnerabilities:
        risk_score += sev_weights.get(vuln.get("severity"), 0)
    risk_score = min(100, risk_score)
    
    # 10. Record on Celo (Audit Trail)
    contract_hash = hashlib.sha256(source_code.encode()).hexdigest()
    tx_hash = record_on_chain(contract_hash, risk_score, len(vulnerabilities), len(transactions))
    
    # 11. Update Reputation on ERC-8004
    # Agent builds reputation for every completed audit
    rep_score = min(10, max(1, 10 - len(vulnerabilities) // 2))
    submit_audit_reputation(
        agent_id=1,  # Manual registration ID
        score=rep_score,
        contract_name=parsed["contract_name"],
        vuln_count=len(vulnerabilities)
    )
    
    # Final Result
    result = {
        "simulation_id":  sim_id,
        "contract_name":  parsed["contract_name"],
        "risk_score":     risk_score,
        "vulnerabilities": vulnerabilities,
        "transactions":   sim_results,
        "attacks":        attacks,
        "fixes":          fixes,
        "on_chain_tx":    tx_hash,
        "contract_hash":  contract_hash,
    }
    
    simulations[sim_id] = result
    return JSONResponse(result)


@app.get("/api/simulation/{id}")
async def get_simulation(id: str):
    if id not in simulations:
        raise HTTPException(404, "Simulation results not found")
    return simulations[id]


@app.post("/api/query")
async def query_results(req: QuestionRequest):
    """NL Q&A logic via Mistral."""
    if req.simulation_id not in simulations:
        raise HTTPException(404, "Simulation not found")
    
    answer = answer_question(simulations[req.simulation_id], req.question)
    return {"answer": answer}


@app.get("/api/agent/stats")
async def agent_stats():
    """Agent economic stats & reputation."""
    earnings   = get_agent_earnings()
    is_verified = get_verification_status(os.getenv("PRIVATE_KEY", ""))
    
    return {
        "agent_name":    os.getenv("AGENT_NAME", "ChainMind"),
        "is_verified":   is_verified,
        "identity_reg":  os.getenv("ERC8004_IDENTITY_REGISTRY"),
        "earnings":      earnings
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
