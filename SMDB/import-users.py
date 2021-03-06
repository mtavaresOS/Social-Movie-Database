from import_handler import SMDB

s = SMDB()

s.addSMDBUser('mtavares')
s.addSMDBUser('pgaspar', 'Pedro Gaspar')
s.addSMDBUser('user_test')
s.addSMDBUser('user_test_all')
s.addSMDBUser('myfriend_1')
s.addSMDBUser('lonelyguy_08')

s.addFriendship('mtavares', 'pgaspar')
s.addFriendship('mtavares', 'user_test')
s.addFriendship('mtavares', 'user_test_all')
s.addFriendship('myfriend_1', 'pgaspar')
s.addFriendship('myfriend_1', 'user_test_all')

s.addMovieSeen('mtavares', 'Pulp Fiction (1994)')
s.addMovieSeen('pgaspar', 'Corpse Bride (2005)')
s.addMovieSeen('pgaspar', 'Pulp Fiction (1994)')
s.addMovieSeen('user_test_all', 'Corpse Bride (2005)')
s.addMovieSeen('myfriend_1', 'Corpse Bride (2005)')
s.addMovieSeen('mtavares', 'The Cotton Club (1984)')
s.addMovieSeen('pgaspar', 'Sin City (2005)')
s.addMovieSeen('lonelyguy_08', 'Sin City (2005)')
s.addMovieSeen('lonelyguy_08', 'Corpse Bride (2005)')

s.addMovieReview(1, 'This movie is awesome[*****]', 'Pulp Fiction (1994)', 'mtavares')
s.addMovieReview(1, 'It was ok.', 'Corpse Bride (2005)', 'user_test_all')

s.printTripleCount()