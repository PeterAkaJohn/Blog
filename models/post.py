from google.appengine.ext import db
import os
import jinja2
from user import User

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                   autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    user = db.ReferenceProperty(User, required = True)
    rating = db.ListProperty(long)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    @classmethod
    def by_id(cls, post_id):
        return Post.get_by_id(post_id, parent = blog_key())

    @classmethod
    def get_all(cls):
        return Post.all().order('-created')

    @classmethod
    def get_all_by_likes(cls):
        return Post.all().order('rating')

    @classmethod
    def get_all_user_posts(cls, username):
        user = User.by_name(username)
        return Post.all().filter('user =', user).order('-created').fetch(None)
