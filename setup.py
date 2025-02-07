from importlib.metadata import metadata
from setuptools import find_packages, setup, Distribution
import os
import shutil
from email.generator import BytesGenerator, Generator
from email.policy import EmailPolicy

from wheel.metadata import pkginfo_to_metadata

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    from wheel.metadata import pkginfo_to_metadata
    class MyWheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            python, abi = 'py3', 'none'
            return python, abi, plat

        def egg2dist(self, egginfo_path: str, distinfo_path: str):
            """Convert an .egg-info directory into a .dist-info directory"""

            def adios(p: str) -> None:
                """Appropriately delete directory, file or link."""
                if os.path.exists(p) and not os.path.islink(p) and os.path.isdir(p):
                    shutil.rmtree(p)
                elif os.path.exists(p):
                    os.unlink(p)

            adios(distinfo_path)

            if not os.path.exists(egginfo_path):
                # There is no egg-info. This is probably because the egg-info
                # file/directory is not named matching the distribution name used
                # to name the archive file. Check for this case and report
                # accordingly.
                import glob

                pat = os.path.join(os.path.dirname(egginfo_path), "*.egg-info")
                possible = glob.glob(pat)
                err = f"Egg metadata expected at {egginfo_path} but not found"
                if possible:
                    alt = os.path.basename(possible[0])
                    err += f" ({alt} found - possible misnamed archive file?)"

                raise ValueError(err)

            if os.path.isfile(egginfo_path):
                # .egg-info is a single file
                pkg_info = pkginfo_to_metadata(egginfo_path, egginfo_path)
                pkg_info.replace_header("Metadata-Version", "2.2")
                os.mkdir(distinfo_path)
            else:
                # .egg-info is a directory
                pkginfo_path = os.path.join(egginfo_path, "PKG-INFO")
                pkg_info = pkginfo_to_metadata(egginfo_path, pkginfo_path)
                pkg_info.replace_header("Metadata-Version", "2.2")
    
                # ignore common egg metadata that is useless to wheel
                shutil.copytree(
                    egginfo_path,
                    distinfo_path,
                    ignore=lambda x, y: {
                        "PKG-INFO",
                        "requires.txt",
                        "SOURCES.txt",
                        "not-zip-safe",
                    },
                )

                # delete dependency_links if it is only whitespace
                dependency_links_path = os.path.join(distinfo_path, "dependency_links.txt")
                with open(dependency_links_path, encoding="utf-8") as dependency_links_file:
                    dependency_links = dependency_links_file.read().strip()
                if not dependency_links:
                    adios(dependency_links_path)

            pkg_info_path = os.path.join(distinfo_path, "METADATA")
            serialization_policy = EmailPolicy(
                utf8=True,
                mangle_from_=False,
                max_line_length=0,
            )
            with open(pkg_info_path, "w", encoding="utf-8") as out:
                Generator(out, policy=serialization_policy).flatten(pkg_info)

            for license_path in self.license_paths:
                filename = os.path.basename(license_path)
                shutil.copy(license_path, os.path.join(distinfo_path, filename))

            adios(egginfo_path)


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
    version="0.0.6",
    description="Rust OpenTelemetry collector",
    packages=find_packages(),
    long_description="Python modules for Streamfold's Rust OpenTelemetry Collector",
    long_description_content_type="text/markdown",
    url="https://github.com/streamfold/pyrotel",
    author="Streamfold",
    author_email="ray@streamfold.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=6.1.0", "pkginfo>=1.12.0" ],
    },
    package_data={
        'rotel': ['rotel-agent'],
    },
    python_requires=">=3.8",
    distclass=MyDistribution
)
