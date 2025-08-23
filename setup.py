from setuptools import setup

setup(
    name='episodic',
    version='1.0.0',
    description='TV Series File Renamer',
    author='Your Name',
    py_modules=['episodic'],
    install_requires=[
        'click>=8.0.0',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
    ],
    entry_points={
        'console_scripts': [
            'episodic=episodic:main',
        ],
    },
    python_requires='>=3.7',
)
