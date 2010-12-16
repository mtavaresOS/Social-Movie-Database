from django_rdf.utils import LazySubject
from django_rdf import graph
from smdb import manager

class BaseModel(LazySubject):
	
	def __new__(self, uri):
		obj = object.__new__(self)
		
		return manager.getOrUse(uri, obj)
	
	def __init__(self, uri):
		
		# Avoid running __init__() in an already created instance
		try:
			self.__getattribute__('uri')
			return True
		except AttributeError: pass
		
		# Proceed with the initialization
		super(BaseModel, self).__init__(graph, uri)
		
		self.dynamic = {}
	
	def __getattr__(self, name):
		
		if name in self.dynamic.keys():
			
			if self.dynamic[name] == None:
				self.dynamic[name] = getattr(self, 'get_' + name)()
			
			return self.dynamic[name]
		else:
			return super(BaseModel, self).__getattr__(name)
	
	def __str__(self):
		return u"%s(%s)" %(self.__class__.__name__, self.uri)


class Movie(BaseModel):
	
	def __init__(self, uri):
		if super(Movie, self).__init__(uri): return		# Call super and exit if this is a created instance
		
		self.title, self.slug, self.releaseDate = graph.query_single(
			"""SELECT ?t ?s ?d WHERE {
						?u rdf:type smdb:Movie .
						?u smdb:title ?t .
						?u smdb:slug ?s .
						?u smdb:releaseDate ?d .
					}""", initBindings={'u': self.uri})
		
		self.releaseDate = self.releaseDate.toPython()
		
		self.dynamic = {
			'directedBy': None,
			'writtenBy': None,
			'featured': None,
			'isOfGenre': None,
			'hasReview': None,
		}
		
			
	def get_directedBy(self):
		print '>> fetching [Movie-directedBy]'
		# Return a single result.
		for person in [ Person(obj.uri) for obj in self.smdb__directedBy__m ]:
			return person
	
	def get_writtenBy(self):
		print '>> fetching [Movie-writtenBy]'
		return [ Person(obj.uri) for obj in self.smdb__writtenBy__m ]
		
	def get_featured(self):
		print '>> fetching [Movie-featured]'
		return [ Person(obj.uri) for obj in self.smdb__featured__m ]
	
	def get_isOfGenre(self):
		print '>> fetching [Movie-isOfGenre]'
		return [ Genre(obj.uri) for obj in self.smdb__isOfGenre__m ]
	
	def get_hasReview(self):
		print '>> fetching [Movie-hasReview]'
		return [ MovieReview(obj.uri) for obj in self.smdb__hasReview__m ]
		
	def get_actor_character(self):
		for uriActor, uriCharacter in graph.query("""SELECT ?a ?c WHERE {
										?a smdb:performedIn ?u.
										?c smdb:inMovie ?u .
										?c smdb:portrayedBy ?a .
										}""", initBindings={'u': self.uri}):
			yield Person(uriActor), Character(uriCharacter)
	
	def get_absolute_url(self):
		return u'/movie/%s/' %(self.slug)
		
class Person(BaseModel):
	
	def __init__(self, uri):
		if super(Person, self).__init__(uri): return		# Call super and exit if this is a created instance
		
		self.name, self.slug = graph.query_single(
			"""SELECT ?n ?s WHERE {
						?u rdf:type smdb:Person .
						?u smdb:name ?n .
						?u smdb:slug ?s .
					}""", initBindings={'u': self.uri})
		
		self.dynamic = {
			'directed': None,
			'wrote': None,
			'performed': None,
			'playsCharacter': None,
		}
		
		
	def get_directed(self):
		print '>> fetching [Person-directed]'
		return [ Movie(obj.uri) for obj in self.smdb__directed__m ]
	
	def get_wrote(self):
		print '>> fetching [Person-wrote]'
		return [ Movie(obj.uri) for obj in self.smdb__wrote__m ]
		
	def get_performed(self):
		print '>> fetching [Person-performed]'
		return [ Movie(obj.uri) for obj in self.smdb__performed__m ]
	
	def get_playsCharacter(self):
		print '>> fetching [Person-playsCharacter]'
		return [ Character(obj.uri) for obj in self.smdb__playsCharacter__m ]

	def get_absolute_url(self):
		return u'/person/%s/' %(self.slug)
		
		
class Character(BaseModel):
	
	def __init__(self, uri):
		if super(Character, self).__init__(uri): return		# Call super and exit if this is a created instance
		
		self.name, self.slug = graph.query_single(
			"""SELECT ?n ?s WHERE {
						?u rdf:type smdb:Character .
						?u smdb:name ?n .
						?u smdb:slug ?s .
					}""", initBindings={'u': self.uri})
					
		
		self.dynamic = {
			'portrayedBy': None,
			'inMovie': None,
		}
		
	
	def get_portrayedBy(self):
		print '>> fetching [Character-portrayedBy]'
		return [ Person(obj.uri) for obj in self.smdb__portrayedBy__m ]
		
	def get_inMovie(self):
		print '>> fetching [Character-inMovie]'
		return [ Movie(obj.uri) for obj in self.smdb__inMovie__m ]
	
	def get_absolute_url(self):
		return u'/character/%s/' %(self.slug)
	
	
class SMDBUser(BaseModel):
	
	def __init__(self, uri):
		if super(SMDBUser, self).__init__(uri): return		# Call super and exit if this is a created instance
		
		self.username = graph.query_single(
			"""SELECT ?un WHERE {
						?u rdf:type smdb:SMDBUser .
						?u smdb:username ?un .
					}""", initBindings={'u': self.uri})
					
		
		self.dynamic = {
			'isFriendsWith': None,
			'hasWritten': None,
			'hasSeen': None,
		}
		
	
	def get_isFriendsWith(self):
		print '>> fetching [SMDBUser-isFriendsWith]'
		return [ SMDBUser(obj.uri) for obj in self.smdb__isFriendsWith__m ]
		
	def get_hasWritten(self):
		print '>> fetching [SMDBUser-hasWritten]'
		return [ MovieReview(obj.uri) for obj in self.smdb__hasWritten__m ]
		
	def get_hasSeen(self):
		print '>> fetching [SMDBUser-hasSeen]'
		return [ Movie(obj.uri) for obj in self.smdb__hasSeen__m ]
	
	def get_absolute_url(self):
		return u'/user/%s/' %(self.username)
	
	
class MovieReview(BaseModel):
	
	def __init__(self, uri):
		if super(MovieReview, self).__init__(uri): return		# Call super and exit if this is a created instance
		
		self.id, self.reviewText = graph.query_single(
			"""SELECT ?id ?t WHERE {
						?u rdf:type smdb:MovieReview .
						?u smdb:id ?id .
						?u smdb:reviewText ?t .
					}""", initBindings={'u': self.uri})
					
		
		self.dynamic = {
			'refersTo': None,
			'writtenByUser': None,
		}
		
	
	def get_refersTo(self):
		print '>> fetching [MovieReview-refersTo]'
		# Return a single result.
		for movie in [ Movie(obj.uri) for obj in self.smdb__refersTo__m ]:
			return movie
	
	def get_writtenByUser(self):
		print '>> fetching [MovieReview-writtenByUser]'
		# Return a single result.
		for user in [ SMDBUser(obj.uri) for obj in self.smdb__writtenByUser__m ]:
			return user
	
	def get_absolute_url(self):
		return u'%s#review-%s' %(self.refersTo.get_absolute_url(), self.id)