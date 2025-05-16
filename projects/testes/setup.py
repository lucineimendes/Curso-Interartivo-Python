# setup.py
from setuptools import setup, find_packages

setup(
    name="curso_interativo_python",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
    ],
    entry_points={
        "console_scripts": [
            "curso-run=projects.run:main",
        ],
    },
)
