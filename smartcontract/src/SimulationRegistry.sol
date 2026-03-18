// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title SimulationRegistry
/// @notice Stores ChainMind audit results immutably on Celo Alfajores.
/// @dev Each simulation gets a unique ID and on-chain record.
contract SimulationRegistry {
    // ─── STRUCTS ──────────────────────────────────────────────
    struct SimulationResult {
        address  submitter;
        string   contractHash;
        uint8    riskScore;
        uint16   vulnerabilities;
        uint32   txSimulated;
        uint256  timestamp;
        string   ipfsReport;
        bool     exists;
    }

    // ─── STATE ────────────────────────────────────────────────
    uint256 public simulationCount;
    mapping(uint256 => SimulationResult) public simulations;
    mapping(address => uint256[])        public simulationsByUser;

    // ─── EVENTS ───────────────────────────────────────────────
    event SimulationRecorded(
        uint256 indexed simulationId,
        address indexed submitter,
        string  contractHash,
        uint8   riskScore,
        uint256 timestamp
    );

    // ─── RECORD ───────────────────────────────────────────────
    function recordSimulation(
        string  calldata contractHash,
        uint8            riskScore,
        uint16           vulnCount,
        uint32           txCount,
        string  calldata ipfsReport
    ) external returns (uint256 simulationId) {
        simulationId = ++simulationCount;
        simulations[simulationId] = SimulationResult({
            submitter:       msg.sender,
            contractHash:    contractHash,
            riskScore:       riskScore,
            vulnerabilities: vulnCount,
            txSimulated:     txCount,
            timestamp:       block.timestamp,
            ipfsReport:      ipfsReport,
            exists:          true
        });
        simulationsByUser[msg.sender].push(simulationId);
        emit SimulationRecorded(simulationId, msg.sender, contractHash, riskScore, block.timestamp);
    }

    // ─── READ ─────────────────────────────────────────────────
    function getSimulation(uint256 id) external view returns (SimulationResult memory) {
        require(simulations[id].exists, "Simulation not found");
        return simulations[id];
    }

    function getMySimulations() external view returns (uint256[] memory) {
        return simulationsByUser[msg.sender];
    }

    function getLatestSimulation() external view returns (SimulationResult memory) {
        require(simulationCount > 0, "No simulations yet");
        return simulations[simulationCount];
    }
}
