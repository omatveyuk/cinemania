"""Models and database functions for users. Movie project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of movie website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    dob = db.Column(db.DateTime, nullable=True)
    genres = db.relationship('UserGenre')
    movies = db.relationship('UserMovie')

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Genre(db.Model):
    """Genre of movies from movie website."""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user = db.relationship('UserGenre')

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Genre genre_id=%s name=%s>" % (self.genre_id, self.name)


class Movie(db.Model):
    """Movie from movie website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    themoviedb_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)
    user = db.relationship('UserMovie')

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<Movie movie_id=%s title=%s>" % (self.movie_id, self.title)


class UserGenre(db.Model):
    """User's favorite genres from movie website"""

    __tablename__ = "user_genres"

    usergenre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False)
    genre_id = db.Column(db.Integer,
                         db.ForeignKey('genres.genre_id'),
                         nullable=False)

    user_g = db.relationship('User')
    genre = db.relationship('Genre')

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<User's genres id=%s user_id=%s genre_id=%s>" % (self.usergenre_id,
                                                                 self.user_id,
                                                                 self.genre_id)

class UserMovie(db.Model):
    """Movie which user nas already seen from movie website"""

    __tablename__ = "user_movies"

    usermovie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False)
    movie_id = db.Column(db.Integer,
                         db.ForeignKey('movies.movie_id'),
                         nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    seen = db.Column(db.Boolean, default=False)

    user_m = db.relationship('User')
    movie = db.relationship('Movie')

    def __repr__(self):
        """Provide helpful represetration when printed"""
        return "<User's movies id=%s user_id=%s movie_id=%s>" % (self.usermovie_id,
                                                                 self.user_id,
                                                                 self.movie_id)
##############################################################################
# Helper functions
def check_movie(movie):
    """Check if movie exists in list of movie(Movie)."""
    check_movie = Movie.query.filter_by(themoviedb_id=movie.id).first()
    if check_movie is None:
        return False
    return True


def add_movie(movie, user_id):
    """Add random chosen movie to user's movie list(UserMovie) and list of movies(Movie)."""

    # Movie
    print "\n\n"
    print "Check in Movie. themoviedb_id= {0}; title= {1}".format(movie.id, movie.title)
    print "\n**********************************************************"
    if not check_movie(movie):
        print "\n\n"
        print "themoviedb_id= {0}; title= {1} DOESN'T EXIST".format(movie.id, movie.title)
        print "\n**********************************************************"
        random_movie = Movie(themoviedb_id=movie.id,
                             title=movie.title,
                             poster_url=movie.poster_url)
        db.session.add(random_movie)
        db.session.commit()     # add to db and create movie_id ptimary key
        print "\n\n"
        print "Add movie"
        print "\n**********************************************************"

    # UserMovie
    # Before add movie yo UserMovie check that commit above is successful
    if check_movie(movie):
        print "\n\n"
        print "themoviedb_id= {0}; title= {1} EXISTS in Movie".format(movie.id, movie.title)
        print "\n**********************************************************"
        movie_id=Movie.query.filter_by(themoviedb_id=movie.id).first().movie_id
        print "\n\n"
        print "movie_id in Movie".format(movie_id)
        print "\n**********************************************************"
        user_movie = UserMovie(user_id=user_id,
                               movie_id=movie_id,
                               rating=None,
                               seen=False)
        db.session.add(user_movie)
        db.session.commit()
        print "\n\n"
        print "Add movie to UserMovie"
        print "\n**********************************************************"


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///movie'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB.",  app.config['SQLALCHEMY_DATABASE_URI']