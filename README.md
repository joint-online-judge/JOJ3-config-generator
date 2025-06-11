# JOJ3-forge

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a98f9aa020874a93bc791a7616fccf21)](https://app.codacy.com/gh/joint-online-judge/JOJ3-config-generator/dashboard)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/a98f9aa020874a93bc791a7616fccf21)](https://app.codacy.com/gh/joint-online-judge/JOJ3-config-generator/dashboard)

## Introduction

JOJ3-forge is a CLI tool that generates configuration files for [JOJ3](https://github.com/joint-online-judge/JOJ3).

## Getting Started

### For users

1. Install [Python>=3.9](https://www.python.org/) and [pip](https://pip.pypa.io/)
2. (Optional) Create a virtual environment, check [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
3. Install/Upgrade the project by `pip install --force-reinstall --upgrade git+ssh://git@focs.ji.sjtu.edu.cn:2222/JOJ/JOJ3-config-generator.git`
4. Run it by `joj3-forge --help`

### For developers

1. Clone this repo by `git clone ssh://git@focs.ji.sjtu.edu.cn:2222/JOJ/JOJ3-config-generator.git`
2. Install [Python>=3.9](https://www.python.org/) and [PDM](https://pdm-project.org/)
3. Change dir to the repo, `cd JOJ3-config-generator`
4. Install deps by `pdm install && pdm run pre-commit install`
5. Run the cli app by `pdm run app --help`
6. Check other commands or scripts with `pdm run --list`

## How to use?

Run `joj3-forge --help` to get basic CLI usage information.

### `convert`

- `joj3-forge convert` function is now supported, currently support one argument as input, it indicates the **convert root*
  - default value on the server should be given as `/home/tt/.config/joj`
  - **NOTE:** the user should ensure that the ideal `repo.toml` file is in the sub-directory of the **convert root**
  - the intended immutable files should be placed at a sub-directory named `immutable_files` at same position as the `repo.toml` file
  - a sample directory tree as follows

```shell
$ tree -a
home
`-- tt
    |-- .cache
    `-- .config
        `-- joj
            |-- hidden
            |   |-- ex1
            |   |   |-- case1.in
            |   |   |-- case1.out
            |   |   |-- conf.json
            |   |   `-- conf.toml
            |   |-- immutable_files
            |   |   |-- push.yaml
            |   |   `-- release.yaml
            |   |-- p1
            |   |   |-- case1.in
            |   |   |-- case1.out
            |   |   |-- conf.json
            |   |   `-- conf.toml
            |   `-- repo.toml
            |-- students
            |   |-- ex1
            |   |   |-- case1.in
            |   |   |-- case1.out
            |   |   |-- conf.json
            |   |   `-- conf.toml
            |   |-- immutable_files
            |   |   |-- push.yaml
            |   |   `-- release.yaml
            |   |-- p1
            |   |   |-- case1.in
            |   |   |-- case1.out
            |   |   |-- conf.json
            |   |   `-- conf.toml
            |   `-- repo.toml
            |-- students.csv
            `-- tools
                |-- .clang-tidy
                |-- compile
                `-- helper.sh
```

- sample command on the server

```shell
joj3-forge convert /home/tt/.config/joj
```
