# -*- coding: utf-8 -*-
import codecs
from pprint import pprint

from django.db import DatabaseError
from django.core.management.base import BaseCommand

from publications.admin_views.import_bibtex import import_bibtex_utility
from publications.bibtex import parse


class Command(BaseCommand):
	help = "imports bibtex entries from .bib file"

	def handle(self, *args, **options):
		bib_raw = codecs.open(args[0], 'rU', 'Cp1252').read()

		supported_keys = [
			'title',
			'author', 
			'year',
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
			'key',
			'type',

			# new keys
			'timestamp',
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
			#todo below this point
			
			'__markedentry',

		]

		bib_list = parse(bib_raw)
		for entry in bib_list:
			for key in entry.keys():
				if str(key) not in supported_keys:
					print 'New key:  %s  in %s' % (key, entry['key'])


		self.stdout.write("Setting up defaults")



		self.stdout.write("Parsing")
		errors, publications = import_bibtex_utility(bib_list)

		if errors:
			print errors
		else:
			for publication in publications:
				print publication.citekey
				publication.save()
