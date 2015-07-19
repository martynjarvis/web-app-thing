from flask import render_template

from app import app


@app.route('/')
def index():
    ''' Standard home page '''
    return render_template('index.html', title="Home")
