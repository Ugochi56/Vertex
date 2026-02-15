from setuptools import setup, find_packages

setup(
    name='vertex-lang',
    version='0.1.0',
    description='A simple, expressive, and powerful programming language designed to be the next Python killer.',
    author='Ugochi56',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'vertex=vertex.cli:entry_point',
        ],
    },
)
