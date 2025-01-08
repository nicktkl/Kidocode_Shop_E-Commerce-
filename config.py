from imports import *

class Config:
    #SECRET KEY configuration
    SECRET_KEY = 'kidocodeverysecretkey'

    #MAIL configuration
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

    #STRIPE configuration
    stripe.api_key = 'sk_test_51QPePWH9NhKxOPMDzZrjxX3EgYCJyKPRr98RlTmHsv22Xhw4iJqZN1VlYRkX373nFr9PcBsckwZ8qBulCRSQoCyR00PrLFdo8c'
    STRIPE_PK = 'pk_test_51QPePWH9NhKxOPMDZRHGPYxSrBltOeWG3fjxjWTWZhwQ1R7A5OUiQplz5kk9f6qQ8jYfdEvoTIC7cnLSoq6MoX2i00F10Bl0v0'