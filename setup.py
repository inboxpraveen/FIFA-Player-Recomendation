"""
Setup script for FIFA Player Recommendation System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fifa-player-recommender",
    version="2.0.0",
    author="Praveen Kumar",
    author_email="inboxpraveen@example.com",
    description="AI-powered FIFA player recommendation system with dual models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inboxpraveen/FIFA-Player-Recomendation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=3.0.0",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "scikit-learn>=1.3.2",
        "scipy>=1.11.4",
        "joblib>=1.3.2",
        "python-dotenv>=1.0.0",
        "gunicorn>=21.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fifa-recommender=run:main",
        ],
    },
)

