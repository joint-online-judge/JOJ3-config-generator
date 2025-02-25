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

## How to use?

- `joj3-config-generator convert` function is now supported, currently support three flags:

```shell
-d/--distribute: Add it without other input, it indicates script is ready to convert things other than testcases within the project
-c/--conf-root: This is where you want to put all your 'task.toml' type folders, default choice for your input can be '/home/tt/.config/joj/'
-r/--repo-root: This would be where you put your 'repo.toml' file as well as your 'immutable files', they should all be at same place, default choice for your input can be 'immutable_files', which is the folder at the position '/home/tt/.config/joj/'
```
- sample command on the server
```shell
joj3-config-generator convert -d -c /home/tt/.config/joj/ -r immutable_files
```
