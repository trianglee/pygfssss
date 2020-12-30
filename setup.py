from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='pyssss',
    version='0.0.0',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'gfssss = pyssss.gfssss:main',
            'gfsplit = pyssss.gfsplit:main',
            'gfcombine = pyssss.gfcombine:main',
        ]
    },
)
