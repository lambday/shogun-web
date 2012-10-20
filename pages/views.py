# Create your views here.

import shogun.settings as settings

from django.http import HttpResponse,Http404

# HTML rendering libraries.
from django.template.loader import get_template
from django.template import Context,TemplateDoesNotExist

# Data Base libraries.
from pages.models import Page
from pages.models import Subpage 
from pages.models import Article 
from pages.models import New

# Import the parser.
import parserHTML
import datetime
from BeautifulSoup import BeautifulSoup

# Parse news object.
newsParser = parserHTML.myContentHandler();


def error(err):
	if  settings.DEBUG:
		print(err)
	raise Http404


def get_news():
	# Get the last 5 articles modified.
	news = New.objects.order_by('-updated_date')[:7]  

	# Latest news
	latest=None
	if len(news)>0:
		latest= news[0]

	return news,latest

# ----------------------------------------------------------------------
#                                HOME
# ----------------------------------------------------------------------
# To render correctly the main view (home).
def home(request):

	# choose the template.
	template = get_template("home.html")

	try:
		# Get all the pages.
		allpages = Page.objects.order_by('sort_order')

		# Parse the news.
		newsParser.parseNews()
		news,lastnew=get_news()
	except ValueError, err:
		error(err)

	return HttpResponse(template.render(Context({'current_page_path' : "home",
												 'all_pages' : allpages,
												 'news' : news,
												 'lastnew' : lastnew})))  


# ----------------------------------------------------------------------
#                             SHOW NEW
# ----------------------------------------------------------------------
# To render correctly the other views (about,documentation,contact,...)
def showNew(request,newID):
	
	# Choose the template.
	template = get_template("news.html")

	# Find the pages.
	try:
		# Get all the pages.
		allpages = Page.objects.order_by('sort_order')

		# Get default subpages.
		defaultsubpages = Subpage.objects.filter(sort_order=1)

		# Get all the subpages.
		allsubpages = Subpage.objects.filter(rootpage__path__exact="news").order_by('sort_order')

		# The new selected.
		articles = New.objects.get(pk=newID)
		news = get_news()[0]

	except ValueError, err:
		error(err)

	return HttpResponse(template.render(Context({'current_page_path' : 'news',
												 'current_subpage_path' : 'onenew',
												 'default_subpages' : defaultsubpages,
												 'all_pages' : allpages,
												 'all_subpages' : allsubpages,
												 'articles' : [articles],
		                                         'news' : news})))  

# ----------------------------------------------------------------------
#                             SHOW BIG PICTURE
# ----------------------------------------------------------------------
# To render correctly the other views (about,documentation,contact,...)
def showPicture(request,pictureName):

	# Choose the template.
	template = get_template("bigpicture.html")

	# Find the pages.
	try:
		# Get all the pages.
		allpages = Page.objects.order_by('sort_order')

		# Get picture url.
		picture_url = "/static/figures/" + pictureName

	except ValueError, err:
		error(err)

	return HttpResponse(template.render(Context({'current_page_path' : 'bigpicture',
												 'current_subpage_path' : 'bigpicture',
												 'all_pages' : allpages,
												 'picture_name' : pictureName,
												 'picture_url' : picture_url}))) 



def weblog(request):


	# Find the pages.
	try:
		template = get_template("weblog.html")

		# Get all the pages.
		allpages = Page.objects.order_by('sort_order')

		news = get_news()[0]

		html=file(settings.SHOGUN_PLANET).read()
		soup = BeautifulSoup(html)
		items=soup.body.findAll("div", { "class" : "daygroup" })
		articles=[]
		for article in soup.body.findAll("div", { "class" : "daygroup" }):
			polished='<dt><h1>' + article.h2.string + '</h1></dt>'
			articles.append(polished + unicode(article.div.div).replace('class="content"',""))


	except Exception, err:
		error(err)

	return HttpResponse(template.render(Context({'current_page_path' : 'weblog',
												 'current_subpage_path' : 'planet',
												 'all_pages' : allpages,
												 'all_subpages' : ['planet'],
												 'articles' : articles,
		                                         'news' : news})))  

# ----------------------------------------------------------------------------------------------------
#                                           NEWS
# ----------------------------------------------------------------------------------------------------
# Method to render correctly the view news, there are three possibilities:
#	- 'onenew' : show the last new.
#   - 'newslist' : show the list with all the news.
#   - Show the news of one year.
def news(request, subpage):

	# Set the page we are.
	page = "news"

	# choose the news template.
	template = get_template(page + ".html")

	defaultsubpages=[]
	all_pages=[]
	all_subpages=[]
	articles=[]
	news=[]
	lastnew=[]

	try:
		# Get all the pages.
		allpages = Page.objects.order_by('sort_order')

		# Get default subpages.
		defaultsubpages = Subpage.objects.filter(sort_order=1)

		# Get all the subpages.
		allsubpages = Subpage.objects.filter(rootpage__path__exact=page).order_by('sort_order')

		# Finding the articles.
		if subpage == 'onenew':
			# Get the last new.
			articles = [New.objects.order_by('-updated_date')[0]]
		elif subpage == 'newslist':
			# Get all news.
			articles = New.objects.order_by('-updated_date')
		else:
			# Get all the news for a year.
			articles = New.objects.filter(updated_date__year=subpage).order_by('-updated_date')

		news,lastnew=get_news()

	except ValueError, err:
		error(err)

	return HttpResponse(template.render(Context({'current_page_path' : page,
												 'current_subpage_path' : subpage,
												 'default_subpages' : defaultsubpages,
												 'all_pages' : allpages,
												 'all_subpages' : allsubpages,
												 'articles' : articles,
		                                         'news' : news,
		                                         'lastnew' : lastnew})))  

# ----------------------------------------------------------------------
#                             PAGE HANDLER
# ----------------------------------------------------------------------
# To render correctly the other views (about,documentation,contact,...)
def pageHandler(request,page,subpage):
	
	# Choose the template.
	try:
		template = get_template(page + ".html")
	except (TemplateDoesNotExist,ValueError), err:
		error(err)

	# Find the pages.
	try:
		# Get all the pages.
		allpages = Page.objects.order_by('sort_order')

		# Get default subpages.
		defaultsubpages = Subpage.objects.filter(sort_order=1)

		# Get all the subpages.
		allsubpages = Subpage.objects.filter(rootpage__path__exact=page).order_by('sort_order')

		if subpage=="downloads":
			# Get all the releases.
			articles = New.objects.order_by('-sg_ver')
		else :
			# Get the articles that are in page/subpage.
			articles = Article.objects.filter(rootsubpage__rootpage__path__exact=page, rootsubpage__path__exact=subpage)

		news, lastnew=get_news()
	except ValueError, err:
		error(err)

	return HttpResponse(template.render(Context({'current_page_path' : page,
												 'current_subpage_path' : subpage,
												 'default_subpages' : defaultsubpages,
												 'all_pages' : allpages,
												 'all_subpages' : allsubpages,
												 'articles' : articles,
		                                         'news' : news,
		                                         'lastnew' : lastnew})))  
