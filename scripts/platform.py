# SPDX-License-Identifier: Apache-2.0

PLATFORM_TAGS = {
    # MacOS builds
    "arm64-darwin": "macosx_10_9_universal2.macosx_12_3_arm64",

    # Glibc Linux builds
    # https://peps.python.org/pep-0600/#legacy-manylinux-tags
    "x86_64-linux": "manylinux_2_34_x86_64",
    "aarch64-linux": "manylinux_2_34_aarch64",

    # "any": "any",
}

# Map to the correct rotel agent build architecture
PLATFORM_FILE_ARCH = {
    "x86_64-linux": "x86_64-unknown-linux-gnu",
    "aarch64-linux": "aarch64-unknown-linux-gnu",
    "arm64-darwin": "aarch64-apple-darwin",
}

PLATFORM_PY_VERSIONS = {
    "3.10",
    "3.11",
    "3.12",
    "3.13",
}
