// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title VulnerableToken
 * @dev A deliberately broken token contract for testing security scanners.
 * Features: Reentrancy, Unauthorized Minting, Weak Flashloans, and Owner Griefing.
 */
contract VulnerableToken {
    string public name = "Vulnerable ChainMind Token";
    string public symbol = "VCT";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    address public owner;

    mapping(address => uint256) public balances;
    mapping(address => uint256) public staked;
    mapping(address => bool) public isBlacklisted;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    constructor(uint256 initialSupply) {
        owner = msg.sender;
        _mint(msg.sender, initialSupply * 10**decimals);
    }

    function balanceOf(address account) public view returns (uint256) {
        return balances[account];
    }

    // ─── VULNERABILITY 1: Unauthorized Minting ──────────────────────
    // Missing onlyOwner modifier!
    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }

    function _mint(address to, uint256 amount) internal {
        totalSupply += amount;
        balances[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    // ─── VULNERABILITY 2: Griefing (Self-Blacklisting) ──────────────
    // Anyone can blacklist anyone!
    function blacklist(address account) public {
        isBlacklisted[account] = true;
    }

    function transfer(address to, uint256 amount) public returns (bool) {
        require(!isBlacklisted[msg.sender], "Blacklisted");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    // ─── VULNERABILITY 3: Reentrancy In Stake/Withdraw ──────────────
    function stake(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        staked[msg.sender] += amount;
        emit Staked(msg.sender, amount);
    }

    /**
     * @dev VULNERABLE: Interaction before effect. 
     * If the amount is larger than internal balance, it tries to send ETH (just for demo).
     */
    function withdraw(uint256 amount) public payable {
        require(staked[msg.sender] >= amount, "Insufficient stake");
        
        // Reentrancy vulnerable: external call before state change
        (bool success, ) = msg.sender.call{value: 0}(""); // Triggering fallback
        require(success, "Withdraw failed");

        staked[msg.sender] -= amount;
        balances[msg.sender] += amount;
        emit Withdrawn(msg.sender, amount);
    }

    // ─── VULNERABILITY 4: Insecure Flash Loan ───────────────────
    function flashLoan(uint256 amount, address borrower, bytes calldata data) public {
        uint256 balanceBefore = balances[address(this)];
        require(balances[address(this)] >= amount, "Insufficient pool");

        // Send tokens
        balances[address(this)] -= amount;
        balances[borrower] += amount;

        // Callback
        (bool success, ) = borrower.call(data);
        require(success, "Callback failed");

        // VULNERABLE: Weak repayment check (doesn't check if balance actually returned)
        // require(balances[address(this)] >= balanceBefore, "Flash loan not repaid");
    }
}
