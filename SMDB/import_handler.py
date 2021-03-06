import rdflib
from rdflib.store.Sleepycat import Sleepycat
from rdflib import Graph
from rdflib.namespace import Namespace, RDF
from rdflib import URIRef, Literal, BNode
from sqlite3 import IntegrityError

from django.template.defaultfilters import slugify

# Loding the environment

from django.core.management import setup_environ
import settings

print "Setting up environment"
setup_environ(settings)

print "Importing models"
from smdb.models import *


class SMDB():
	
	def __init__(self, identifier="http://www.smdb.com/smdb.owl"):
		
		self.store = Sleepycat()
		#self.store.open('rdf-db')
		self.store.open('database/rdf', create = False)
		
		self.graph = Graph(self.store, identifier = URIRef(identifier))
		
		self.printTripleCount()
		
		if(len(self.graph) == 0):
			self.graph.parse('../Ontology/SocialMovieDatabase.owl')
		
		self.smdb = Namespace(identifier + '#')
		self.person = Namespace("/person/")
		self.movie = Namespace("/movie/")
		self.character = Namespace("/character/")
		self.user = Namespace("/user/")

	def printTripleCount(self):
		print "Triples in graph: ", len(self.graph)

	
	def addPerson(self, name, bio="Sample Biography."):

		uri = self.person[slugify(name) + '/']

		self.graph.add((uri, RDF.type, self.smdb['Person']))
		self.graph.add((uri, self.smdb['name'], Literal(name)))
		self.graph.add((uri, self.smdb['biography'], Literal(bio)))
		
		self.graph.commit()
	
	def addPerformance(self, actor, movie):
		
		uriActor = self.person[slugify(actor) + '/']
		uriMovie = self.movie[slugify(movie) + '/']
		
		self.graph.add((uriActor, self.smdb['performedIn'], uriMovie))
		self.graph.add((uriMovie, self.smdb['featured'], uriActor))
		
		self.graph.commit()
	
	def addDirector(self, director, movie):
		
		uriDirector = self.person[slugify(director) + '/']
		uriMovie = self.movie[slugify(movie) + '/']
		
		self.graph.add((uriDirector, self.smdb['directed'], uriMovie))
		self.graph.add((uriMovie, self.smdb['directedBy'], uriDirector))
		
		self.graph.commit()
		
	def addWriter(self, writer, movie):

		uriWriter = self.person[slugify(writer) + '/']
		uriMovie = self.movie[slugify(movie) + '/']

		self.graph.add((uriWriter, self.smdb['wrote'], uriMovie))
		self.graph.add((uriMovie, self.smdb['writtenBy'], uriWriter))

		self.graph.commit()

		
	def addCharacter(self, movie, actor, character):

		uriMovie = self.movie[slugify(movie) + '/']
		uriActor = self.person[slugify(actor) + '/']
		uriCharacter = self.character[slugify(character) + '/']

		character = character.replace("[","").replace("]","")

		self.graph.add((uriCharacter, RDF.type, self.smdb['Character']))
		self.graph.add((uriCharacter, self.smdb['name'], Literal(character)))
		
		self.graph.add((uriCharacter, self.smdb['portrayedBy'], uriActor))
		self.graph.add((uriActor, self.smdb['playsCharacter'], uriCharacter))
		
		self.graph.add((uriCharacter, self.smdb['inMovie'], uriMovie))
			
		self.graph.commit()
	
	
	def addMovie(self, title, releaseDate, synopsis="Sample synopsis."):

		uri = self.movie[slugify(title) + '/']
		
		if '(' in title: clean_title = title[:title.find('(')-1]
		
		self.graph.add((uri, RDF.type, self.smdb['Movie']))
		self.graph.add((uri, self.smdb['title'], Literal(clean_title)))
		self.graph.add((uri, self.smdb['releaseDate'], Literal(releaseDate)))
		self.graph.add((uri, self.smdb['synopsis'], Literal(synopsis)))
		
		self.graph.commit()
		
	def addGenre(self, movie, genre):
		
		uri = self.movie[slugify(movie) + '/']
		uriGenre = self.smdb[genre]
		
		self.graph.add((uri, self.smdb['isOfGenre'], uriGenre))
		
		self.graph.commit()
	
	def addRating(self, movie, rating):
		
		uriMovie = self.movie[slugify(movie) + '/']
		uriRating = self.smdb[rating]
		
		self.graph.add((uriMovie, self.smdb['hasRating'], uriRating))
		
		self.graph.commit()
		
	
	def addLocation(self, movie, location):
		
		uriMovie = self.movie[slugify(movie) + '/']
		
		self.graph.add((uriMovie, self.smdb['shotIn'], Literal(location)))
		
		self.graph.commit()
		
	def addDuration(self, movie, duration):
		
		uriMovie = self.movie[slugify(movie) + '/']
		
		self.graph.add((uriMovie, self.smdb['duration'], Literal(duration)))
		
		self.graph.commit()
	
	def addSMDBUser(self, username, fullname=''):
		
		uri = self.user[slugify(username) + '/']
		
		self.graph.add((uri, RDF.type, self.smdb['SMDBUser']))
		self.graph.add((uri, self.smdb['username'], Literal(username)))
		if fullname: self.graph.add((uri, self.smdb['fullName'], Literal(fullname)))
		
		# Add the django model.
		try:
			user = User.objects.create_user(username, '', username) # Use username as password
		
			if fullname:
				user.first_name = fullname.split(' ', 1)[0]
				if ' ' in fullname: user.last_name = fullname.split(' ',1)[1]
		
			user.save()
		
		except IntegrityError:
			user = User.objects.get(username=username)
			print 'The user', username, 'was already created in the Django database.'
		
		# Add the Profile info if it doesn't exist yet
		try:
			profile = user.get_profile()
			profile._uri = uri
			
		except UserProfile.DoesNotExist:
			profile = UserProfile(_uri=uri)
			profile.user = user
			print 'Created Profile for:', uri
		
		# Save changes
		profile.save()
		self.graph.commit()
		
	
	def addFriendship(self, user1, user2):
		
		uriUser1 = self.user[slugify(user1) + '/']
		uriUser2 = self.user[slugify(user2) + '/']
		
		self.graph.add((uriUser1, self.smdb['isFriendsWith'], uriUser2))
		self.graph.add((uriUser2, self.smdb['isFriendsWith'], uriUser1))
		
		self.graph.commit()
	
	def addMovieSeen(self, user, movie):
		
		uriUser = self.user[slugify(user) + '/']
		uriMovie = self.movie[slugify(movie) + '/']
		
		self.graph.add((uriUser, self.smdb['hasSeen'], uriMovie))
		
		self.graph.commit()
	
	
	def addMovieReview(self, review_id, text, movie, author):
		
		cleanMovie = slugify(movie) + '/'
		
		uri = self.movie[cleanMovie + '#review-' + str(review_id)]
		uriMovie = self.movie[cleanMovie]
		uriUser = self.user[slugify(author) + '/']
		
		self.graph.add((uri,RDF.type, self.smdb['MovieReview']))
		self.graph.add((uri, self.smdb['id'], Literal(review_id)))
		self.graph.add((uri, self.smdb['refersTo'], uriMovie))
		self.graph.add((uri, self.smdb['writtenByUser'], uriUser))
		self.graph.add((uri, self.smdb['reviewText'], Literal(text)))
		
		self.graph.commit()
	
	def exportData(self, file_name='res'):
		
		# save the graph in RDF/XML and N3
		self.graph.serialize(destination=file_name + ".xml")
		self.graph.serialize(destination=file_name + ".n3", format="n3")
