from imports import *

class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'nurulizzatihayat@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'tmcn fehq fttp smym')
    MAIL_DEFAULT_SENDER = ('Kidocode', 'nurulizzatihayat@gmail.com')

    # SQLAlchemy configurations
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+mysqlconnector://root:dlvvkxl@127.0.0.1:3306/ecommerceNEW')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
