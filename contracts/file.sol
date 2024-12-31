
// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

// Updated file.sol contract
contract File {

  address[] private _users;
  string[] private _files;
  string[] private _names;
  address[][] private _tokens;

  mapping(string => bool) private _fileExists;

  function addFile(address user, string memory name, string memory fileT) public {
    require(!_fileExists[fileT], "File already exists");

    _fileExists[fileT] = true;
    _users.push(user);
    _names.push(name);
    _files.push(fileT);
    _tokens.push([user]);
  }

  function viewFiles() public view returns (address[] memory, string[] memory, string[] memory, address[][] memory) {
    return (_users, _names, _files, _tokens);
  }

  function addToken(string memory file1, address user) public {
    uint i;
    for (i = 0; i < _files.length; i++) {
      if (keccak256(abi.encodePacked(file1)) == keccak256(abi.encodePacked(_files[i]))) {
        _tokens[i].push(user);
      }
    }
  }

  function removeToken(string memory file1, address user) public {
    uint i;
    uint j;
    for (i = 0; i < _files.length; i++) {
      if (keccak256(abi.encodePacked(file1)) == keccak256(abi.encodePacked(_files[i]))) {
        for (j = 0; j < _tokens[i].length; j++) {
          if (_tokens[i][j] == user) {
            delete _tokens[i][j];
          }
        }
      }
    }
  }
}
