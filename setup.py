from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent.resolve()
long_description = (this_directory / "README.rst").read_text(encoding="utf-8")


setup(
    name="dicetables",
    version="4.0.2",
    description="get all combinations for any set of dice",
    long_description=long_description,
    keywords="dice, die, statistics, table, probability, combinations",
    url="http://github.com/eric-s-s/dice-tables",
    author="Eric Shaw",
    author_email="shaweric01@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Games/Entertainment :: Role-Playing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=["tests", "time_trials", "docs"]),
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
