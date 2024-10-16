class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://simpleserviceuser:simpleservicepwd11@192.168.0.120/simpleservice"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JAEGER_SETTINGS = {
        "enabled": False,
        "host": "localhost",
        "port": 6831
    }


class DevelopmentConfig(Config):
    DEBUG = True
    JAEGER_SETTINGS = {
        "enabled": True,
        "host": "192.168.0.120",
        "port": 6831
    }


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use SQLite for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
