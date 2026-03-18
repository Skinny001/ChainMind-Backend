// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import {Currency} from "v4-core/types/Currency.sol";

/**
 * @title IPointsHookFactory
 * @notice Interface for the PointsHookFactory contract
 * @dev This interface contains only the essential functions needed for deployment scripts
 */
interface IPointsHookFactory {
    /**
     * @notice Deploy a new PointsHook with pre-mined address and salt
     * @param targetToken The token that users need to buy to earn points
     * @param pointsRatio How many units to spend per 1 point
     * @param baseURI The base URI for the ERC1155 metadata
     * @param feePercentage Fee percentage in basis points (0-1000)
     * @param feeThreshold Fee threshold for triggering lottery
     * @param salt Pre-computed salt from off-chain mining
     * @param expectedHookAddress Expected address from off-chain mining
     * @return hook The address of the deployed hook
     */
    function deployPointsHook(
        Currency targetToken,
        uint256 pointsRatio,
        string memory baseURI,
        uint256 feePercentage,
        uint256 feeThreshold,
        bytes32 salt,
        address expectedHookAddress
    ) external returns (address hook);
    
    /**
     * @notice Creator-friendly function with sensible defaults and pre-mined salt
     * @param tokenAddress Token address for the points system
     * @param pointsPerToken Points awarded per token spent
     * @param metadataURI Base URI for metadata
     * @param salt Pre-computed salt from off-chain mining
     * @param expectedHookAddress Expected address from off-chain mining
     * @return hook The address of the deployed hook
     */
    function createPointsSystem(
        address tokenAddress,
        uint256 pointsPerToken,
        string memory metadataURI,
        bytes32 salt,
        address expectedHookAddress
    ) external returns (address hook);
    
    /**
     * @notice Compute the expected hook address for given parameters (for off-chain mining)
     * @param targetToken The target token
     * @param pointsRatio Points ratio
     * @param baseURI Base URI
     * @param feePercentage Fee percentage
     * @param feeThreshold Fee threshold
     * @param salt The salt to use for CREATE2
     * @return hookAddress The predicted hook address
     */
    function computeHookAddress(
        Currency targetToken,
        uint256 pointsRatio,
        string memory baseURI,
        uint256 feePercentage,
        uint256 feeThreshold,
        bytes32 salt
    ) external view returns (address hookAddress);
    
    /**
     * @notice Compute the expected hook address for createPointsSystem parameters
     * @param tokenAddress Token address
     * @param pointsPerToken Points per token
     * @param metadataURI Metadata URI
     * @param salt The salt to use for CREATE2
     * @return hookAddress The predicted hook address
     */
    function computePointsSystemAddress(
        address tokenAddress,
        uint256 pointsPerToken,
        string memory metadataURI,
        bytes32 salt
    ) external view returns (address hookAddress);
    
    /**
     * @notice Get the platform fee percentage
     * @return The platform fee percentage in basis points
     */
    function platformFEE() external view returns (uint256);
    
    /**
     * @notice Get all hooks deployed by a specific address
     * @param deployer The deployer address
     * @return Array of hook addresses
     */
    function getHooksByDeployer(address deployer) external view returns (address[] memory);
    
    /**
     * @notice Get total number of deployed hooks
     * @return The total hook count
     */
    function getHookCount() external view returns (uint256);
    
    /**
     * @notice Get hook at specific index
     * @param index The index
     * @return The hook address
     */
    function getHookAtIndex(uint256 index) external view returns (address);
    
    /**
     * @notice Get the fee recipient address
     * @return The fee recipient address
     */
    function feeRecipient() external view returns (address);
}
