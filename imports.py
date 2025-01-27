import os, pytz, random, string, uuid, stripe
from models import Branch, Category, Product, User, Order, OrderItem, Review, Payment, Feedback, db
from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt, bcrypt
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from functools import wraps

csrf = CSRFProtect()