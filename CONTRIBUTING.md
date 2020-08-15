# Gym Contribution Guidelines

We will welcome:

- Bug reports (keep in mind that changing environment behavior should be minimized as that requires releasing a new version of the environment and makes results hard to compare across versions)
- Pull requests for bug fixes
- Documentation improvements

We are not actively looking to add new environments (other than for classic), or add API extensions, so please raise an issue or contact us directly to start a discussion before making a PR for new environments.

## Contributing

### Coding

Contributing code is done through standard github methods:

1. Fork this repo
1. Commit you code
1. Submit a pull request. It will be reviewed by maintainers and they'll give you proper feedback so you can iterate over it.

#### Considerations
- Make sure existing tests pass (run `pytest pettingzoo/tests/pytest_runner.py`)
- Make sure linter passes (run `check_style.sh`)
- Make sure your new code is properly tested and fully-covered
- Any fixes to environments should include fixes to the appropriate documentation
