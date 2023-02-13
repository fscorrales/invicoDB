from setuptools import setup, find_packages

setup(
    name='update_db',
    author='Fernando Corrales',
    author_email='corrales_fernando@hotmail.com',
    description="""
    Reading, processing and writing classes using invicodatpy. 
    INVICO's database it's not provide within this repo due to privacy reasons (gitignored).
    """,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    dependency_links=['http://github.com/fscorrales/invicodatpy/tarball/master#egg=invicodatpy#']
)
