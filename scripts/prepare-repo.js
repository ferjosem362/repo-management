// This script will prepare the repository changing the package.json
const fs = require('fs');
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout,
});
const { execSync } = require('child_process');

const package = JSON.parse(fs.readFileSync(`${__dirname}/../package.json`, { encoding: 'utf-8' }));

const readme = fs.readFileSync(`${__dirname}/README.md.template`, { encoding: 'utf-8' });

const updatePackage = () => {
    // saves the new package.json file
    fs.writeFileSync(`${__dirname}/../package.json`, JSON.stringify(package, null, 4));
};

const updateGitURL = () => {
    // update the git from package.json to be the correct one data

    // get the name of the url
    const gitName = execSync('git config --get remote.origin.url').toString().trim();

    // update!
    package.repository.url = gitName;
    package.bugs.url = `${gitName.split('.git')[0]}/issues`;
    package.homepage = `${gitName.split('.git')[0]}#readme`;
};

const executeCMD = (cmd) => execSync(cmd).toString().trim();

const versionChecker = /HEAD^(\d+\.)?(\d+\.)?(\*|\d+)$/;

console.log('\x1b[33m** Repository preparation **\x1b[0m');
console.log(`
Please, answer the next questions to prepare the repository for you:
`);
readline.question('\x1b[32mName of the reporistory\x1b[0m: ', name => {
    if (!name) {
        console.log('You need to set a name for the repository!');
        process.exit(0);
    }

    package.name = name;

    readline.question('\x1b[32mSmall description\x1b[0m: ', description => {
        package.description = description;

        readline.question('\x1b[32mStart version (1.0.0 by default)\x1b[0m: ', version => {
            // check if the version complains the way you set it
            if (version && versionChecker.test(version)) {
                package.version = version;
            }

            // update git part
            updateGitURL();

            // update package
            updatePackage();

            // update readme with template one
            fs.writeFileSync(`${__dirname}/../README.md`, readme.replace('{REPO-NAME}', name));

            // show message
            console.log(`
Repository updated sucessfully!.

Executing \x1b[33mnpm install\x1b[0m... please wait...
            `);

            executeCMD('npm install');

            console.log(`
\x1b[32m** Installation finished **\x1b[0m
            `);

            // exit in the good way
            process.exit(0);
        });
    });
});