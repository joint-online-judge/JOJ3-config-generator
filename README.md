# JOJ3-config-generator

## Getting Started

### For users

1. Install [Python>=3.9](https://www.python.org/) and [pip](https://pip.pypa.io/)
2. Install the project by `pip install git+ssh://git@focs.ji.sjtu.edu.cn:2222/JOJ/JOJ3-config-generator.git`
3. Run it by `joj3-config-generator --help`

### For developers

1. Clone this repo by `git clone ssh://git@focs.ji.sjtu.edu.cn:2222/JOJ/JOJ3-config-generator.git`
2. Install [Python>=3.9](https://www.python.org/) and [PDM](https://pdm-project.org/)
3. Change dir to the repo, `cd JOJ3-config-generator`
4. Install deps by `pdm install && pdm run pre-commit install`
5. Run the cli app by `pdm run app --help`
6. Check other commands or scripts with `pdm run --list`

## How to use?

- `joj3-config-generator convert` function is now supported, currently support one argument as input, it indicates the **convert root**
  - default value on the server can be given as `/home/tt/.config/joj`
  - **NOTE:** the user should ensure that the ideal `repo.toml` file is in the sub-directory of the **convert root**
  - the intended immutable files should be placed at a sub-directory named `immutable_files` at same position as the `repo.toml` file

```shell
$ tree .
.
|- immutable_files
| |-- push.yaml
| |-- release.yaml
|-- repo.toml
```

- sample command on the server

```shell
joj3-config-generator convert /home/tt/.config/joj
```
