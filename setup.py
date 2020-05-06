from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = ""
    header_count = 0
    for line in fh:
        if line.startswith("##"):
            header_count += 1
        if header_count < 2:
            long_description += line
        else:
            break

setup(
    name='PettingZoo',
    version="0.1.3",
    author='PettingZoo Team',
    author_email="justinkterry@gmail.com",
    description="Gym for multi-agent reinforcement learning",
    url='https://github.com/PettingZoo-Team/PettingZoo',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Reinforcement Learning", "game", "RL", "AI", "gym"],
    python_requires=">=3.5",
    data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gym>=0.15.4",
        "pygame==2.0.0.dev6",
        "scikit-image>=0.16.2",
        "numpy>=1.18.0",
        "pymunk>=5.6.0",
        "gym[box2d]>=0.15.4",
        "python-chess",
        "rlcard >= 0.1.14",
        "pynput",
        "opencv-python"
    ],
)
