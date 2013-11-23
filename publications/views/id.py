__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from publications.models import Type, Publication
from django.views.decorators.cache import cache_page

@cache_page(60*60*24)
def id(request, publication_id):
	publications = Publication.objects.filter(pk=publication_id)

	if 'ascii' in request.GET:
		return render_to_response('publications/publications.txt', {
				'publications': publications
			}, context_instance=RequestContext(request), mimetype='text/plain; charset=UTF-8')

	elif 'bibtex' in request.GET:
		return render_to_response('publications/publications.bib', {
				'publications': publications
			}, context_instance=RequestContext(request), mimetype='text/x-bibtex; charset=UTF-8')

	else:
		for publication in publications:
			publication.links = publication.customlink_set.all()
			publication.files = publication.customfile_set.all()

		return render_to_response('publications/id.html', {
				'publications': publications
			}, context_instance=RequestContext(request))

def abstract(request, publication_id):
	publication = get_object_or_404(Publication, pk=publication_id)

	if publication.state == 1:
		return render(request, 'publications/abstract.html', {'publication': publication})
