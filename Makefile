##
# PettingZoo
#
# @file
# @version 0.1

help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test-all: ## Run ALL tests
	pytest -v --cov=pettingzoo --cov-report term

test-all-html: ## Run tests with HTML report, see `index.html` file in the `htmlcov` folder
	pytest -v --cov=pettingzoo --cov-report html --cov-report term

test-print: ## Run `print_test.py` tests
	pytest -v ./test/print_test.py

test-runner: ## Run `pytest_runner_test.py` tests
	pytest -v ./test/pytest_runner_test.py

test-param-combs: ## Run `all_parameter_combs_test.py` tests
	pytest -v ./test/all_parameter_combs_test.py

test-unwrapped: ## Run `unwrapped_test.py` tests
	pytest -v ./test/unwrapped_test.py

test-variable-env: ## Run `variable_env_test.py` tests
	pytest -v ./test/variable_env_test.py

test-doc-examples: ## Run `doc_examples_test.py` tests
	pytest -v ./test/doc_examples_test.py

test-specific-env: ## Run `specific_env_test.py` tests
	pytest -v ./test/specific_env_test.py

clean: ## Clean tmp files
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

# end
