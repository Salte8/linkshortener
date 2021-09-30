import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from linker.db import get_db
import re
import random  

class Links:
    def __init__(self):
        self.bp = Blueprint('links', __name__, url_prefix='/')
        self.bp.add_url_rule('/shorten_url', 'shorten_url', self.shorten_url, methods=('GET', 'POST'))
        self.bp.add_url_rule('/mylinks', 'mylinks', self.my_links)
        self.bp.add_url_rule('/r/<short_url>','redirect',self.redirect)
        self.bp.add_url_rule('/delete_link', 'delete_link', self.delete_link, methods=('GET', 'POST'))

    def shorten_url(self):
        try:
            if request.method == 'POST':
                original_url = request.form['original_url']
                short_url = random.randrange(1000, 9999)
                user_id = g.user['id']
                db = get_db()
                error = None
                if not original_url:
                    error = 'Please enter an URL'
                elif db.execute(
                    'SELECT id FROM link WHERE original_url = ?', (original_url,)
                ).fetchone() is not None:
                    error = 'The URL {} is already shortened.'.format(original_url)

                if error is None:
                    db.execute(
                        'INSERT INTO link (original_url, short_url, user_id) VALUES (?, ?, ?)',
                        (original_url, short_url, user_id))
                    db.commit()
                    return redirect(url_for('links.mylinks'))
                flash(error)
        except Exception as e:
            print(e)
        return render_template('links/shorten_url.html')
        
    def my_links(self):
        user_id = g.user['id']

        db = get_db()
        link = db.execute(
            'SELECT * FROM link WHERE user_id = ?', [str(user_id)]
        ).fetchall()
        return render_template('links/mylinks.html', links=link)

    def redirect(self, short_url):
        try:
            db = get_db()
            error = None
            if error is None:
                link = db.execute(
                'SELECT * FROM link WHERE short_url = ?', [short_url]
                ).fetchone()
                return redirect(link['original_url'])
            else:
                error = "Unable to redirect to a valid link"
                return redirect(url_for('links.mylinks'))
        except Exception as e:
            print(e)

    def delete_link(self):
        try:
            db = get_db()
            link = db.execute(
                'DELETE FROM link WHERE original_url = ?', [request.form['original_url']]
                ).fetchone()
            db.commit()
            return redirect(url_for('links.mylinks'))
        except Exception as e:
            print(e)

        return render_template('links/mylinks.html', links=link)