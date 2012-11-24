from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util, template
from google.appengine.ext import db
from google.appengine.api import mail
import datetime

class HomeHandler(webapp.RequestHandler):
    def get(self):
        food = Food.all()
        template_values = {
            'food': food,
         }
        self.response.out.write(template.render('templates/signup.html', template_values))

class ThanksHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/thanks.html', locals()))

class FoodHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/add_food.html', locals()))

###User###
class User(db.Model):
    email = db.EmailProperty()
    city = db.StringProperty()
    food = db.StringListProperty(default='Surprise')
    register_date = db.DateTimeProperty(auto_now_add=True)

class AddUser(webapp.RequestHandler):
    def post(self):
        user = User()
        user.email = self.request.get('email')
        user.city = str(self.request.get('city'))
        user.food = list(self.request.get_all('food'))
        user.put()
        message = mail.EmailMessage(sender="YourDinnerDeals <jong.vincent@gmail.com>",
              subject="A User has Subscribed")
        message.to="Vincent Jong <jong.vincent@gmail.com>",
        message.body= self.request.get('email')
        message.send()
        self.redirect('/thanks')

###Food###
class Food(db.Model):
    name = db.StringProperty()
    match_yelp = db.StringListProperty(default='X')
    match_groupon = db.StringListProperty(default='X')

class AddFood(webapp.RequestHandler):
    def post(self):
        food = Food()
        food.name = str(self.request.get('food'))
        food.put()
        self.redirect('/admin')


###Menu###

class AboutUs(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/aboutus.html', {}))

class Terms(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/terms.html', {}))

def main():
    application = webapp.WSGIApplication([
        ('/', HomeHandler),
        ('/thanks', ThanksHandler),
        ('/admin', FoodHandler),
        ('/food', AddFood),
        ('/aboutus', AboutUs),
        ('/terms', Terms),
        ('/signup', AddUser)], debug=True)

    util.run_wsgi_app(application)

if __name__ == '__main__':
  main()