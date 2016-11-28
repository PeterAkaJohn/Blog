import bloghandler
from bloghandler import BlogHandler
from models import Comment

class NewComment(BlogHandler):
    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        content = self.request.get('comment')

        if content:
            comment = Comment(parent = bloghandler.blog_key(), content = content, username = self.user.name, user_id = self.user.key().id(), post_id = int(post_id))
            comment.put()
            self.redirect('/blog/' + post_id)
        else:
            error = "content, please!"
            self.render('comment_error.html', error = error)
