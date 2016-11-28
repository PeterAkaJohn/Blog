from bloghandler import BlogHandler
from models import Post

class LikePost(BlogHandler):
    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return
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
