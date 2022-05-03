#!/bin/bash

set -e

pytest ./test/print_test.py
pytest ./test/pytest_runner.py
pytest ./test/all_parameter_combs.py
pytest ./test/unwrapped_test.py
pytest ./test/variable_env_test.py
pytest ./test/doc_examples_test.py
pytest ./test/specific_env_tests.py

bash ./check_style.sh
