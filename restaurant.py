from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import util, template
from credentials import CJCredentials

class CJAPI(webapp.RequestHandler):
    def get(self):

        #apicall = fetch('https://product-search.api.cj.com/v2/product-search?authorization=' + CJCredentials().developer_key + '&website-id=3813599&advertiser-ids=867296')

        self.response.out.write('https://product-search.api.cj.com/v2/product-search?authorization=' + str(CJCredentials().developer_key) + '&website-id=' + str(CJCredentials().website_id) + '&advertiser-ids=867296')

        #xml = parseString(apicall.content)

def main():
    application = webapp.WSGIApplication([
        ('/restaurant', CJAPI)], debug=True)
    
    util.run_wsgi_app(application)

if __name__ == "__main__":
    main()