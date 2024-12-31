// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

// Updated Register.sol contract
contract Register {

  address[] private _users;
  bytes32[] private _passwords; // Store hashed passwords

  mapping(address => bool) private _registered;

  function registerUser(address user, bytes32 hashedPassword) public {
    require(user != address(0), "Invalid address");
    require(hashedPassword != 0, "Password hash must be valid");
    require(!_registered[user], "User is already registered");

    _registered[user] = true;
    _users.push(user);
    _passwords.push(hashedPassword);
  }

  function loginUser(address user, bytes32 hashedPassword) public view returns (bool) {
    require(_registered[user], "User is not registered");
    for (uint i = 0; i < _users.length; i++) {
      if (_users[i] == user && _passwords[i] == hashedPassword) {
        return true;
      }
    }
    return false;
  }

  function viewUsers() public view returns (address[] memory) {
    return _users;
  }
}