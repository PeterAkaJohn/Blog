import os
import re
import random
import hashlib
import hmac
import logging
import time
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'secret'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))



# users
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

##### blog stuff

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
    def get_all_user_posts(cls, username):
        return Post.all().filter('post_user_name =', username).order('-created').fetch(None)

class Comment(db.Model):
    """docstring for Comment."""
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


class DeletePost(BlogHandler):
    def post(self):
        if not self.user:
            self.redirect('/')
            return
        post_id = self.request.get('post_id')
        post_user_id = self.request.get('post_user_id')
        logging.info(post_id)
        if self.user.key().id() == long(post_user_id):
            #post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #post = db.get(post_key)
            post = Post.by_id(int(post_id))
            post.delete()
            time.sleep(1)
            self.redirect('/')
        else:
            self.redirect('/blog/' + post_id)

class DeleteComment(BlogHandler):
    """docstring for DeleteComment."""
    def post(self):
        if not self.user:
            self.redirect('/')
            return
        post_id = self.request.get('post_id')
        comment_id = self.request.get('comment_id')
        comment_user_id = self.request.get('comment_user_id')
        if self.user.key().id() == long(comment_user_id):
            #post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #post = db.get(post_key)
            comment = Comment.by_id(int(comment_id))
            comment.delete()
            time.sleep(1)
            self.redirect('/blog/' + post_id)
        else:
            self.redirect('/blog/' + post_id)


class EditPost(BlogHandler):
    def post(self):
        post_id = self.request.get('post_id')
        post_user_id = self.request.get('post_user_id')
        content = self.request.get('new-content')
        if self.user.key().id() == long(post_user_id):
            #post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #post = db.get(post_key)
            post = Post.by_id(int(post_id))
            post.content = content
            post.put()
            #time.sleep(2)
            self.redirect('/blog/' + post_id)

class EditComment(BlogHandler):
    """docstring for EditComment."""
    def post(self):
        post_id = self.request.get('post_id')
        comment_user_id = self.request.get('comment_user_id')
        comment_id = self.request.get('comment_id')
        content = self.request.get('new-comment')
        if not content:
            content = " "
        if self.user.key().id() == long(comment_user_id):
            #post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #post = db.get(post_key)
            comment = Comment.by_id(int(comment_id))
            comment.content = content
            comment.put()
            #time.sleep(2)
        self.redirect('/blog/' + post_id)

class LikePost(BlogHandler):
    """docstring for LikePost."""
    def post(self):
        if not self.user:
            self.redirect('/login')
            return
        post_id = self.request.get('post_id')
        post_user_id = self.request.get('post_user_id')
        user_id = self.user.key().id()
        if user_id != long(post_user_id):
            post = Post.by_id(int(post_id))
            if user_id in post.rating:
                post.rating.remove(user_id)
            else:
                post.rating.append(user_id)
            post.put()
        self.redirect('/blog/' + post_id)

class BlogFront(BlogHandler):
    def get(self):
        posts = Post.get_all()
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        post = Post.by_id(int(post_id))
        comments = Comment.get_all(int(post_id))

        if not post:
            self.error(404)
            return
        same_user = False
        user_id = False
        user_liked = None
        if self.user:
            user_id = self.user.key().id()
            user_liked = check_user_liked_post(user_id, post)
            if user_id == post.user_id:
                same_user = True

        self.render("permalink.html", post = post, comments = comments, same_user = same_user, user_id = user_id, user_liked = user_liked)

def check_user_liked_post(user_id, post):
    if user_id in post.rating:
        return True


class NewComment(BlogHandler):
    """docstring for NewComment."""
    def post(self):
        if not self.user:
            self.redirect('/login')
            return

        post_id = self.request.get('post_id')
        content = self.request.get('comment')

        if content:
            comment = Comment(parent = blog_key(), content = content, username = self.user.name, user_id = self.user.key().id(), post_id = int(post_id))
            comment.put()
            self.redirect('/blog/' + post_id)
        else:
            error = "content, please!"
            self.redirect('/blog/'+ post_id)
            #self.render("permalink.html",error_comment=error)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')
            return

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content, user_id = self.user.key().id(), post_user_name = self.user.name)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content,error=error)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class UserPage(BlogHandler):
    """docstring for UserPage."""
    def get(self, username):
        #user_id = self.user.key().id()
        posts = Post.get_all_user_posts(username)
        comments = Comment.get_all_user_comments(username)
        self.render('userpage.html', posts = posts, comments = comments)


class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/signup')

app = webapp2.WSGIApplication([('/', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/post/delete', DeletePost),
                               ('/blog/post/edit', EditPost),
                               ('/blog/post/like', LikePost),
                               ('/blog/post/addcomment', NewComment),
                               ('/blog/post/comment/delete', DeleteComment),
                               ('/blog/post/comment/edit', EditComment),
                               ('/user/(.*)', UserPage)
                               ],
                              debug=True)
