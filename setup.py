from setuptools import setup

setup(
    name='rita_heallis',
    version='0.1',
    py_modules=['rita_heallis'],
    install_requires=[
        'Click',
        'numpy',
        'pandas',
    ],
    entry_points='''
        [console_scripts]
        rita=rita_heallis:main
    ''',
)
