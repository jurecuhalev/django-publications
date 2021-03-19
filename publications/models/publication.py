# -*- coding: utf-8 -*-

__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.db import models, connections, transaction
from django.db.models.signals import post_save
from django.utils.http import urlquote_plus
from django.contrib.auth.models import User
from django.core.cache import cache

from string import split, strip, join, replace, ascii_uppercase
from publications.fields import PagesField
from publications.models import Type


# def _clear_page_cache(sender, instance, **kwargs):
# 	cursor = connections['default'].cursor()
# 	cursor.execute('DELETE FROM cache')
# 	transaction.commit_unless_managed(using='default')

class Publication(models.Model):
    class Meta:
        app_label = 'publications'
        ordering = ['-year', '-month', '-id']
        verbose_name_plural = ' Publications'

    # names shown in admin area
    MONTH_CHOICES = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December')
    )

    # abbreviations used in BibTex
    MONTH_BIBTEX = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }

    YEAR_CHOICES = [(i, i) for i in range(2005, 2024)]

    STATE_CHOICES = (
        (0, 'Needs review'),
        (1, 'Reviewed and published'),
        (2, 'Removed')
    )

    type = models.ForeignKey(Type)
    citekey = models.CharField(max_length=512, blank=True, null=True,
                               help_text='BibTex citation key. Leave blank if unsure.')
    title = models.CharField(max_length=512, verbose_name=u'Publication Title')
    authors = models.CharField(max_length=2048,
                               help_text='List of authors separated by commas or <i>and</i>.')
    year = models.PositiveIntegerField(max_length=4, verbose_name=u'Year of Publication', choices=YEAR_CHOICES)
    month = models.IntegerField(choices=MONTH_CHOICES, blank=True, null=True, verbose_name=u'Month of Publication')
    journal = models.CharField(max_length=256, blank=True)
    book_title = models.TextField(blank=True)
    publisher = models.CharField(max_length=256, blank=True)
    institution = models.CharField(max_length=256, blank=True)
    volume = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True, verbose_name='Issue number')
    pages = PagesField(max_length=32, blank=True)
    note = models.TextField(blank=True)
    keywords = models.TextField(blank=True,
                                help_text='List of keywords separated by commas.')
    url = models.TextField(blank=True, verbose_name='URL',
                           help_text='Link to PDF or journal page.')
    code = models.URLField(blank=True,
                           help_text='Link to page with code.')
    pdf = models.FileField(upload_to='publications/', verbose_name='PDF', blank=True, null=True)
    doi = models.CharField(max_length=128, verbose_name='DOI', blank=True)
    external = models.BooleanField(
        help_text='If publication was written in another lab, mark as external.')
    abstract = models.TextField(blank=True)
    isbn = models.CharField(max_length=32, verbose_name="ISBN", blank=True,
                            help_text='Only for a book.')  # A-B-C-D

    # GGP specific import fields
    timestamp = models.DateField(auto_now_add=True)
    owner = models.CharField(max_length=64, blank=True, null=True, default='admin')
    owner_user = models.ForeignKey(User, blank=True, null=True, related_name='publication_owner_user')
    user = models.ForeignKey(User, blank=True, null=True, related_name="publication_user")

    language = models.CharField(max_length=255, blank=True)
    editor = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True, verbose_name=u'Published address')
    organization = models.CharField(max_length=255, blank=True)
    volume = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=255, blank=True)
    series = models.CharField(max_length=255, blank=True)
    edition = models.CharField(max_length=255, blank=True)
    chapter = models.CharField(max_length=255, blank=True)

    school = models.CharField(max_length=255, blank=True)
    howpublished = models.CharField(max_length=255, blank=True, verbose_name=u'How is it published?')
    issn = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)

    state = models.IntegerField(max_length=5, blank=True, null=True, default=0, choices=STATE_CHOICES)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)

        # post-process keywords
        self.keywords = replace(self.keywords, ';', ',')
        self.keywords = replace(self.keywords, ', and ', ', ')
        self.keywords = replace(self.keywords, ',and ', ', ')
        self.keywords = replace(self.keywords, ' and ', ', ')
        self.keywords = [strip(s).lower() for s in split(self.keywords, ',')]
        self.keywords = join(self.keywords, ', ').lower()

        # tests if title already ends with a punctuation mark
        self.title_ends_with_punct = self.title[-1] in ['.', '!', '?'] \
            if len(self.title) > 0 else False

        self.authors_bibtex = self.authors
        self.authors_list = self.get_authors_list(self.authors)
        self.authors_list_simple = self.get_authors_list(self.authors, simple=True)

    @staticmethod
    def get_authors_list(authors, simple=False):
        # # post-process author names
        authors = replace(authors, ', and ', ', ')
        authors = replace(authors, ',and ', ', ')
        authors = replace(authors, ' and ', ', ')
        authors = replace(authors, ';', ',')

        # list of authors
        authors_list = [strip(author) for author in split(authors, ',')]

        # simplified representation of author names
        authors_list_simple = []

        suffixes = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', "Jr.", "Sr."]
        prefixes = ['Dr.']
        prepositions = ['van', 'von', 'der', 'de', 'den']

        # further post-process author names
        for i, author in enumerate(authors_list):
            if author == '':
                continue

            names = split(author, ' ')

            # check if last string contains initials
            if (len(names[-1]) <= 3) \
                    and names[-1] not in suffixes \
                    and all(c in ascii_uppercase for c in names[-1]):
                # turn "Gauss CF" into "C. F. Gauss"
                names = [c + '.' for c in names[-1]] + names[:-1]

            # number of suffixes
            num_suffixes = 0
            for name in names[::-1]:
                if name in suffixes:
                    num_suffixes += 1
                else:
                    break

            # abbreviate names
            for j, name in enumerate(names[:-1 - num_suffixes]):
                # don't try to abbreviate these
                if j == 0 and name in prefixes:
                    continue
                if j > 0 and name in prepositions:
                    continue

                if (len(name) > 2) or (len(name) and (name[-1] != '.')):
                    k = name.find('-')
                    if 0 < k + 1 < len(name):
                        # take care of dash
                        names[j] = name[0] + '.-' + name[k + 1] + '.'
                    else:
                        names[j] = name[0] + '.'

            if len(names):
                authors_list[i] = join(names, ' ')

                # create simplified/normalized representation of author name
                if len(names) > 1:
                    for name in names[0].split('-'):
                        name_simple = Publication.simplify_name(join([name, names[-1]], ' '))
                        authors_list_simple.append(name_simple)
                else:
                    authors_list_simple.append(Publication.simplify_name(names[0]))

        if simple:
            return authors_list_simple
        else:
            return authors_list

        # Do not normalize strings as we already imported them in Bibtex format

        # # list of authors in BibTex format
        # # self.authors_bibtex = join(self.authors_list, ' and ')

        # # overwrite authors string
        # if len(self.authors_list) > 2:
        # 	self.authors = join([
        # 		join(self.authors_list[:-1], ', '),
        # 		self.authors_list[-1]], ', and ')
        # elif len(self.authors_list) > 1:
        # 	self.authors = join(self.authors_list, ' and ')
        # else:
        # 	self.authors = self.authors_list[0]

    def __unicode__(self):
        if len(self.title) < 64:
            return self.title
        else:
            index = self.title.rfind(' ', 40, 62)

            if index < 0:
                return self.title[:61] + '...'
            else:
                return self.title[:index] + '...'

    def keywords_escaped(self):
        return [(strip(keyword), urlquote_plus(strip(keyword)))
                for keyword in split(self.keywords, ',')]

    def authors_escaped(self):
        return [(author, replace(author.lower(), ' ', '+'))
                for author in self.authors_list]

    def key(self):
        # this publication's first author
        authors_list = self.get_authors_list(self.authors)

        author_lastname = authors_list[0].split(' ')[-1]

        publications = Publication.objects.filter(
            year=self.year,
            authors__icontains=author_lastname).order_by('month', 'id')

        # character to append to BibTex key
        char = ord('a')

        # augment character for every publication 'before' this publication
        for publication in publications:
            if publication == self:
                break

            if publication.authors_list[0].split(' ')[-1] == author_lastname:
                char += 1

        return authors_list[0].split(' ')[-1] + str(self.year) + chr(char)

    def month_bibtex(self):
        return self.MONTH_BIBTEX.get(self.month, '')

    def month_long(self):
        for month_int, month_str in self.MONTH_CHOICES:
            if month_int == self.month:
                return month_str
        return ''

    def first_author(self):
        return self.authors_list[0]

    def journal_or_book_title(self):
        if self.journal:
            return self.journal
        else:
            return self.book_title

    def clean(self):
        if not self.citekey:
            self.citekey = self.key()

    @staticmethod
    def simplify_name(name):
        name = name.lower()
        name = replace(name, u'ä', u'ae')
        name = replace(name, u'ö', u'oe')
        name = replace(name, u'ü', u'ue')
        name = replace(name, u'ß', u'ss')
        return name

    def get_absolute_url(self):
        return '/form/publications/%s/' % self.id

        # post_save.connect(_clear_page_cache, sender=Publication, dispatch_uid='publication_postsave_clear_cache')
