from bloghandler import BlogHandler
from models import Comment
import time

class DeleteComment(BlogHandler):
    def post(self, post_id, comment_id):
        if not self.user:
            self.redirect('/')
            return
        comment_user_id = self.request.get('comment_user_id')
        if self.user.key().id() == long(comment_user_id):
            comment = Comment.by_id(int(comment_id))
            comment.delete()
            time.sleep(1)
            self.redirect('/blog/' + post_id)
        else:
            self.redirect('/blog/' + post_id)
