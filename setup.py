"""Setup script for Homework Grading System."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="homework-grading-system",
    version="1.0.0",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    description="Automated homework grading system with Gmail and AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/homework-grading-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "homework-grading=src.main:main",
        ],
    },
)
