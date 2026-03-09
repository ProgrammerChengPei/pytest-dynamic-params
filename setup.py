from setuptools import find_packages, setup

setup(
    name="pytest-dynamic-params",
    version="0.1.0",
    packages=find_packages(where="src"),  # 只查找src目录下的包
    package_dir={"": "src"},
    install_requires=["pytest"],
    entry_points={
        "pytest11": [
            "dynamic-params = dynamic_params.plugin"
        ]
    },
    classifiers=[
        "Framework :: Pytest",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)