"""
Allow users use the reader without python installation, just with bash.
"""

from setuptools import setup, find_packages

setup(
    name="rss_reader",
    version="1.0.1",
    description="Python RSS-reader with possibility to open from bash without installation",
    url="https://github.com/Bulachka/PythonFinalTask",
    author="Valodzina Aliaksandra",
    keywords="rss_reader",
    packages=find_packages(),
    python_requires=">=3.6, <4",
)