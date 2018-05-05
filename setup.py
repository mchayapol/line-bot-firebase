from setuptools import setup

setup(
    name='linefirebase',
    version='0.9',
    description='A LINE Bot function which saves all chat contents to firebase',
    author='Chayapol Moemeng',
    author_email='mchayapol@gmail.com',
    packages=['linefirebase'],
    install_requires=['line-bot-sdk', 'firebase-admin'],
)
