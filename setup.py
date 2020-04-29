from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='PettingZoo',
    version="0.1.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.5",
    data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
)
