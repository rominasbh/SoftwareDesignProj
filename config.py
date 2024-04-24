

class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://rominasobhani:romi@localhost/fuelmetrics'
    SQLALCHEMY_DATABASE_URI = 'postgresql://rominasobhani:romi@8.tcp.ngrok.io:16206/fuelmetrics'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'

class TestConfig(Config):
    # Using an in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    SECRET_KEY = 'test_secret_key'  # Change the secret key for testing if needed
    # Disable CSRF protection in the testing configuration to simplify request processing
    WTF_CSRF_ENABLED = False
