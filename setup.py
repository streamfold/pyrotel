from setuptools import find_packages, setup


setup(
    name="rotel",
    version="0.0.1",
    description="Rust OpenTelemetry collector",
    packages=find_packages(),
    long_description="Python modules for Streamfold's Rust OpenTelemetry Collector",
    long_description_content_type="text/markdown",
    url="https://github.com/streamfold/pyrotel",
    author="Streamfold",
    author_email="ray@streamfold.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache License 2.0",
        "Programming Language :: Python :: 3.10",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    package_data={
        'rotel': ['rotel-agent'],
    },
    python_requires=">=3.10",
)
