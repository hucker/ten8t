from setuptools import find_packages, setup

setup(
    name="ten8t_tomlrc.py",
    version="0.1.0",
    packages=find_packages(where="src/ten8t_tomlrc.py", include=["ten8t_tomlrc.py.*"]),
    # look in 'src' and include packages in 'ten8t_tomlrc.py' and its sub-packages
    package_dir={"": "src"},
)
