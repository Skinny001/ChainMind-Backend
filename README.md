# 🧠 ChainMind: Autonomous AI Security Auditor

> **Secure your Celo smart contracts with agentic AI intelligence.**

ChainMind is an autonomous security auditor built on the Celo blockchain. It leverages advanced LLMs (Gemini 2.0 & Llama 3) to scan, simulate, and patch smart contract vulnerabilities in real-time. Every audit is backed by an on-chain reputation system (ERC-8004) and recorded immutably on the Celo Sepolia testnet.

---

## 🚀 Key Features

- **🤖 Agentic AI Scanning**: Uses Gemini 2.0 Flash for surgical vulnerability detection and Groq (Llama-3.3-70b) for high-speed attack simulations.
- **⚡ 1,000+ Attack Simulations**: Automatically simulates common attack vectors (Reentrancy, Flash Loans, Logic errors) to stress-test your code.
- **🔐 On-Chain Registry**: All audit results are stored on the `SimulationRegistry` contract, creating a permanent, verifiable security trail.
- **🏆 ERC-8004 Reputation**: The auditor has an on-chain identity and builds reputation based on the accuracy and volume of its audits.
- **💳 Seamless USDC Payments**: Integrated payment gateway allowing users to pay for audits using USDC on Celo Sepolia.
- **📄 Professional PDF Reports**: One-click generation of executive security summaries for your team.

---

## 🏗️ Architecture

ChainMind is divided into three core modules:

### 1. Smart Contracts (`/smartcontract`)
The backbone of the project, handling payments and immutable logging.
- `SimulationRegistry`: Stores the results and unique IDs of every audit.
- `AuditPaymentGateway`: Handles USDC payments and fee management.
- `AgentIdentityRegistry`: Manages the AI Auditor's on-chain identity.

### 2. Backend (`/backend`)
The "Brain" of the operation, written in Python (FastAPI).
- **Audit Engine**: Integrates with Gemini & Groq APIs.
- **Simulation**: Generates attack scenarios and patches.
- **Q&A Agent**: Uses Mistral Large to answer developer questions about their specific audit results.

### 3. Frontend (`/frontend`)
A modern, dark-mode dashboard built with Next.js & Tailwind CSS.
- **Dashboard**: Real-time progress tracking of the audit.
- **History**: A dedicated archive to manage and review past scans.
- **Wallet Integration**: Powered by Reown AppKit for seamless Celo connectivity.

---

## 🛠️ Tech Stack

- **Blockchain**: Celo Sepolia
- **Smart Contracts**: Solidity, Foundry
- **AI Models**: Gemini 2.0, Groq (Llama 3.3), Mistral Large
- **Backend**: Python, FastAPI, Web3.py
- **Frontend**: Next.js 15, Tailwind CSS, ethers.js, Wagmi/AppKit

---

## 🚦 Getting Started

### Prerequisites
- Node.js & npm
- Python 3.10+
- Foundry (for smart contracts)

### Installation

1. **Clone the Repo**
   ```bash
   git clone [your-repo-url]
   cd chainmind
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Create .env and add API keys (GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY)
   uvicorn main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   # Create .env.local and add contract addresses
   npm run dev
   ```

---

## 📍 Deployed Addresses (Celo Sepolia)

| Contract | Address |
| :--- | :--- |
| **SimulationRegistry** | `0xf433656dd5aea6c43b5b87133f59b414a9d4427a` |
| **AuditPaymentGateway** | `0x655ee571133586d689e75cd2e572b91e17bc0c06` |
| **IdentityRegistry** | `0x1be6c56ceea03f4acfab1a5b9250f3987ec1f292` |
| **ReputationRegistry** | `0x1b89392afa35fb8df79541939fa546216364e8ce` |
| **USDC (Sepolia)** | `0x01C5C0122039549AD1493B8220cABEdD739BC44E` |

---

## 📜 License
MIT License. Built with ❤️ for the Celo Ecosystem.
