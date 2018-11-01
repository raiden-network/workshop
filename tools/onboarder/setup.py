from setuptools import setup

setup(
    name='onboarder',
    version='1.0',
    description='',
    long_description='',
    author='Brainbot Labs Est.',
    author_email='contact@brainbot.li',
    license='MIT',
    zip_safe=False,
    install_requires=[
        'click==6.7',
        'eth-keyfile==0.5.1',
        'eth-utils==1.2.1',
        'requests==2.20.0',
    ],
    entry_points={
        'console_scripts': [
            'onboarder = onboarder:main'
        ]
    }
)
