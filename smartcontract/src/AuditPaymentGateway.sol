// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AuditPaymentGateway
/// @notice Accepts cUSD payments for ChainMind AI audits on Celo.
/// @dev Gives ChainMind genuine economic agency via stablecoin revenue.

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
}

contract AuditPaymentGateway {
    // ─── STATE ────────────────────────────────────────────────
    address public owner;
    address public cUSD;
    uint256 public auditFee;
    uint256 public totalEarned;
    uint256 public totalAudits;

    struct Payment {
        address payer;
        uint256 amount;
        uint256 timestamp;
        string  contractHash;
        bool    refunded;
    }

    mapping(uint256 => Payment)     public payments;
    mapping(address => uint256[])   public paymentsByUser;
    uint256 public paymentCount;

    // ─── EVENTS ───────────────────────────────────────────────
    event AuditPaid(uint256 indexed paymentId, address indexed payer, uint256 amount, string contractHash);
    event FeeUpdated(uint256 oldFee, uint256 newFee);
    event Withdrawn(address indexed to, uint256 amount);
    event Refunded(uint256 indexed paymentId, address indexed payer, uint256 amount);

    // ─── CONSTRUCTOR ──────────────────────────────────────────
    /// @param _cUSD  cUSD token address on Celo Alfajores
    /// @param _fee   Audit fee in cUSD wei (1e18 = 1 cUSD)
    constructor(address _cUSD, uint256 _fee) {
        owner    = msg.sender;
        cUSD     = _cUSD;
        auditFee = _fee;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only agent owner");
        _;
    }

    // ─── PAY FOR AUDIT ────────────────────────────────────────
    function payForAudit(string calldata contractHash) external returns (uint256 paymentId) {
        require(
            IERC20(cUSD).transferFrom(msg.sender, address(this), auditFee),
            "cUSD transfer failed"
        );

        paymentId = ++paymentCount;
        payments[paymentId] = Payment({
            payer:        msg.sender,
            amount:       auditFee,
            timestamp:    block.timestamp,
            contractHash: contractHash,
            refunded:     false
        });
        paymentsByUser[msg.sender].push(paymentId);

        totalEarned += auditFee;
        totalAudits++;

        emit AuditPaid(paymentId, msg.sender, auditFee, contractHash);
    }

    // ─── VERIFY PAYMENT ───────────────────────────────────────
    function verifyPayment(uint256 paymentId)
        external view
        returns (bool paid, address payer, string memory contractHash)
    {
        Payment memory p = payments[paymentId];
        return (p.amount > 0 && !p.refunded, p.payer, p.contractHash);
    }

    // ─── WITHDRAW EARNINGS ────────────────────────────────────
    function withdraw(uint256 amount) external onlyOwner {
        require(IERC20(cUSD).balanceOf(address(this)) >= amount, "Insufficient balance");
        IERC20(cUSD).transfer(owner, amount);
        emit Withdrawn(owner, amount);
    }

    // ─── UPDATE FEE ───────────────────────────────────────────
    function setFee(uint256 newFee) external onlyOwner {
        emit FeeUpdated(auditFee, newFee);
        auditFee = newFee;
    }

    // ─── REFUND ───────────────────────────────────────────────
    function refund(uint256 paymentId) external onlyOwner {
        Payment storage p = payments[paymentId];
        require(p.amount > 0 && !p.refunded, "Invalid payment");
        p.refunded = true;
        totalEarned -= p.amount;
        IERC20(cUSD).transfer(p.payer, p.amount);
        emit Refunded(paymentId, p.payer, p.amount);
    }

    // ─── READ ─────────────────────────────────────────────────
    function getAgentBalance() external view returns (uint256) {
        return IERC20(cUSD).balanceOf(address(this));
    }

    function getMyPayments() external view returns (uint256[] memory) {
        return paymentsByUser[msg.sender];
    }
}
