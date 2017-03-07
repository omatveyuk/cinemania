"""Models and database functions for users. Movie project."""

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import bcrypt

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
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    provider = db.Column(db.String(30), nullable=True)
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
    themoviedb_id = db.Column(db.Integer, nullable=False)
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
    if not check_movie(movie):
        random_movie = Movie(themoviedb_id=movie.id,
                             title=movie.title,
                             poster_url=movie.poster_url)
        db.session.add(random_movie)
        db.session.commit()     # add to db and create movie_id ptimary key

    # UserMovie
    # Before add movie to UserMovie check that commit above is successful
    if check_movie(movie):
        if not is_movie_in_user_movies_list(user_id, movie.id):
            movie_id = Movie.query.filter_by(themoviedb_id=movie.id).first().movie_id
            user_movie = UserMovie(user_id=user_id,
                                      movie_id=movie_id,
                                      rating=None,
                                      seen=False)
            db.session.add(user_movie)
            db.session.commit()


def get_user_movie_rating(movie_id, user_id):
    """Return user's rating for movie."""
    user_movierating = None

    movie_db = Movie.query.filter(Movie.themoviedb_id == movie_id).first()
    if movie_db is not None:
        id_movie_db = movie_db.movie_id
        user_movierating = UserMovie.query.filter(UserMovie.user_id == user_id,
                                                  UserMovie.movie_id == id_movie_db).first().rating

    return user_movierating


def update_rating(user_id, movie_id, rating):
    """Update user's movie rating"""
    usermovie_rating = UserMovie.query.filter(UserMovie.user_id == user_id,
                                              UserMovie.movie_id == movie_id).first()
    if usermovie_rating:
        usermovie_rating.rating = rating
    db.session.commit()


def get_user(user_id):
    """Return information about user: name, email, password, dob."""
    return User.query.get(user_id)


def get_user_movies(user_id):
    """ Return user's list of movies."""
    movies = db.session.query(UserMovie.movie_id,
                              UserMovie.rating,
                              UserMovie.seen,
                              Movie.title,
                              Movie.poster_url,
                              Movie.themoviedb_id).join(Movie).filter(UserMovie.user_id == user_id).order_by(Movie.title).all()

    return movies


def is_movie_in_user_movies_list(user_id, themoviedb_id):
    """Return true if user has already seen the movie"""
    # get movies id which user has already seen
    user_movies = [movie[5] for movie in get_user_movies(user_id)]
    if themoviedb_id in user_movies:
        return True
    return False


def get_user_genres(user_id):
    """ Return user's genre preference."""
    genres = db.session.query(UserGenre.genre_id,
                              Genre.name,
                              Genre.themoviedb_id).join(Genre).filter(UserGenre.user_id == user_id).all()
    return genres


def add_user(info_user):
    """Add new user."""
    email, password, provider = info_user
    print email, password

    user = User.query.filter_by(email=email).first()
    if user is None:
        # Hash a password with a randomly-generated salt"
        hashed = bcrypt.hashpw(password.encode('UTF_8'), bcrypt.gensalt())
        user = User(name=None, email=email, password=hashed, provider=provider, dob=None)
        db.session.add(user)
        db.session.commit()

        user_id = User.query.filter(User.email == email).first().user_id
        # check that commit is successful
        if user is not None:
            return user_id
    else:
        return 0


def add_info_user(info_user):
    """Add info from registration form"""
    user_id, name, dob, genres = info_user
    user = get_user(user_id)

    # Information about user
    user.name = name
    user.dob = dob
    db.session.commit()

    # Genres' preferences
    delete_user_genres(user_id)
    add_user_genres(user_id, genres)


def delete_user_genres(user_id):
    """Delete user's genre preferences"""
    genres = UserGenre.query.filter(UserGenre.user_id == user_id).delete()
    db.session.commit()


def add_user_genres(user_id, genres):
    """Add user's genre preference."""
    for genre in genres:
        genre_id = Genre.query.filter_by(name=genre).first().genre_id
        usergenre_id = UserGenre.query.filter(UserGenre.user_id == user_id,
                                              UserGenre.genre_id == genre_id).first()
        if usergenre_id is None:
            usergenre = UserGenre(user_id=user_id, genre_id=genre_id)
            db.session.add(usergenre)
    db.session.commit()


def is_user(email, password):
    """Return user id if user is valid, overwise 0(false)."""
    # Check that a unhashed password matches password in db which
    # has previously been hashed
    user = User.query.filter(User.email == email).first()
    if user is not None:
        if bcrypt.hashpw(password.encode('UTF_8'), user.password.encode('UTF_8')) == user.password.encode('UTF_8'):
            return user.user_id

    return 0


def connect_to_db(app, db_url='postgresql:///movie'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB.",  app.config['SQLALCHEMY_DATABASE_URI']