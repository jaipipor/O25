from setuptools import setup, find_packages

setup(
    name="o25",
    version="0.1.0",
    author="Jaime Pitarch",
    author_email="jaime.pitarch@cnr.it",
    description="Bidirectional correction and IOP retrieval for aquatic optics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jaipipor/O25",
    packages=find_packages(include=["o25", "o25.*"]),
    install_requires=[
        "numpy",
        "scipy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)