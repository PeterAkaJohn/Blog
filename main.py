import webapp2
import handlers

app = webapp2.WSGIApplication([('/', handlers.BlogFront),
                               ('/blog/([0-9]+)', handlers.PostPage),
                               ('/blog/newpost', handlers.NewPost),
                               ('/signup', handlers.Register),
                               ('/login', handlers.Login),
                               ('/logout', handlers.Logout),
                               ('/blog/([0-9]+)/delete', handlers.DeletePost),
                               ('/blog/([0-9]+)/like', handlers.LikePost),
                               ('/blog/([0-9]+)/edit', handlers.EditPost),
                               ('/blog/([0-9]+)/comment/add', handlers.NewComment),
                               ('/blog/([0-9]+)/comment/delete/([0-9]+)', handlers.DeleteComment),
                               ('/blog/([0-9]+)/comment/edit/([0-9]+)', handlers.EditComment),
                               ('/user/(.*)', handlers.UserPage)
                               ],
                              debug=True)
