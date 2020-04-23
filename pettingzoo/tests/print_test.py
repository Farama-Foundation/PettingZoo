import os


# add more dir names here
dir_names = ["gamma", "sisl", "magent", "mpe"]

for name in dir_names:
    root_dir = os.path.join(os.pardir, name)

    for _dir, subdirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(_dir, file), 'r') as f:
                    for line in f:
                        if line.lstrip().startswith("print"):
                            print("File: {} has a print statement. Please remove it.".format(os.path.join(_dir, file)))
                            break
