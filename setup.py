from importlib.metadata import metadata
from setuptools import find_packages, setup, Distribution

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class MyWheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            python, abi = 'py3', 'none'
            return python, abi, plat

    class MyDistribution(Distribution):

        def __init__(self, *attrs):
            Distribution.__init__(self, *attrs)
            self.cmdclass['bdist_wheel'] = MyWheel

        def is_pure(self):
            return False

        def has_ext_modules(self):
            return True

except ImportError:
    class MyDistribution(Distribution):
        def is_pure(self):
            return False

        def has_ext_modules(self):
            return True

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
        "dev": ["pytest>=7.0", "twine>=6.1.0"],
    },
    package_data={
        'rotel': ['rotel-agent'],
    },
    python_requires=">=3.10",
    distclass=MyDistribution
)
