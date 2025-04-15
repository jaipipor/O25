from setuptools import setup

setup(
    name="o25",
    version="0.1.0",
    packages=["o25"],
    install_requires=[
        "numpy>=1.21",  # Wide but safe lower bound
        "scipy>=1.7"     # Covers most Python 3.8+ installations
    ],
    python_requires=">=3.8",  # Casts a wide compatibility net
    description="Simple bidirectional Rrs correction for water remote sensing",
)
