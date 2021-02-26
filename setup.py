from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()

setup(
    name='pygfssss',
    version='1.0.1',
    description="Python implementation of Shamir's Secret Sharing Scheme, using polynomials over GF(256)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trianglee/pygfssss",
    author="Nimrod Zimerman",
    author_email="zimerman@fastmail.fm",
    license="Apache License 2.0",
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pygfssss = pygfssss.gfssss:main',
            'pygfsplit = pygfssss.gfsplit:main',
            'pygfcombine = pygfssss.gfcombine:main',
        ]
    },
)
