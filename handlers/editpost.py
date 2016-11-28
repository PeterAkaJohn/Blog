from models import Post
from bloghandler import BlogHandler

class EditPost(BlogHandler):
    def post(self, post_id):
        post = Post.by_id(int(post_id))
        subject = self.request.get('subject')
        content = self.request.get('content')
        if self.user.key().id() == post.user_id:
            if not content or not subject:
                error_edit = "Subject and content required"
                self.render('editpost.html', error = error_edit)
            else:
                #post = Post.by_id(int(post_id))
                post.content = content
                post.subject = subject
                post.put()
                self.redirect('/blog/' + post_id)
