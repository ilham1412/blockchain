// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Copyright Registry
/// @notice Register proof of work ownership on blockchain
contract CopyrightRegistry {
    address public owner;

    struct WorkRegistration {
        string workId;           // Unique work identifier
        string workTitle;        // Title of the work
        string workType;         // Type: image, text, music, video, etc.
        string contentHash;      // SHA-256 hash of the work content
        address creator;         // Wallet address of the creator
        uint256 timestamp;       // Registration timestamp
        string metadata;         // Additional info (optional)
    }

    // Mapping from workId to registration details
    mapping(string => WorkRegistration) public registrations;
    
    // Mapping from creator address to their work IDs
    mapping(address => string[]) public creatorWorks;
    
    // Mapping from content hash to work ID (prevents duplicate content)
    mapping(string => string) public hashToWorkId;

    event WorkRegistered(
        string indexed workId,
        string workTitle,
        address indexed creator,
        string contentHash,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Register a new work on the blockchain
    /// @param workId Unique identifier for the work
    /// @param workTitle Title of the work
    /// @param workType Type of work (image, text, music, etc.)
    /// @param contentHash SHA-256 hash of the work content
    /// @param metadata Additional metadata (JSON string or URI)
    function registerWork(
        string memory workId,
        string memory workTitle,
        string memory workType,
        string memory contentHash,
        string memory metadata
    ) public {
        // Check if work ID already exists
        require(
            bytes(registrations[workId].workId).length == 0,
            "Work ID already registered"
        );
        
        // Check if content hash already registered
        require(
            bytes(hashToWorkId[contentHash]).length == 0,
            "This content already registered with different ID"
        );

        // Create new registration
        registrations[workId] = WorkRegistration({
            workId: workId,
            workTitle: workTitle,
            workType: workType,
            contentHash: contentHash,
            creator: msg.sender,
            timestamp: block.timestamp,
            metadata: metadata
        });

        // Add to creator's work list
        creatorWorks[msg.sender].push(workId);
        
        // Map hash to work ID
        hashToWorkId[contentHash] = workId;

        emit WorkRegistered(workId, workTitle, msg.sender, contentHash, block.timestamp);
    }

    /// @notice Verify if a content hash matches a registered work
    /// @param workId The work identifier
    /// @param contentHash The hash to verify
    /// @return bool True if hash matches
    function verifyWork(string memory workId, string memory contentHash) 
        public 
        view 
        returns (bool) 
    {
        return keccak256(abi.encodePacked(registrations[workId].contentHash)) == 
               keccak256(abi.encodePacked(contentHash));
    }

    /// @notice Get full details of a registered work
    /// @param workId The work identifier
    /// @return WorkRegistration struct with all details
    function getWorkDetails(string memory workId) 
        public 
        view 
        returns (WorkRegistration memory) 
    {
        require(
            bytes(registrations[workId].workId).length > 0,
            "Work not found"
        );
        return registrations[workId];
    }

    /// @notice Check if content hash is already registered
    /// @param contentHash The hash to check
    /// @return string The work ID if registered, empty string otherwise
    function checkContentExists(string memory contentHash) 
        public 
        view 
        returns (string memory) 
    {
        return hashToWorkId[contentHash];
    }

    /// @notice Get all works registered by a creator
    /// @param creator The creator's address
    /// @return string[] Array of work IDs
    function getCreatorWorks(address creator) 
        public 
        view 
        returns (string[] memory) 
    {
        return creatorWorks[creator];
    }

    /// @notice Get total number of works by a creator
    /// @param creator The creator's address
    /// @return uint256 Number of works
    function getCreatorWorkCount(address creator) 
        public 
        view 
        returns (uint256) 
    {
        return creatorWorks[creator].length;
    }
}