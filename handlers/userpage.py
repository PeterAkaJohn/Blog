from models import Comment
from models import Post
from bloghandler import BlogHandler

class UserPage(BlogHandler):
    def get(self, username):
        #user_id = self.user.key().id()
        posts = Post.get_all_user_posts(username)
        comments = Comment.get_all_user_comments(username)
        self.render('userpage.html', posts = posts, comments = comments)
