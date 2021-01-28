import os

dir_names = ["butterfly", "sisl", "magent", "mpe"]

had_error = False

for name in dir_names:
    root_dir = os.path.join("pettingzoo", name)

    for _dir, subdirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(_dir, file), 'r') as f:
                    for line in f:
                        if line.lstrip().startswith("print"):
                            print("File: {} has a print statement. Please remove it.".format(os.path.join(_dir, file)))
                            had_error = True
                            break

exit(-1 if had_error else 0)
