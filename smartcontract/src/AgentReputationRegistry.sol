// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentReputationRegistry
 * @notice Stores AI Agent audit quality feedback on Celo Alfajores.
 */
contract AgentReputationRegistry {
    struct Reputation {
        uint256 totalScore;
        uint256 feedbackCount;
    }

    mapping(uint256 => Reputation) public agentReputation;

    event FeedbackSubmitted(uint256 indexed agentId, address indexed submitter, uint8 score, string feedback);

    function submitFeedback(uint256 agentId, uint8 score, string calldata feedback) external {
        require(score <= 10, "Score must be 1-10");
        
        agentReputation[agentId].totalScore += uint256(score);
        agentReputation[agentId].feedbackCount += 1;

        emit FeedbackSubmitted(agentId, msg.sender, score, feedback);
    }

    function getReputation(uint256 agentId) external view returns (uint256 totalScore, uint256 feedbackCount) {
        Reputation memory rep = agentReputation[agentId];
        return (rep.totalScore, rep.feedbackCount);
    }
}
