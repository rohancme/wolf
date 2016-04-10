# Wolf
![Wolfe](img/wolfe.png)

Find problems in test coverage, add and improve it.

### Overview

Writing unit tests is quite possibly the least exciting part of a coding project. When complete, this tool aims to automate that process by:

1. Running [PITest](http://pitest.org). Finding code that is either not covered, or fails the mutation created by PITest
2. Once the problematic code is identified, run one or more auto test generation tools- randoop/evosuite/etc to generate test cases for it.
3. Now run PITest again. Keep the tests that improve PITest coverage. Submit a pull request with these new unit tests.


### Requirements

On *nix
```
# Install libxml2
sudo apt-get install libxml2 -y;
sudo apt-get install libxml2-dev -y;
sudo apt-get install libxslt1-dev -y;
sudo apt-get install zlib1g-dev -y;

# Install python
sudo apt-get install python;
sudo apt-get install python-dev;

### Running the current state of the code

#### Initialize environment

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

#### Tests

```
py.test tests
```

#### Run the tool

```
python wolf/test.py
```
*Either --repoPath or --url should be specified*
##### Arguments

```
  -h, --help            show this help message and exit
  --url URL             The Github URL for the repo
  --repoPath FOLDER     Local Path to existing maven java project
  --skipClassList FILE  Specify a file with classes that should be ignored
  --testListFile FILE   Specify output file with list of tests generated
  --numCommits INTEGER  Number of commits to check for modified files
  --subfolder FOLDER    Specify a specific subfolder for which wolf should be
                        run. NOTE: The subfolder must contain pom.xml
  --randoopPath JAR     Path to the randoop jar wolf should use
  --randoopTimeout SECONDS
                        Max time randoop should spend on generating tests
  --reduce              Attempt to reduce the number of test cases
```
