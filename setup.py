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
    install_requires=[
        "gym>=0.15.4",
        "pygame==2.0.0.dev6",
        "scikit-image>=0.16.2",
        "numpy>=1.18.0",
        "matplotlib>=3.1.2",
        "pymunk>=5.6.0",
        "gym[box2d]>=0.15.4",
        "python-chess",
        "rlcard >= 0.1.14",
        "pynput",
        "opencv-python"
    ],
)
