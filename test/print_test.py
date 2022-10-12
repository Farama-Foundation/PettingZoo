import os


def test_print():
    dir_names = ["butterfly", "sisl", "mpe", "atari"]

    for name in dir_names:
        root_dir = os.path.join("pettingzoo", name)

        for _dir, subdirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(_dir, file)) as f:
                        for line in f:
                            assert not line.lstrip().startswith(
                                "print"
                            ), f"File: {os.path.join(_dir, file)} has a print statement. Please remove it."
