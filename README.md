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
