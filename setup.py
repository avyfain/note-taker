from setuptools import setup, find_packages

setup(
    name='note-taking-app',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pywhispercpp',
        'sounddevice',
    ],
    entry_points={
        'console_scripts': [
            'note-taking-app = src.main:main',
        ],
    },
)