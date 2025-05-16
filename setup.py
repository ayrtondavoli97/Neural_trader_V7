from setuptools import setup, find_packages

setup(
    name='NeuralTraderV7',
    version='1.0',
    description='Sistema AI di trading automatico su KuCoin Futures',
    author='Il Sistemista',
    packages=find_packages(exclude=["notebooks", "__pycache__"]),
    install_requires=[
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'scikit-learn>=0.24.2',
        'requests>=2.26.0',
        'torch>=1.10.0',
        'glob2>=0.7',
        'python-dateutil>=2.8.2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
