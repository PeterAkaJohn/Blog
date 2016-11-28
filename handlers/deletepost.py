from bloghandler import BlogHandler
from models import Post
import time
import logging

class DeletePost(BlogHandler):
    def post(self, post_id):
        if not self.user:
            self.redirect('/')
            return
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
