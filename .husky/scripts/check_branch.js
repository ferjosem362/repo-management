const { execSync } = require('child_process');

const cli = (cmd) => execSync(cmd).toString().trim();

const validNames = /HEAD|^[a-z0-9-]*\/[a-z0-9-]*$/;
const branchName = cli('git rev-parse --abbrev-ref HEAD');
const branchNameIsValid = validNames.test(branchName);

if (!branchNameIsValid) {
  console.log('\r\n\x1b[31m** Atention: There was a problem on your branch name **\x1b[0m')
  console.log(`\x1b[33mBranch name '\x1b[31m${branchName}\x1b[0m' is not valid\x1b[0m`);
  console.log('Please use lowercase alphanumeric words separated by hyphens\r\n');
  process.exit(1);
}