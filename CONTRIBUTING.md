# PettingZoo Contribution Guidelines

We welcome:

- Bug reports
- Pull requests for bug fixes
- Documentation improvements

We have a bug bounty of sorts for PRs, outlined in the readme

If you're thinking about creating submitting a new environment, please contact us first. There's a very small number of things that we'd like to add in the main PettingZoo repo that we haven't already done.

## Contributing

### Coding

Contributing code is done through standard github methods:

1. Fork this repo
3. Commit your code
4. Submit a pull request. It will be reviewed by maintainers and they'll give feedback or make requests as applicable

### Considerations
- Make sure existing tests pass (`pip install -e .[all]` and then run `pytest -v` -- may also need to `apt-get`/`brew` `install swig` and `AutoROM -v`)
- Make sure your new code is properly tested and fully-covered
- Any fixes to environments should include fixes to the appropriate documentation
- Changes to environment functionality should be avoided when reasonable, and when they occur the environment version must be bumped.

### Git hooks
The CI will run several checks on the new code pushed to the PettingZoo repository. These checks can also be run locally without waiting for the CI by following the steps below:
1. [install `pre-commit`](https://pre-commit.com/#install),
2. install the Git hooks by running `pre-commit install`.

Once those two steps are done, the Git hooks will be run automatically at every new commit. The Git hooks can also be run manually with `pre-commit run --all-files`, and if needed they can be skipped (not recommended) with `git commit --no-verify`. **Note:** you may have to run `pre-commit run --all-files` manually a couple of times to make it pass when you commit, as each formatting tool will first format the code and fail the first time but should pass the second time.

### Testing shortcuts
A few _Make_ commands are provided to quickly test parts of the test suite.

To use it you first need to have _Make_ installed on your local machine:
- Linux: `sudo apt install make` (depends on the distribution/package manager)
- MacOS: `brew install make`, the command should then be available as `gmake` instead of `make` (https://formulae.brew.sh/formula/make)
- Windows: `choco install make` (https://community.chocolatey.org/packages/make)

Then `make help` should give all the available commands and you can use `Tab` when writing the command if it's too long to write. For example to run all the tests, one would write `make test-all`.
