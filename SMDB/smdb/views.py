from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import Http404

from django_rdf import graph
from rdflib import Literal, URIRef

from smdb.semantic_models import *
from smdb import manager


# Util Functions

def render(request,template,context={}):
	return render_to_response(template,context,context_instance=RequestContext(request))

def get_object_or_404(Model, uri):
	try: return Model(uri)
	except TypeError: raise Http404
	

# Detail Pages

def movie_detail(request, slug):
	
	uri = request.path
	
	movie = get_object_or_404(Movie, uri)
	
	return render(request, 'movie.html', {'movie': movie})
	
def user_detail(request, username):
	
	uri = request.path
	user = get_object_or_404(SMDBUser, uri)
	
	return render(request, 'user.html', {'user': user})
	
def person_detail(request, slug):
	
	uri = request.path
	person = get_object_or_404(Person, uri)
	
	return render(request, 'person.html', {'person': person})
	
def character_detail(request, slug):
	
	uri = request.path
	character = get_object_or_404(Character, uri)
	
	return render(request, 'character.html', {'character': character})
	

# Browsing

def browse_movies(request):
	
	initBindings = {}
	
	year = request.GET.get('year', None)
	director = request.GET.get('director', None)
	genre = request.GET.get('genre', None)
	location = request.GET.get('location', None)
	
	print 'Year:', year
	print 'Director:', director
	print 'Genre:', genre
	print 'Location:', location
	
	f = Movie.getFilterList(year, director, genre, location)
	
	query = """SELECT ?a ?b ?y WHERE {
				?a rdf:type smdb:Movie .
				?a smdb:title ?b .
				?a smdb:releaseDate ?y .
				"""
	
	# Director
	if director: query += '?d smdb:directed ?a .\n'
	
	# Genre
	if genre: query += '?a smdb:isOfGenre ?g .\n'
	
	# Location
	if location: query += '?a smdb:shotIn ?l .\n'
	
	# Filters	
	if year: query += """FILTER(?y = "%s") .\n""" % Literal(year)
	if director: query += """FILTER(?d = <%s>) .\n""" % URIRef(director)
	if genre: query += """FILTER(?g = <%s>) .\n""" % graph.ontologies['smdb'][genre]
	if location: query += """FILTER(?l = "%s") .\n""" % Literal(location)
	
	res = graph.query(query + "}", initBindings=initBindings)
	
	return render(request, 'browse.html', {'filter_list':f, 'movie_list': res})
	
def browse_people(request):
	
	res = graph.query("""SELECT ?a ?b WHERE {
					?a rdf:type smdb:Person .
					?a smdb:name ?b .
				}""")
	
	return render(request, 'browse.html', {'people_list': res})	

# Searching

def search(request):
	
	searchString = request.GET.get('find', None)
	
	query = """SELECT ?a ?b ?d WHERE{
				?a rdf:type smdb:Movie .
				?a smdb:title ?b .
				?a smdb:releaseDate ?d .
				"""
				
	if searchString: query += 'FILTER( regex(str(?b), "%s", "i") ) .' %searchString
	
	movies = graph.query(query + '}')
	
	query = """SELECT ?a ?b WHERE{
				?a rdf:type smdb:Person .
				?a smdb:name ?b .
				"""
				
	if searchString: query += 'FILTER( regex(str(?b), "%s", "i") ) .' %searchString
	
	people = graph.query(query + '}')
	
	if movies and not people:
		
		query = """SELECT DISTINCT ?a ?b WHERE{
				?a rdf:type smdb:Person .
				?a smdb:name ?b .
				?a smdb:performedIn ?m .
				"""
		if searchString: query += 'FILTER( regex(str(?m), "%s", "i") ) .' %searchString	
	
		people = graph.query(query + '}')
				
	elif people and not movies:
		print "Searching directed by"
		print people
		query = """SELECT DISTINCT ?a ?b ?d WHERE{
				?a rdf:type smdb:Movie .
				?a smdb:title ?b .
				?a smdb:releaseDate ?d .
				?p smdb:directed ?a .
				?p rdf:type smdb:Person .
				?p smdb:name ?n .
				"""
				
		if searchString: query += 'FILTER( regex(str(?n), "%s", "i") ) .' %searchString	
	
		movies = graph.query(query + '}')
	
	return render(request, 'search.html', {'movie_list': movies, 'person_list': people})