import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://paxopprc:4Pk_SIhj0z1AxUgO0N12Y0BSnkaRsx-0@john.db.elephantsql.com:5432/paxopprc'
