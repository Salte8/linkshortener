import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from linker.db import get_db
import re


class Account:
    def __init__(self):
        self.bp = Blueprint('account', __name__, url_prefix='/')
        self.bp.add_url_rule('/home', 'home', self.home)
        self.bp.add_url_rule('/register', 'register', self.register, methods=('GET', 'POST'))
        self.bp.add_url_rule('/login', 'login', self.login, methods=('GET', 'POST'))
        self.bp.add_url_rule('/logout', 'logout', self.logout)
        self.bp.before_app_request(self.load_logged_in_user)

    def load_logged_in_user(self):
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

    def home(self):
        return redirect(url_for('home'))
        
    def logout(self):
        session.clear()
        return redirect(url_for('home'))

    def login(self):
        try:
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                db = get_db()
                error = None
                user = db.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
                ).fetchone()

                if user is None:
                    error = 'Incorrect username.'
                elif not check_password_hash(user['password'], password):
                    error = 'Incorrect password.'

                if error is None:
                    session.clear()
                    session['user_id'] = user['id']
                    return redirect(url_for("home"))

                flash(error)
        except Exception as e:
            print(e)
        return render_template('account/login.html')
        
    def register(self):
        try:
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                first_name = request.form['first_name']
                last_name = request.form['last_name']
                db = get_db()
                error = None

                if not username:
                    error = 'Username is required.'
                elif not password:
                    error = 'Password is required.'
                elif not first_name:
                    error = 'First Name is required.'
                elif not last_name:
                    error = 'Last Name is required'
                elif not re.match("[^@]+@[^@]+\.[^@]+", username):
                    error = 'Not a valid username'
                elif len(password) < 4:
                    error = 'Password must be atleast 4 characters'
                elif db.execute(
                    'SELECT id FROM user WHERE username = ?', (username,)
                ).fetchone() is not None:
                    error = 'User {} is already registered.'.format(username)

                if error is None:
                    db.execute(
                        'INSERT INTO user (username, password, first_name, last_name) VALUES (?, ?, ?, ?)',
                        (username, generate_password_hash(password), first_name, last_name))
                    db.commit()
                    self.login()
                    return redirect(url_for("home"))

                flash(error)
        except Exception as e:
            print(e)
            
        return render_template('account/register.html')
