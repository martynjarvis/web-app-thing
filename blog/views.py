from blog import app
from models import Post
from decorators import login_required

from flask import render_template, flash, url_for, redirect, request

from google.appengine.api import users

@app.route('/posts')
def list_posts():
    posts = Post.all()
    return render_template('list_posts.html', posts=posts)
    
    
@app.route('/posts/new', methods = ['GET', 'POST'])
@login_required
def new_post():    
    if request.method == 'POST':
        post = Post(title = request.form['title'],
                    content = request.form['content'],
                    author = users.get_current_user())
        post.put()
        flash('Post saved on database.')
        return redirect(url_for('list_posts'))
    return render_template('new_post.html')