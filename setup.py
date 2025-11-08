from setuptools import setup, find_packages

setup(
    name='it_spelling_bee',
    version='0.1.0',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    description='Italian Spelling Bee CLI (minimal MVP)',
    python_requires='>=3.9',
)
