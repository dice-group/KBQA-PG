# Knowledge Base Question Answering

[develop](../../tree/develop) branch:&nbsp;
![Deployment develop](https://github.com/dice-group/KBQA-PG/actions/workflows/deploy.yml/badge.svg?branch=develop)
![Testing develop](https://github.com/dice-group/KBQA-PG/actions/workflows/lint.yml/badge.svg?branch=develop)
![Gerbil develop](<https://img.shields.io/badge/dynamic/xml?color=informational&label=Gerbil%20F1&query=(//tr[1]/td[13]/text()[1])[1]&suffix=%&url=http://kbqa-pg.cs.upb.de/gerbil/&link=http://kbqa-pg.cs.upb.de/gerbil/>)

[master](../../tree/master) branch:&nbsp;
![Deployment master](https://github.com/dice-group/KBQA-PG/actions/workflows/deploy.yml/badge.svg?branch=master)
![Testing master](https://github.com/dice-group/KBQA-PG/actions/workflows/lint.yml/badge.svg?branch=master)
![Gerbil master](<https://img.shields.io/badge/dynamic/xml?color=informational&label=Gerbil%20F1&query=(//tr[1]/td[13]/text()[1])[1]&suffix=%&url=http://kbqa-pg.cs.upb.de/dev/gerbil/&link=http://kbqa-pg.cs.upb.de/dev/gerbil/>)

<!-- [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/dice-group/KBQA-PG/develop.svg)](https://results.pre-commit.ci/latest/github/dice-group/KBQA-PG/develop) -->

Explore our QA system: [kbqa-pg.cs.upb.de](http://kbqa-pg.cs.upb.de/)

# Contributing

## Workflow

We use the workflow as described by [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow).

Follow the guidelines for [commit messages](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53).

A properly formed git commit subject line should always be able to complete the following sentence

> If applied, this commit will _\<your subject line here\>_

### Branches

We have two main branches `master` for releases and `develop` for development builds. These branches always contain completed changes and executable, formated code and will be deployed to our server. Therefore, these branches are protected and only reviewed pull requests (PR) can be merged. For every feature/topic a new branch based on develop has to be created. A PR should only contain one topic and can also be opened as a draft to get early feedback. When merging a PR, individual commits can be combined (rebased) if they describe a related change.

<table>
  <thead>
    <tr>
      <th>Instance</th>
      <th>Branch</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Release</td>
      <td>master</td>
      <td>Accepts merges from Develop</td>
    </tr>
    <tr>
      <td>Working</td>
      <td>develop</td>
      <td>Accepts merges from Features/Issues and Hotfixes</td>
    </tr>
    <tr>
      <td>Features/Issues</td>
      <td>feature/*</td>
      <td>A branch for each Feature/Issue</td>
    </tr>
    <tr>
      <td>Hotfix</td>
      <td>hotfix/*</td>
      <td>Always branch off Develop</td>
    </tr>
  </tbody>
</table>

### Folder structure

The top directory contains only configuration files that refer to this repository. Everything else is in the [KBQA](/KBQA) folder:

The end-to-end system that is automatically deployed on the VM is located in the folder [kbqa](/KBQA/kbqa).
Other topics that are not (yet) included in the end-to-end system should have their own folder.

## Code Style

We use the standard style guides.

### Python conventions

For python, this is the [PEP 8](https://www.python.org/dev/peps/pep-0008/).

Type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/)) should be used whenever possible. Static analysis can then ensure that variables and functions are used correctly.

For documenting the code we use docstrings ([PEP 257](https://www.python.org/dev/peps/pep-0257/)). Every method and class has a docstring describing its function and arguments. We follow the [numpy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html). Using consistent docstrings in the project, we automatically create a code documentation website.

## Setup

### Installation

In order to include modules from different directories, you can install the project as a package. This way the project can be splitted into different subdirectories/subprojects, which can be imported by each other. The installation can be done by running the following command in this directory:

```
pip install -e .
```

After that, you can import all source files starting with the root directory `KBQA`.

### Linters

We use the different linters to apply style rules and point out issues in code. This greatly simplifies code reviews and helps to detect errors early on.

To automatically run the linters on every commit, we use [pre-commit](https://pre-commit.com/). To setup pre-commit once run the following commands:

```
pip install pre-commit
pre-commit install
```

Now on every commit the linters defined in [pre-commit config](.pre-commit-config.yaml) will run automatically.

If you are in a hurry, you can skip the linting with `git commit --no-verify`.
But to merge into the develop branch the pipeline has to pass.

### Exclude external code files

The linters should not be applied to external code files (libraries), configs, and non-code folders as they do not have to meet our coding conventions. Therefore, these files or folders have to be excluded from the linting process. This can be done in the [pre-commit config](.pre-commit-config.yaml) by adding the files or folders to the exclude option, which is a regular expression.
Example: `exclude: ^documentation/`

### Recommended VS Code Extensions

#### Python Docstring Generator

Quickly generate docstrings for python functions in the right format by typing triple quotes.
