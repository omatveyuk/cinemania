""" Model """
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import request_helper

##############################################################################
# Model definitions

class Movie(object):
    """ Movie class """
    def __init__(self, movie_id):
        self.id = movie_id
        self.title = ""
        self.original_language = []
        self.production_countries = []
        self.production_companies = []
        self.release_date = None
        self.imdb_id = None
        self.imdb_rating = None
        self.genres = []
        self.runtime = None
        self.directors = []
        self.writers = []
        self.actors = []
        self.overview = None
        self.trailer_url = []
        self.poster_url = None
        self.reviews = []
        self.total_pages_reviews = 0
        self.total_reviews = 0
        self.vote_average = None
        self.vote_count = None

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Movie id={0} Title={1}>".format(self.id, self.title)

    def print_actors(self):
        """Print list of actors for movie"""
        print 'Title', self.title, '. Actors:'
        for actor in self.actors:
            print actor

    def print_directors(self):
        """ Print list of directors for movie """
        print 'Title', self.title, '. Directors:'
        for director in self.directors:
            print director
        
    def print_writers(self):
        """ Print list of writers for movie """
        print 'Title', self.title, '. Writers:'
        for writer in self.writers:
            print writer

    def print_reviews(self):
        """ Print list of reviews for movie """
        print 'Title', self.title, '. Reviews (pages=', self.total_pages_reviews, '):'
        for review in self.reviews:
            print review

    def load_info(self, config):
        """Get information about movie from themoviedb API"""
        json_movie = request_helper.get_movie_by_id(config, self.id)

        self.title = json_movie['title']
        self.original_language = json_movie['original_language']
        self.production_countries = [ country['name'] for country in json_movie['production_countries']]
        self.production_companies = [ company['name'] for company in json_movie['production_companies']]
        self.release_date = json_movie['release_date']
        self.imdb_id = json_movie['imdb_id']
        self.genres = [ genre['name'] for genre in json_movie['genres']]
        self.runtime = json_movie['runtime']
        self.overview = json_movie['overview']
        self.poster_url = '{0}{1}'.format(config['url']['poster'], json_movie['poster_path'])
        self.vote_average = json_movie['vote_average']
        self.vote_count = json_movie['vote_count']

    def load_trailer(self, config):
        """ Get trailer of movie from themoviedb API """
        json_videos = request_helper.get_videos_by_id(config, self.id)

        self.trailer_url = ['{0}/{1}'.format(config['url']['youtube'], video['key']) 
                         for video in json_videos['results'] if video['site'] == 'YouTube']

    def load_crew(self, config):
        """ Get information about actors, director, writer from themoviedb API"""
        json_crew = request_helper.get_crew_by_id(config, self.id)

        # Actors
        for actor in json_crew['cast']:
            profile_url = None
            if actor['profile_path'] is not None:
                profile_url = '{0}{1}'.format(config['url']['profile'], actor['profile_path'])
            self.actors.append(Person(actor['id'], actor['name'], profile_url, config))

        # Directors and writers
        for person in json_crew['crew']:
            if person['job'] in ['Director', 'Screenplay']:
                profile_url = None
                if person['profile_path'] is not None:
                    profile_url = '{0}{1}'.format(config['url']['profile'], person['profile_path'])
                crew_member = Person(person['id'], person['name'], profile_url, config)
                if person['job'] == 'Director':
                    self.directors.append(crew_member)
                if person['job'] == 'Screenplay':
                    self.writers.append(crew_member)

    def load_reviews(self, config):
        """Get review about movie from themoviedb API"""
        json_reviews = request_helper.get_reviews_by_id(config, self.id)

        for result in json_reviews['results']: 
            self.reviews.append(Review(result['author'], result['content']))
        self.total_pages_reviews = json_reviews['total_pages']
        self.total_reviews = json_reviews['total_results']

    def create(self, config):
        """ Load all information about movie to the movie instance"""

        # Load information about movie from themoviedb API
        self.load_info(config)
        # Load trailer of movie from themoviedb API
        self.load_trailer(config)
        # Load information about actors, director, writer from themoviedb API
        self.load_crew(config)
        # Load review about movie from themoviedb API
        self.load_reviews(config)

        #self.imdb_rating = None
    
    def exists(self):
        return True


class Person(object):
    """Person class"""
    def __init__(self, person_id, name, profile_url, config):
        self.id = person_id
        self.name = name
        self.profile_url = profile_url
        self.wikipedia_url = '{0}/{1}'.format(config['url']['wikipedia'], name.replace(' ','_'))

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Person id={0} name={1} profile={2}>".format(self.id, self.name, self.profile_url)


class Review(object):
    """Review class"""
    def __init__(self, name, text=""):
        self.name = name
        self.text = text

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Review name={0} text={1}>".format(self.name, self.text)
