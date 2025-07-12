import setuptools

setuptools.setup(
    name = "gst",
    packages = {".": "gst"},
    version = "0.1.6",
    license="MIT",
    description = "Git status tool",
    author = "Chris Gravel",
    author_email = "cpagravel@gmail.com",
    url = "https://github.com/cpagravel/gst-python",
    download_url = "https://github.com/cpagravel/gst-python/archive/0.1.6.tar.gz",
    keywords = ["git", "git status", "git workflow"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
  ],
  entry_points = {
      'console_scripts': [
          'gst = gst:main'
      ]
  },
)