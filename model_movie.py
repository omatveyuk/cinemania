""" Model """
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import request_helper
from datetime import datetime
import json

##############################################################################
# Model definitions

class Movie(object):
    """ Movie class """
    def __init__(self, movie_id):
        self.id = movie_id          # id in themoviedb API
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

    def repr_json(self):
        return dict(id=self.id,
                    title=self.title,
                    original_language=self.original_language,
                    production_countries=self.production_countries,
                    production_companies=self.production_companies,
                    release_date=self.release_date,
                    imdb_id=self.imdb_id,
                    imdb_rating=self.imdb_rating,
                    genres=self.genres,
                    runtime=self.runtime,
                    directors=self.directors,
                    writers=self.writers,
                    actors=self.actors,
                    overview=self.overview,
                    trailer_url=self.trailer_url,
                    poster_url=self.poster_url,
                    reviews=self.reviews,
                    total_pages_reviews=self.total_pages_reviews,
                    total_reviews=self.total_reviews,
                    vote_average=self.vote_average,
                    vote_count=self.vote_count)

    @classmethod
    def load_from_JSON(cls, json_movie, config):
        """Load movie from JSON"""
        movie = cls(json_movie["id"])       # create instance using constructor
        movie.title = json_movie["title"]
        movie.original_language = json_movie["original_language"]
        movie.production_countries = json_movie["production_countries"]
        movie.production_companies = json_movie["production_companies"]
        movie.release_date = json_movie["release_date"]
        movie.imdb_id = json_movie["imdb_id"]
        movie.imdb_rating = json_movie["imdb_rating"]
        movie.genres = json_movie["genres"]
        movie.runtime = json_movie["runtime"]
        movie.directors = [ Person(person["id"], person["name"], person["profile_url"], config['url']['wikipedia']) for person in json_movie["directors"]]
        movie.writers = [ Person(person["id"], person["name"], person["profile_url"], config['url']['wikipedia']) for person in json_movie["writers"]]
        movie.actors = [ Person(person["id"], person["name"], person["profile_url"], config['url']['wikipedia']) for person in json_movie["actors"]]
        movie.overview = json_movie["overview"]
        movie.trailer_url = json_movie["trailer_url"]
        movie.poster_url = json_movie["poster_url"]
        movie.reviews = [ Review(review["name"], review["text"]) for review in json_movie["reviews"]]
        movie.total_pages_reviews = json_movie["total_pages_reviews"]
        movie.total_reviews = json_movie["total_reviews"]
        movie.vote_average = json_movie["vote_average"]
        movie.vote_count = json_movie["vote_count"]
        return movie

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
        release_date = datetime.strptime(str(json_movie['release_date']), '%Y-%m-%d').strftime('%d-%b-%Y') if json_movie['release_date'] != "" else ""

        self.title = json_movie['title']
        self.original_language = json_movie['original_language']
        self.production_countries = [ country['name'] for country in json_movie['production_countries']]
        self.production_companies = [ company['name'] for company in json_movie['production_companies']]
        self.release_date = release_date
        self.imdb_id = json_movie['imdb_id']
        self.genres = [ genre['name'] for genre in json_movie['genres']]
        self.runtime = json_movie['runtime']
        self.overview = json_movie['overview']
        if json_movie['poster_path'] is not None:
            self.poster_url = '{0}{1}'.format(config['url']['poster'], json_movie['poster_path'])
        else:
            self.poster_url = None
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

        print "*****************INSIDE LOAD_CREW*****************"

        # Actors
        for actor in json_crew['cast']:
            profile_url = None
            if actor['profile_path'] is not None:
                profile_url = '{0}{1}'.format(config['url']['profile'], actor['profile_path'])
            self.actors.append(Person(actor['id'], actor['name'], profile_url, config['url']['wikipedia']))

        # Directors and writers
        for person in json_crew['crew']:
            if person['job'] in ['Director', 'Screenplay']:
                profile_url = None
                if person['profile_path'] is not None:
                    profile_url = '{0}{1}'.format(config['url']['profile'], person['profile_path'])
                crew_member = Person(person['id'], person['name'], profile_url, config['url']['wikipedia'])
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

    def load(self, config):
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
    def __init__(self, person_id, name, profile_url, wikipedia_url):
        self.id = person_id
        self.name = name
        self.profile_url = profile_url
        self.wikipedia_url = '{0}/{1}'.format(wikipedia_url, name.replace(' ', '_'))
        print "**********************************************"
        print 'Class Person'
        print "wikipedia_url(config)", wikipedia_url
        print "Name: ", self.name
        print "wkikipedia url: ", self.wikipedia_url


    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Person id={0} name={1} profile={2}>".format(self.id, self.name, self.profile_url)

    def repr_json(self):
        return dict(id=self.id,
                    name=self.name,
                    profile_url=self.profile_url,
                    wikipedia_url=self.wikipedia_url)


class Review(object):
    """Review class"""
    def __init__(self, name, text=""):
        self.name = name
        self.text = text

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Review name={0} text={1}>".format(self.name, self.text)

    def repr_json(self):
        return dict(name=self.name,
                    text=self.text)


class PersonNode(object):
    """Node representing a person in a cast graph
       person - object of class Person
       movies - dictionary of movies where person participated
    """

    def __init__(self, person, movies, adjacent=None):
        """Create a person node with another actors adjacent
           person - object of class Person
           movies - dictionary of movies (id: name)
        """

        if adjacent is None:
            adjacent = set()

        assert isinstance(adjacent, set), \
            "adjacent must be a set!"

        self.person = person
        self.movies = movies
        self.adjacent = adjacent

    def __repr__(self):
        """Debugging-friendly representation"""
        return "<PersonNode: {0}; Movies: {1}>".format(self.person, self.movies.keys())

    def print_node(self):
        """Print node"""
        print "\nPersonNode:"
        print self.person
        for key, value in self.movies.items():
            print key, value
        print self.adjacent


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)
