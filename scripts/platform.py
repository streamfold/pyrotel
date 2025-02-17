
PLATFORM_TAGS = {
    # MacOS builds
    "arm64-darwin": "macosx_10_9_universal2.macosx_12_3_arm64",

    # Glibc Linux builds
    # https://peps.python.org/pep-0600/#legacy-manylinux-tags
    "x86_64-linux": "manylinux2014_x86_64.manylinux_2_17_x86_64",

    # "any": "any",
}

# Map to the correct rotel agent build architecture
PLATFORM_FILE_ARCH = {
    "x86_64-linux": "x86_64-unknown-linux-gnu",
    "arm64-darwin": "aarch64-apple-darwin",
}
