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

extras = {
    "atari": ["multi_agent_ale_py", "pygame==2.0.0.dev10"],
    "classic": ["python-chess", "rlcard >= 0.2.5", "python-shogi", "hanabi_learning_environment"],
    "butterfly": ["pygame==2.0.0.dev10", "pymunk==5.6.0"],
    "magent": ["magent"],
    "mpe": [],
    "sisl": ["pygame==2.0.0.dev10", "opencv-python", "scikit-image>=0.16.2", "gym[box2d]>=0.17.2", "box2d-py"],
    "tests": ["pynput"]
}

extras["all"] = list(set().union(extras["atari"], extras["classic"], extras["butterfly"], extras["magent"], extras["mpe"], extras["sisl"]))


setup(
    name='PettingZoo',
    version="1.0.1",
    author='PettingZoo Team',
    author_email="justinkterry@gmail.com",
    description="Gym for multi-agent reinforcement learning",
    url='https://github.com/PettingZoo-Team/PettingZoo',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Reinforcement Learning", "game", "RL", "AI", "gym"],
    python_requires=">=3.6",
    data_files=[("", ["LICENSE.txt"])],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gym>=0.17.2",
        "numpy>=1.18.0",
        "gym>=0.17.2"
    ],
    extras_requires=extras,
)
