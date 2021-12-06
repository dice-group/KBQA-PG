# Knowledge Base Question Answering

![action_deploy develop](https://github.com/dice-group/KBQA-PG/actions/workflows/deploy.yml/badge.svg?branch=develop)

Explore our QA system: [kbqa-pg.cs.upb.de](http://kbqa-pg.cs.upb.de/)

# Contributing

## Workflow

We use the workflow as described by [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow).
Follow the guidelines for [commit messages](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53).

### Branches

We have two main branches `master` and `develop`. These branches always contain working end-to-end code and will be deployed to our server. These branches are protected and only reviewed pull requests can be merged.

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

## Code Style

We use the standard style guides.

### Python conventions

For python, this is the [PEP 8](https://www.python.org/dev/peps/pep-0008/).

Type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/)) should be used whenever possible. With this static analysis can ensure that variables and functions are used correctly.

For documenting the code we use docstrings ([PEP 257](https://www.python.org/dev/peps/pep-0257/)). Every method and class has a docstring describing its function and arguments. With the help of this, we automatically create a documentation website.

## Setup

We use the different linters to apply style rules and point out issues in code. This greatly simplifies code reviews and helps to detect errors early on.

To automatically run the linters on every commit, we use [pre-commit](https://pre-commit.com/). To setup pre-commit once run the following commands:

```
pip install pre-commit
pre-commit install
```

Now on every commit the linters defined in [pre-commit config](.pre-commit-config.yaml) will run automatically.

If you are in a hurry, you can skip the linting with `git commit --no-verify`.
But to merge into the develop branch the pipeline has to pass.
