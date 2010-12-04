from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
	(r'^$', direct_to_template, {'template': 'index.html'}),
	(r'^movie/$', direct_to_template, {'template': 'movie.html'}),
	(r'^person/$', direct_to_template, {'template': 'person.html'}),
	(r'^character/$', direct_to_template, {'template': 'character.html'}),
	(r'^user/$', direct_to_template, {'template': 'user.html'}),
)
