from setuptools import setup, find_packages
setup(
    name = "Game Engine",
    version = "0.1",
    packages = find_packages(),
    scripts = [],

    # Requirements
    install_requires = ['pyramid==1.4.5',
                        'sqlalchemy==0.9.3',
                        'alembic==0.6.3',
                        'zope.sqlalchemy==0.7.4',
                        'genshi==0.7',
                        'pyramid_genshi==0.1.3',
                        'requests==2.2.1'],


    package_data = {},

    # metadata for upload to PyPI
    author = "Rob Green",
    author_email = "robsgreen@gmail.com",
    description = "AI Game engine server",
    license = "BSD",
    url = "https://github.com/robsgreen/game_engine",   # project home page, if any

)