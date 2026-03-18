// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/AgentIdentityRegistry.sol";
import "../src/AgentReputationRegistry.sol";

contract RegistryTest is Test {
    AgentIdentityRegistry public identity;
    AgentReputationRegistry public reputation;

    address public agentOwner = address(0xACE);
    address public user = address(0xBEE);

    function setUp() public {
        identity = new AgentIdentityRegistry();
        reputation = new AgentReputationRegistry();
    }

    function test_RegisterAgent() public {
        vm.prank(agentOwner);
        uint256 agentId = identity.registerAgent(
            "ChainMind",
            "AI Security Auditor",
            "https://chainmind.ai/metadata.json"
        );

        assertEq(agentId, 1);
        
        AgentIdentityRegistry.AgentInfo memory info = identity.getAgent(agentId);
        assertEq(info.name, "ChainMind");
        assertEq(info.owner, agentOwner);
        assertTrue(info.exists);
    }

    function test_SubmitFeedback() public {
        // First register agent
        vm.prank(agentOwner);
        uint256 agentId = identity.registerAgent("CM", "Desc", "URI");

        // Now submit feedback from a user
        vm.prank(user);
        reputation.submitFeedback(agentId, 9, "Great audit, found critical reentrancy!");

        (uint256 totalScore, uint256 count) = reputation.getReputation(agentId);
        assertEq(totalScore, 9);
        assertEq(count, 1);
    }

    function test_MultipleFeedbacks() public {
        vm.prank(agentOwner);
        uint256 agentId = identity.registerAgent("CM", "Desc", "URI");

        vm.prank(user);
        reputation.submitFeedback(agentId, 10, "Perfect");

        vm.prank(address(0x123));
        reputation.submitFeedback(agentId, 8, "Good");

        (uint256 totalScore, uint256 count) = reputation.getReputation(agentId);
        assertEq(totalScore, 18);
        assertEq(count, 2);
    }

    function test_InvalidScoreReverts() public {
        vm.prank(agentOwner);
        uint256 agentId = identity.registerAgent("CM", "Desc", "URI");

        vm.prank(user);
        vm.expectRevert("Score must be 1-10");
        reputation.submitFeedback(agentId, 11, "Too high");
    }

    function test_GetNonExistentAgentReverts() public {
        vm.expectRevert("Agent not found");
        identity.getAgent(99);
    }
}
