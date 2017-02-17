"""Utility file to seed movie database from data files in seed_data/"""

from sqlalchemy import func
from model_user import User
from model_user import Movie
from model_user import Genre
from model_user import UserGenre
from model_user import UserMovie
import datetime

from model_user import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        # unpacking
        user_id, name, email, password, dob = row.split(",")
        if dob:
            dob = datetime.datetime.strptime(dob, "%d-%b-%Y")
        else:
            dob = None

        user = User(user_id=user_id,
                    name=name,
                    email=email,
                    password=password,
                    dob=dob)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_genres():
    """Load genres from u.genre into database."""
    print "Genres"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Genre.query.delete()

    # Read u.genre file and insert data
    for row in open("seed_data/u.genre"):
        row = row.rstrip()
        # unpacking
        genre_id, name = row.split(",")

        genre = Genre(genre_id=genre_id,
                      name=name)

        # We need to add to the session or it won't ever be stored
        db.session.add(genre)

    # Once we're done, we should commit our work
    db.session.commit()

def load_movies():
    """Load movies from u.movie into database."""
    print "Movies"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Movie.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.movie"):
        row = row.rstrip()
        # unpacking
        movie_id, themoviedb_id, title, poster_url = row.split(",")

        movie = Movie(movie_id=movie_id,
                      themoviedb_id=themoviedb_id,
                      title=title,
                      poster_url=poster_url)

        # We need to add to the session or it won't ever be stored
        db.session.add(movie)

    # Once we're done, we should commit our work
    db.session.commit()


def load_user_genres():
    """Load user's favorite genres from u.usergenre into database."""
    print "User's genres"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    UserGenre.query.delete()

    # Read u.user_genre file and insert data
    for row in open("seed_data/u.user_genre"):
        row = row.rstrip()
        usergenre_id, user_id, genre_id = row.split(",")

        user_genre = UserGenre(usergenre_id=usergenre_id,
                        user_id=user_id,
                        genre_id=genre_id)

        # We need to add to the session or it won't ever be stored
        db.session.add(user_genre)

    # Once we're done, we should commit our work
    db.session.commit()


def load_user_movies():
    """Load movies which uses has already seen from u.usermovie into database."""
    print "User's movies"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    UserMovie.query.delete()

    # Read u.user_genre file and insert data
    for row in open("seed_data/u.user_movie"):
        row = row.rstrip()
        usermovie_id, user_id, movie_id, rating, seen = row.split(",")
        if not rating:
            rating = None

        user_movie = UserMovie(usermovie_id=usermovie_id,
                        user_id=user_id,
                        movie_id=movie_id,
                        rating=rating,
                        seen=seen)

        # We need to add to the session or it won't ever be stored
        db.session.add(user_movie)

    # Once we're done, we should commit our work
    db.session.commit()

def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_movie_id():
    """Set value for the next movie_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Movie.movie_id)).one()
    max_id = int(result[0])

    # Set the value for the next movie_id to be max_id + 1
    query = "SELECT setval('movies_movie_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_user_movies_id():
    """Set value for the next usermovie_id after seeding database"""

    # Get the Max usermovie_id in the database
    result = db.session.query(func.max(UserMovie.usermovie_id)).one()
    max_id = int(result[0])

    # Set the value for the next movie_id to be max_id + 1
    query = "SELECT setval('user_movies_usermovie_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_user_genres_id():
    """Set value for the next usergenre_id after seeding database"""

    # Get the Max usermovie_id in the database
    result = db.session.query(func.max(UserGenre.usergenre_id)).one()
    max_id = int(result[0])

    # Set the value for the next movie_id to be max_id + 1
    query = "SELECT setval('user_genres_usergenre_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_genres()
    load_user_genres()
    load_user_movies()
    set_val_user_id()
    set_val_movie_id()
    set_val_user_movies_id()
    set_val_user_genres_id()