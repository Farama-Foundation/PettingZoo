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

#### Considerations
- Make sure existing tests pass (`pip install -r requirements.txt` and then run `pytest test/pytest_runner.py` -- may also need to apt-get/brew install swig)
- Make sure linter passes (run `check_style.sh`)
- Make sure your new code is properly tested and fully-covered
- Any fixes to environments should include fixes to the appropriate documentation
- Changes to environment functionality should be avoided when reasonable, and when they occur the environment version must be bumped.
