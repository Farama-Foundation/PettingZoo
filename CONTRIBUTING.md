# PettingZoo Contribution Guidelines

We welcome:

- Bug reports
- Pull requests for bug fixes
- Documentation improvements

We have a bug bounty of sorts for PRs, outlined in the readme

We are not actively looking to add new environments (other than for classic) or other additional functionality. Please raise an issue or contact us directly before starting on a new classic environment.

## Contributing

### Coding

Contributing code is done through standard github methods:

1. Fork this repo
1. Commit your code
1. Submit a pull request. It will be reviewed by maintainers and they'll give feedback or make requests as applicable

#### Considerations
- Make sure existing tests pass (run `pytest pettingzoo/tests/pytest_runner.py`)
- Make sure linter passes (run `check_style.sh`)
- Make sure your new code is properly tested and fully-covered
- Any fixes to environments should include fixes to the appropriate documentation
- Changes to environment functionality should be avoided when reasonable, and when they occur the environment version must be bumped.
