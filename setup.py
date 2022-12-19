from setuptools import setup
setup(
    name='update_db',
    author='Fernando Corrales',
    author_email='corrales_fernando@hotmail.com',
    description="""
    Reading, processing and writing classes using invicodatpy. 
    INVICO's database it's not provide within this repo due to privacy reasons (gitignored).
    """,
    py_modules=['update_db'],
    dependency_links=['http://github.com/fscorrales/invicodatpy/tarball/master#egg=invicodatpy#']
)
