# -*- coding: utf-8 -*-

import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from PIL import Image
from os.path import join
from datetime import datetime
import config
import math

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

date_list = []
image_dict = {}
page = 10
total_pages = 0
birthday = datetime.strptime(config.birthday, '%Y-%m-%d')


def init_image_info():
    img_path = config.image_path
    img_path = os.path.join(app.root_path, img_path)

    r = os.walk(img_path)

    for dir_path, dirnames, filenames in r:
        for filename in filenames:
            if filename.endswith('.jpg'):
                pic = Image.open(join(dir_path, filename))
                image_exif = pic._getexif()

                shoot_time = datetime.strptime(image_exif[306], "%Y:%m:%d %H:%M:%S")

                shoot_date = datetime.strftime(shoot_time, "%Y-%m-%d")
                if shoot_date not in image_dict:
                    days = (shoot_time - birthday).days
                    date_list.append([shoot_date, days])
                    tmp_set = set()
                    tmp_set.add(join(os.path.basename(dir_path), filename))
                    image_dict[shoot_date] = tmp_set
                else:
                    tmp_set = image_dict[shoot_date]
                    tmp_set.add(join(os.path.basename(dir_path), filename))
                    image_dict[shoot_date] = tmp_set

    global total_pages
    total_pages = math.ceil(len(date_list) / 10)
    date_list.sort(key=lambda x: x[1], reverse=True)


@app.route('/<current_page>')
def show_image(current_page):
    result_list = date_list[(int(current_page) - 1) * 10: int(current_page) * 10]
    return render_template('hippo_show.html',
                           date_list=result_list,
                           image_dict=image_dict,
                           total_pages=total_pages,
                           current_page=int(current_page))


@app.route('/')
def home_page():
    return redirect('/1')


# @app.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
#                [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New entry was successfully posted')
#     return redirect(url_for('show_entries'))
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             flash('You were logged in')
#             return redirect(url_for('show_entries'))
#     return render_template('login.html', error=error)
#
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('show_entries'))


if __name__ == '__main__':
    init_image_info()
    app.run()
