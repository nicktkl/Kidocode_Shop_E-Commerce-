# Flask-related imports
from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy and other utility imports
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename

# Models and database
from models import Category, Product, User, Order, OrderItem, Review, Payment, db

# Date and time utilities
from datetime import datetime
import pytz
import random

# Miscellaneous imports
from itsdangerous import URLSafeTimedSerializer
import os

# Initialize reusable objects
bcrypt = Bcrypt()
mail = Mail()
