"""
Setup script for EcoCompute AI.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ecocompute-ai",
    version="1.0.0",
    author="Hongping Zhang",
    author_email="your-email@example.com",
    description="A High-Fidelity Energy-Economic Auditor for Large-Scale AI Training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hongping-zh/ecocompute-ai",
    project_urls={
        "Bug Tracker": "https://github.com/hongping-zh/ecocompute-ai/issues",
        "Documentation": "https://hongping-zh.github.io/ecocompute-ai/",
        "Dataset": "https://huggingface.co/datasets/hongpingzhang/rtx5090-energy-benchmark",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
    ],
    packages=find_packages(exclude=["tests", "tests.*", "examples", "benchmarks"]),
    python_requires=">=3.8",
    install_requires=[
        "pynvml>=11.0.0",
    ],
    extras_require={
        "hf": ["transformers>=4.20.0"],
        "wandb": ["wandb>=0.12.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "all": [
            "transformers>=4.20.0",
            "wandb>=0.12.0",
            "torch>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ecocompute=ecocompute.cli:main",
        ],
    },
    keywords=[
        "energy efficiency",
        "carbon footprint",
        "green AI",
        "LLM",
        "machine learning",
        "sustainability",
        "GPU monitoring",
    ],
)
