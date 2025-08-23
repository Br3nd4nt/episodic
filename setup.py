from setuptools import setup

setup(
    name='episodic',
    version='1.0.0',
    description='Automatically rename TV series files using episode titles from IMDB',
    author='br3nd4nt',
    py_modules=['episodic'],
    install_requires=[
        'click>=8.0.0',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'colorama>=0.4.6',
    ],
    entry_points={
        'console_scripts': [
            'episodic=episodic:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Video',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ],
    keywords=['tv', 'series', 'rename', 'imdb', 'episodes', 'video', 'files', 'automation'],
    project_urls={
        'Homepage': 'https://github.com/br3nd4nt/episodic',
        'Repository': 'https://github.com/br3nd4nt/episodic.git',
        'Issues': 'https://github.com/br3nd4nt/episodic/issues',
    },
)
