from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from models import db, Operator
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return render_template('login.html', error="Invalid credentials")

    operator = Operator.query.filter_by(name=username).first()
    if operator and bcrypt.checkpw(password.encode('utf-8'), operator.passcode_hash.encode('utf-8')):
        login_user(operator)
        return redirect(url_for('dashboard'))

    return render_template('login.html', error="Invalid credentials")

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
