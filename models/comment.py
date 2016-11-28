from google.appengine.ext import db

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Comment(db.Model):
    content = db.TextProperty(required=True)
    date = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=True)
    user_id = db.IntegerProperty(required = True)
    post_id = db.IntegerProperty(required = True)

    @classmethod
    def by_id(cls, comment_id):
        return Comment.get_by_id(comment_id, parent = blog_key())

    @classmethod
    def get_all(cls, post_id):
        return Comment.all().filter('post_id =', post_id).order('-date').fetch(None)

    @classmethod
    def get_all_user_comments(cls, username):
        return Comment.all().filter('username =', username).order('-date').fetch(None)
