from models import Comment
from bloghandler import BlogHandler

class EditComment(BlogHandler):
    def post(self, post_id, comment_id):
        comment = Comment.by_id(int(comment_id))
        content = self.request.get('comment')
        if not content:
            error = "Content required"
            self.render('comment_error.html', error = error)
            return
        if self.user.key().id() == comment.user.key().id():
            comment.content = content
            comment.put()
        self.redirect('/blog/' + post_id)
