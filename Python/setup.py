from setuptools import setup, find_packages

setup(
    name="o25",  # PyPI package name
    version="0.1.0",
    packages=find_packages(),  # Auto-finds 'Python' as package
    package_dir={"": "."},     # Look in root directory
    install_requires=["numpy", "scipy"],
)
