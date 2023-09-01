def pytest_markdown_docs_globals():
    import gymnasium
    import shimmy
    import supersuit

    import pettingzoo

    return {
        "math": pettingzoo,
        "gymnasium": gymnasium,
        "shimmy": shimmy,
        "supersuit": supersuit,
    }
