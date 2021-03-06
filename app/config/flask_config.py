from os import path, getenv

DATABASE__USER = getenv('DATABASE__USER')
DATABASE__PWD = getenv('DATABASE__PWD')
DATABASE__HOST = getenv('DATABASE__HOST')
DATABASE__DBS = getenv('DATABASE__DBS')

class BaseConfig(object):
    'Base config class'
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = getenv(
        'SQLALCHEMY_DATABASE_URI',
        f'postgresql+psycopg2://{DATABASE__USER}:{DATABASE__PWD}@{DATABASE__HOST}/{DATABASE__DBS}'
    )


class ProductionConfig(BaseConfig):
    'Production specific config'
    DEBUG = False


class StagingConfig(BaseConfig):
    'Staging specific config'
    DEBUG = True


class DevelopmentConfig(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True
    DEVELOPMENT = True