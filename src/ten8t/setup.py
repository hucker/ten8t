"""Baseline setup file """

# pragma no cover
from setuptools import find_packages, setup  # type: ignore

# Mostly AI generated setup.
setup(
    name='ten8t',
    version='0.1.0',
    description='A tool for checking rules against filesystems, databases, and APIs',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Chuck Bass',
    author_email='chuck@acrocad.net',
    url='https://github.com/hucker/ten8t',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ten8tit=ten8t.ten8t_it:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
)
