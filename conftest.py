def pytest_markdown_docs_globals():
    import pettingzoo
    import gymnasium
    import shimmy
    return {"math": pettingzoo, "gymnasium": gymnasium, "shimmy": shimmy}

# pytest docs --markdown-docs -m markdown-docs --ignore=docs/_scripts --ignore=conf.py --ignore=docs/environments/

# pytest ../docs --markdown-docs -m markdown-docs --ignore=../docs/_scripts --ignore=../docs/conf.py