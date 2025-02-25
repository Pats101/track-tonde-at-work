from setuptools import setup, find_packages

setup(
    name="time-tracker",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
        "psutil>=5.9.0",
        "pywin32>=305",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="An application usage time tracker",
    python_requires=">=3.7",
) 