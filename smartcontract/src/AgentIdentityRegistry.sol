// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentIdentityRegistry
 * @notice Follows ERC-8004 draft standard for AI Agent Identity on Celo.
 */
contract AgentIdentityRegistry {
    struct AgentInfo {
        string  name;
        string  description;
        address owner;
        string  metadataURI;
        bool    exists;
    }

    uint256 public agentCount;
    mapping(uint256 => AgentInfo) public agents;

    event AgentRegistered(uint256 indexed agentId, address indexed owner, string name, string metadataURI);

    function registerAgent(
        string calldata name,
        string calldata description,
        string calldata metadataURI
    ) external returns (uint256 agentId) {
        agentId = ++agentCount;
        agents[agentId] = AgentInfo({
            name:        name,
            description: description,
            owner:       msg.sender,
            metadataURI: metadataURI,
            exists:      true
        });
        emit AgentRegistered(agentId, msg.sender, name, metadataURI);
    }

    function getAgent(uint256 agentId) external view returns (AgentInfo memory) {
        require(agents[agentId].exists, "Agent not found");
        return agents[agentId];
    }
}
