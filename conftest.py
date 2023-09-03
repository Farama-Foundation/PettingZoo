def pytest_markdown_docs_globals():
    import gymnasium
    import shimmy
    import supersuit

    import pettingzoo
    from pettingzoo.utils.all_modules import all_environments

    libs = {
        "pettingzoo": pettingzoo,
        "gymnasium": gymnasium,
        "shimmy": shimmy,
        "supersuit": supersuit,
    }
    # Format: {"go_v5": <module ' pettingzoo.classic.go_v5'>, ...}
    envs = {name.split("/")[1]: module for name, module in all_environments.items()}
    libs.update(envs)
    return libs
