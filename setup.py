from setuptools import setup, find_packages

setup(
    name="time_tracker",
    version="0.1.0",
    packages=find_packages(include=['time_tracker', 'time_tracker.*']),
    python_requires=">=3.7",
    install_requires=[
        "psutil>=5.9.0",
        "pywin32>=305",
        "PyQt6>=6.4.0",
        "PyQt6-Qt6>=6.4.0",
        "PyQt6-sip>=13.4.0",
        "PyQt6-Charts>=6.4.0",
    ],
    extras_require={
        'test': [
            'pytest>=7.0.0',
            'pytest-mock>=3.10.0',
            'pytest-cov>=4.1.0',
            'pytest-qt>=4.2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'time-tracker=time_tracker.__main__:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="An application usage time tracker",
) 