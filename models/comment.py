from google.appengine.ext import db
from user import User
from post import Post

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Comment(db.Model):
    content = db.TextProperty(required=True)
    date = db.DateTimeProperty(auto_now_add = True)
    user = db.ReferenceProperty(User, required=True)
    post = db.ReferenceProperty(Post, required=True)

    @classmethod
    def by_id(cls, comment_id):
        return Comment.get_by_id(comment_id, parent = blog_key())

    @classmethod
    def get_all(cls, post_id):
        post = Post.by_id(post_id)
        return Comment.all().filter('post =', post).order('-date').fetch(None)

    @classmethod
    def get_all_user_comments(cls, username):
        user = User.by_name(username)
        return Comment.all().filter('user =', user).order('-date').fetch(None)
