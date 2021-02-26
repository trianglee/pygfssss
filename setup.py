from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='pygfssss',
    version='0.0.0',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'gfssss = pygfssss.gfssss:main',
            'gfsplit = pygfssss.gfsplit:main',
            'gfcombine = pygfssss.gfcombine:main',
        ]
    },
)
