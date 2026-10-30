"""
Setup script for FIFA Player Recommendation System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fifa-player-recommender",
    version="2.1.0",
    author="Praveen Kumar",
    author_email="inboxpraveen.17@gmail.com",
    description="Find similar EA SPORTS FC 25 players with cosine similarity over 35 attributes, served by a Flask app and JSON API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inboxpraveen/FIFA-Player-Recomendation",
    packages=find_packages(exclude=["tests", "tests.*"]),
    py_modules=["run"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.11",
    install_requires=[
        "flask>=3.0.0",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "joblib>=1.3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fifa-recommender=run:main",
        ],
    },
)

