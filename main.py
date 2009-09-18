#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import wsgiref.handlers


class Article(db.Model):
	author = db.UserProperty()
	title = db.StringProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
	deleted = db.BooleanProperty()	#for delete state
	password = db.StringProperty()

class MainHandler(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			urlLinktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			urlLinktext = 'Login'
			
		template_values = {
			'url': url,
			'url_linktext': urlLinktext,
			}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))


class EditHandler(webapp.RequestHandler):      
	def get(self):
		key = db.Key(self.request.get('key'))
		article = Article.all().ancestor(key).get()
		user = users.get_current_user()
		template_values = {
			'user': user,
			'article': article,
			}
		path = os.path.join(os.path.dirname(__file__), 'write.html')
		self.response.out.write(template.render(path, template_values))


class WriteHandler(webapp.RequestHandler):      
	def get(self):
		user = users.get_current_user()
		template_values = {
			'user': user,
			}
		path = os.path.join(os.path.dirname(__file__), 'write.html')
		self.response.out.write(template.render(path, template_values))
	def post(self):
		user = users.get_current_user()
		password = self.request.get('password')
		if self.request.get('key'):
			key = db.Key(self.request.get('key'))
			article = Article.all().ancestor(key).get()
			if user or password == greeting.password:
				greeting.deleted = True
				db.put(greeting)
			else:
				self.response.out.write('modify failed')
				return
		article = Article()
		if user:
			article.author = user
		if password:
			article.password = password
		article.deleted = False
		article.content = self.request.get('content')
		article.title = self.request.get('title')
		article.put()
		if self.request.get('key'):
			self.response.out.write('modify ok')
		else:
			self.response.out.write('post ok')


class ListHandler(webapp.RequestHandler):      
	def get(self):
		user = users.get_current_user()
		page = self.request.get('page')
		if page:
			#todo : paging 
			pass
		articleQuery = Article.all().filter('deleted =', False).order('-date')
		articles = articleQuery.fetch(10)
		template_values = {
			'articles': articles,
			'user':user,
			}

		path = os.path.join(os.path.dirname(__file__), 'list.html')
		self.response.out.write(template.render(path, template_values))


class DeleteHandler(webapp.RequestHandler):      
	def get(self):
		#todo : delete
		self.response.out.write('Hello world!')


def main():
  application = webapp.WSGIApplication([('/', MainHandler),
      ('/write', WriteHandler),
      ('/edit', EditHandler),
      ('/list', ListHandler),
      ('/del', DeleteHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
