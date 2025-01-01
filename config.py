class Config:
    #secretkey
    SECRET_KEY = 'kidocodeverysecretkey'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:dlvvkxl@127.0.0.1:3306/ecommerceNEW'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'nurulizzatihayat@gmail.com'
    MAIL_PASSWORD = 'tmcn fehq fttp smym'
    MAIL_DEFAULT_SENDER = ('Kidocode', 'nurulizzatihayat@gmail.com')