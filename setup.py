from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='SocketSwap',
    version='0.1.1',    
    description='SocketSwap is a python package that allows to proxy any third-party libraries traffic through a local TCP Proxy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fyx99/SocketSwap',
    author='fxy99',
    author_email='',
    license='MIT',
    packages=['SocketSwap'],
    install_requires=[],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)