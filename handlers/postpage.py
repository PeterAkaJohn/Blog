from models import Post
from models import Comment
from bloghandler import BlogHandler


def check_user_liked_post(user_id, post):
    if user_id in post.rating:
        return True

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
            if user_id == post.user.key().id():
                same_user = True
        self.render("permalink.html", post = post, comments = comments, same_user = same_user, user_id = user_id, user_liked = user_liked)
