import bloghandler
from bloghandler import BlogHandler
from models import Comment
from models import Post

class NewComment(BlogHandler):
    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        content = self.request.get('comment')

        if content:
            post = Post.by_id(int(post_id))
            comment = Comment(parent = bloghandler.blog_key(), content = content, user = self.user, post = post)
            comment.put()
            self.redirect('/blog/' + post_id)
        else:
            error = "content, please!"
            self.render('comment_error.html', error = error)
