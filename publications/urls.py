__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^(?P<publication_id>\d+)/abstract/$', 'publications.views.id.abstract', name='abstract'),
	url(r'^(?P<publication_id>\d+)/$', 'publications.views.id', name='view'),
	url(r'^year/(?P<year>\d+)/$', 'publications.views.year', name='year'),
	url(r'^tag/(?P<keyword>.+)/$', 'publications.views.keyword', name='keyword'),
	url(r'^(?P<name>.+)/$', 'publications.views.person', name='person'),

	url(r'^$', 'publications.views.year', name='index'),
)
