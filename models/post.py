from google.appengine.ext import db
import os
import jinja2

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
    user_id = db.IntegerProperty(required = True)
    rating = db.ListProperty(long)
    post_user_name = db.StringProperty(required = True)

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
        return Post.all().filter('post_user_name =', username).order('-created').fetch(None)
