# Setup configuration for pytest-dynamic-params

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pytest-dynamic-params",
    version="0.1.0",
    description="A pytest plugin for dynamic parameter generation and parametrization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cheng Pei",
    author_email="penelope_cheng@163.com",
    url="https://github.com/ProgrammerChengPei/pytest-dynamic-params",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pytest>=7.0.0"
    ],
    extras_require={
        "dev": [
            "pytest-cov",
            "flake8",
            "isort",
            "black",
            "mypy",
            "pre-commit"
        ]
    },
    classifiers=[
        "Framework :: Pytest",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "pytest11": [
            "dynamic_params = dynamic_params.plugin.pytest_plugin"
        ]
    },
    python_requires=">=3.7"
)
