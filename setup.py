from setuptools import setup
setup(
    name='itunes2Spotify',
    version='0.1.0',
    description='Transfer albums from iTunes to Spotify',
    url='https://github.com/colbymorrison/itunes2spotify',
    author='Colby Morrison',
    author_email='colbyamorrison@gmail.com',
    license='MIT',
    install_requires=[
        'spotipy', 'click'
    ],
    packages=['itunes2Spotify'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'i2s = itunes2spotify.itunes2spotify:main'
        ]
    })