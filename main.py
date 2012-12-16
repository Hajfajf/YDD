from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db
from google.appengine.api import mail
from appengine_utilities import sessions
import datetime

class HomeHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/Howdoesitwork.html', locals()))

class ThanksHandler(webapp.RequestHandler):
    def get(self):
        session = sessions.Session()
        email = session["Email"]
        self.response.out.write(template.render('templates/thanks.html', locals()))

###User###
class User(db.Model):
    email = db.EmailProperty()
    register_date = db.DateTimeProperty(auto_now_add=True)

class AddUser(webapp.RequestHandler):
    def post(self):
        session = sessions.Session()
        ### Database entry ###
        user = User()
        user.email = self.request.get('email')
        user.city = str(self.request.get('city'))
        user.put()
        ### Email to YDD ###
        session["Email"] = user.email
        message = mail.EmailMessage(sender="YourDinnerDeals <jong.vincent@gmail.com>",
              subject="A User has Subscribed")
        message.to="Vincent Jong <jong.vincent@gmail.com>",
        message.body= session["Email"]
        message.send()
        ### Email to User ###
        template_values = {
            'email': session["Email"],            
        }
        message = mail.EmailMessage(sender="YourDinnerDeals <jong.vincent@gmail.com>",
        subject="Welcome to Your Dinner Deals")
        message.to= session["Email"],
        message.body= template.render('templates/confirm-email.html', template_values) 
        message.html= template.render('templates/confirm-email.html', template_values) 
        message.send()
        ### Redirect ###
        self.redirect('/thanks')

###Menu###

class AboutUs(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/aboutus.html', {}))

class Terms(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/terms.html', {}))

class SignupHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/signup.html', {}))


def main():
    application = webapp.WSGIApplication([
        ('/', HomeHandler),
        ('/thanks', ThanksHandler),
        ('/aboutus', AboutUs),
        ('/terms', Terms),
        ('/signup', SignupHandler),
        ('/signupexe', AddUser)], debug=True)

    util.run_wsgi_app(application)

if __name__ == '__main__':
  main()