"""
This script reads documentation from /docs and puts it into zoo python files
"""

__author__ = "Sander Schulhoff"
__email__ = "sanderschulhoff@gmail.com"

import os
import re


def get_python_file_name(env_type, env_name):
    dir_path = os.path.join("..", "..", "pettingzoo")
    for env_file in os.listdir(os.path.join(dir_path, env_type)):
        if env_file == env_name:
            with open(
                os.path.join(dir_path, env_type, env_file, env_file + ".py"),
                encoding="utf-8",
            ) as file:
                if env_name in file.name:
                    return file.name


def insert_docstring_into_python_file(file_path, doc):
    doc = remove_front_matter(doc)
    with open(file_path, "r+", encoding="utf-8") as file:
        file_text = file.read()

        file_text = f'"""\n{doc}\n"""\n\n' + file_text

        file.seek(0)
        file.write(file_text)


def remove_front_matter(string):
    regex = re.compile(r"---\s*(\n|.)*?(---\s*\n)")
    match = regex.match(string)
    if match:
        g = match.group(0)
        return string[len(g) :]
    else:
        return string


if __name__ == "__main__":
    envs_dir = os.path.join("..", "environments")
    for env_type in os.listdir(envs_dir):
        dir_path = os.path.join("..", "environments", env_type)
        if not os.path.isdir(dir_path):
            continue
        for env_name in os.listdir(dir_path):
            if str(env_name)[-3:] == ".md":
                with open((os.path.join(dir_path, env_name)), encoding="utf-8") as file:
                    python_file_name = get_python_file_name(env_type, env_name[:-3])
                    print(python_file_name)
                    if python_file_name is not None:
                        insert_docstring_into_python_file(python_file_name, file.read())
