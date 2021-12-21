__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.bibtex import parse
from publications.models import Publication, Type
from string import split, join
from datetime import datetime
from pprint import pprint

# mapping of months
MONTHS = {
	'jan': 1, 'january': 1,
	'feb': 2, 'february': 2,
	'mar': 3, 'march': 3,
	'apr': 4, 'april': 4,
	'may': 5,
	'jun': 6, 'june': 6,
	'jul': 7, 'july': 7,
	'aug': 8, 'august': 8,
	'sep': 9, 'september': 9,
	'oct': 10, 'october': 10,
	'nov': 11, 'november': 11,
	'dec': 12, 'december': 12}


def import_bibtex(request):
	if request.method == 'POST':
		errors = {}

		# try to parse BibTex
		bib = parse(request.POST['bibliography'])

		# check for errors
		if not bib:
			if not request.POST['bibliography']:
				errors['bibliography'] = 'This field is required.'

		errors, publications = import_bibtex_utility(bib)

		if not errors and not publications:
			errors['bibliography'] = 'No valid BibTex entries found.'

		if errors:
			# some error occurred
			return render_to_response(
				'admin/publications/import_bibtex.html', {
					'errors': errors,
					'title': 'Import BibTex',
					'types': Type.objects.all(),
					'request': request},
				RequestContext(request))
		else:
			try:
				# save publications
				for publication in publications:
					publication.user = request.user
					if not publication.external:
						publication.external = False

					publication.save()
			except Exception as e:
				msg = 'Some error occured during saving of publications.'
			else:
				if len(publications) > 1:
					msg = 'Successfully added ' + str(len(publications)) + ' publications.'
				else:
					msg = 'Successfully added ' + str(len(publications)) + ' publication.'

			# show message
			messages.info(request, msg)

			# redirect to publication listing
			return HttpResponseRedirect('../')
	else:
		return render_to_response(
			'admin/publications/import_bibtex.html', {
				'title': 'Import BibTex',
				'types': Type.objects.all(),
				'request': request},
			RequestContext(request))

def import_bibtex_utility(bib):
		# container for error messages
		errors = {}

		# publication types
		types = Type.objects.all()

		if not errors:
			publications = []

			# try adding publications
			for entry in bib:
				if entry.has_key('title') and \
				   entry.has_key('year'):
					# parse authors
					if not entry.has_key('author'):
						entry['author'] = ''

					authors = entry['author']
					# authors = split(entry['author'], ' and ')
					# for i in range(len(authors)):
					# 	author = split(authors[i], ',')
					# 	author = [author[-1]] + author[:-1]
					# 	authors[i] = join(author, ' ')
					# authors = join(authors, ', ')

					if entry.has_key('timestamp'):
						try:
							timestamp = datetime.strptime(entry['timestamp'], "%d.%m.%Y")
						except ValueError:
							timestamp = datetime.strptime(entry['timestamp'], "%Y.%m.%d")
					else:
						timestamp = datetime.now()

					# add missing keys
					keys = [
						'journal',
						'booktitle',
						'publisher',
						'institution',
						'url',
						'doi',
						'isbn',
						'keywords',
						'note',
						'abstract',
						'month',
						'volume',
						'number',
						'owner',
						'language',
						'editor',
						'pages',
						'address',
						'organization',
						'volume',
						'number',
						'school',
						'chapter',
						'howpublished',
						'issn',
						'comment',
						'series',
						'edition'						
						]

					for key in keys:
						if not entry.has_key(key):
							entry[key] = ''

					# map integer fields to integers
					if entry['month']:
						if MONTHS.get(entry['month'].lower(), 0):
							entry['month'] = MONTHS.get(entry['month'].lower(), 0)
						else:
							input_text = entry['month'].lower()
							for month_name in MONTHS:
								if input_text.find(month_name) >= 0:
									entry['month'] = MONTHS.get(month_name)
									break
					if type(0) != type(entry['month']):
						entry['month'] = 0

					# entry['month'] = MONTHS.get(entry['month'].lower(), 0)
					entry['volume'] = entry.get('volume', None)
					entry['number'] = entry.get('number', None)

					# determine type
					type_id = None

					for t in types:
						entry['type'] = entry['type'].lower()
						if entry['type'] in t.bibtex_type_list:
							type_id = t.id
							break

					if type_id is None:
						errors['bibliography'] = 'Type "' + entry['type'] + '" in @' + entry['key'] +' unknown.'
						break

					# add publication
					publications.append(Publication(
						type_id=type_id,
						citekey=entry['key'],
						title=entry['title'],
						authors=authors,
						year=entry['year'],
						month=entry['month'],
						journal=entry['journal'],
						book_title=entry['booktitle'],
						publisher=entry['publisher'],
						institution=entry['institution'],
						volume=entry['volume'],
						number=entry['number'],
						note=entry['note'],
						url=entry['url'],
						doi=entry['doi'],
						isbn=entry['isbn'],
						abstract=entry['abstract'],
						keywords=entry['keywords'],
						timestamp=timestamp,
						owner=entry['owner'],
						language=entry['language'],
						editor=entry['editor'],
						pages=entry['pages'],
						address=entry['address'],
						organization=entry['organization'],
						school=entry['school'],
						chapter=entry['chapter'],
						howpublished=entry['howpublished'],
						issn=entry['issn'],
						comment=entry['comment'],
						series=entry['series'],
						edition=entry['edition']
						)
					)
				else:
					pprint(entry)
					errors['bibliography'] = 'Make sure that the keys title, author and year are present.'
					break

		return errors, publications

import_bibtex = staff_member_required(import_bibtex)
