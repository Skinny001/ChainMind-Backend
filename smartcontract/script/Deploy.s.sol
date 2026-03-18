// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/SimulationRegistry.sol";
import "../src/AuditPaymentGateway.sol";
import "../src/AgentIdentityRegistry.sol";
import "../src/AgentReputationRegistry.sol";

contract DeployChainMind is Script {
    // Celo Sepolia USDC Address (Circle Faucet)
    address constant USDC_SEPOLIA = 0x01C5C0122039549AD1493B8220cABEdD739BC44E;
    // Celo Alfajores cUSD Address
    address constant CUSD_ALFAJORES = 0x874069Fa1Eb16D44d622F2e0Ca25eeA172369bC1;

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 1. Deploy SimulationRegistry (Audit Trail)
        SimulationRegistry registry = new SimulationRegistry();
        console.log("SimulationRegistry deployed at:", address(registry));

        // Detect network and pick correct token and fee
        address token;
        uint256 fee;
        if (block.chainid == 11142220) {
           token = USDC_SEPOLIA;
           fee   = 1 * 10**6; // 1.00 USDC (6 decimals)
           console.log("Network detected: Celo Sepolia");
           console.log("Using USDC as payment token");
        } else {
           token = CUSD_ALFAJORES;
           fee   = 1 * 10**18; // 1.00 cUSD (18 decimals)
           console.log("Network detected: Celo Alfajores");
           console.log("Using cUSD as payment token");
        }

        // 2. Deploy AuditPaymentGateway
        AuditPaymentGateway gateway = new AuditPaymentGateway(token, fee);
        console.log("AuditPaymentGateway deployed at:", address(gateway));

        // 3. Deploy IdentityRegistry (ERC-8004)
        AgentIdentityRegistry identity = new AgentIdentityRegistry();
        console.log("AgentIdentityRegistry deployed at:", address(identity));

        // 4. Deploy ReputationRegistry (ERC-8004)
        AgentReputationRegistry reputation = new AgentReputationRegistry();
        console.log("AgentReputationRegistry deployed at:", address(reputation));

        vm.stopBroadcast();
    }
}

// HOW TO DEPLOY:
// source .env
// forge script script/Deploy.s.sol:DeployChainMind --rpc-url $CELO_RPC_URL --broadcast --verify -vvvv
