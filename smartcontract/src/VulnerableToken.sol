// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title VulnerableToken
 * @dev A simple contract designed to demonstrate common vulnerabilities like Reentrancy.
 */
contract VulnerableToken {
    mapping(address => uint256) public balances;
    string public name = "Vulnerable Test Token";
    string public symbol = "VTT";

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev VULNERABLE: This function is susceptible to a reentrancy attack.
     * It sends ETH before updating the state (The check-effects-interactions pattern is ignored).
     */
    function withdraw(uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Vulnerable part: Interaction before effect
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] -= _amount;
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
