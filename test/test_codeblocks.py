"""
This script is used to test the code blocks in the documentation.
"""

import os
from pathlib import Path

import pytest

IGNORED_FILES = ["index.md", "README.md"]
DOCS_DIR = Path(__file__).parent.parent


def parse_codeblocks():
    # Get all markdown files in the docs directory
    markdown_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    # Get all code blocks in the markdown files
    code_blocks = []
    for markdown_file in markdown_files:
        if str(Path(markdown_file).relative_to(DOCS_DIR)) in IGNORED_FILES:
            continue
        with open(markdown_file, encoding="utf-8") as f:
            lines = f.readlines()

        in_code_block = False
        for line_number, line in enumerate(lines, start=1):
            if line.startswith("```python"):
                code_blocks.append({})
                code_blocks[-1]["code"] = []
                code_blocks[-1]["filename"] = markdown_file
                code_blocks[-1]["line"] = line_number
                in_code_block = True
            elif in_code_block:
                if line.startswith("```"):
                    in_code_block = False
                else:
                    code_blocks[-1]["code"].append(line)
    return code_blocks


CODE_BLOCKS = parse_codeblocks()


@pytest.mark.parametrize("code_block", CODE_BLOCKS)
def test_codeblocks(code_block):
    code_block_rel_path = Path(code_block["filename"]).relative_to(DOCS_DIR)
    code_test_filename = f"<doctest {Path(code_block['filename']).relative_to(Path(DOCS_DIR))}[line: {code_block['line']}]>"

    print("-" * 80)
    print(f"Testing code block: {code_block_rel_path}, line: {code_block['line']}")
    exec(compile("\n".join(code_block["code"]), code_test_filename, "exec"))
    print("Result: PASSED")
