from setuptools import setup, find_packages

setup(
    name='ml-intrusion-detection',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A machine learning-based Intrusion Detection System (IDS)',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'flask',
        'pyyaml',
        'jupyter'
    ],
    entry_points={
        'console_scripts': [
            'ml-ids=main:main',
        ],
    },
)