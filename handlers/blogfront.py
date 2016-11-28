from bloghandler import BlogHandler
from models import Post

class BlogFront(BlogHandler):
    def get(self):
        posts_created = Post.get_all()
        posts_popular = Post.get_all_by_likes()
        self.render('front.html', posts_created = posts_created, posts_popular = posts_popular)
