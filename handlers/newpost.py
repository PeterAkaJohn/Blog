import bloghandler
from bloghandler import BlogHandler
from models import Post

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
            p = Post(parent = bloghandler.blog_key(), subject = subject, content = content, user_id = self.user.key().id(), post_user_name = self.user.name)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content,error=error)
