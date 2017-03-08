"""Testing"""

import unittest

from server import app, config
from flask import session
from flask_sqlalchemy import SQLAlchemy
import model_movie as mm
import model_user as mu
from model_user import Movie, Genre, User, UserMovie, UserGenre, db, connect_to_db

class CinemaniaTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        """Test start page."""
        result = self.client.get("/")
        self.assertIn("Welcome", result.data)
        self.assertIn("to peek at randomly selected movie", result.data)

    def test_movie_page_random(self):
        """Test movie page for movie randomly choosen."""
        result = self.client.get("/random_movie")
        self.assertIn("Country:", result.data)


class TestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['SECRET_KEY'] = 'key'
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, 'postgresql:///testdb')

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at the end of every test."""
        db.session.close()
        db.drop_all()

    def test_user_in_session(self):
        """Test that the user's page displays movies that already are seen
           from example_data()"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['logged_in_user_id'] = 3
        result = self.client.get('/users/3')
        self.assertIn("Your favorite genre:", result.data)

    def test_check_movie(self):
        """Test checking if movie exists in list of movie(Movie)."""
        # Create movie objects which contain information about movie
        movie_not_in_db = mm.Movie(271110)
        movie_not_in_db.load(config)
        movie_in_db = mm.Movie(135397)
        movie_in_db.load(config)

        self.assertFalse(mu.check_movie(movie_not_in_db))
        self.assertTrue(mu.check_movie(movie_in_db))

    def test_add_movie(self):
        """Test adding movie to user's movie list(UserMovie) and list of movies(Movie)"""
        # Create movie objects which contain information about movie
        movie_not_in_db = mm.Movie(155)
        movie_not_in_db.load(config)

        mu.add_movie(movie_not_in_db, 1)
        self.assertTrue(mu.check_movie(movie_not_in_db))
        self.assertTrue(mu.is_movie_in_user_movies_list(1, 155))

    def test_get_user_movie_rating(self):
        """Test fetching user's rating for movie."""

        self.assertEqual(mu.get_user_movie_rating(135397, 1), 5)
        self.assertIsNone(mu.get_user_movie_rating(238, 1))

    def test_update_rating(self):
        """Test updating user's rating for movie"""
        user_id = 1
        movie_id = 5
        rating = 6
        mu.update_rating(user_id, movie_id, rating)
        usermovie_rating = mu.UserMovie.query.filter(mu.UserMovie.user_id == user_id,
                                                     mu.UserMovie.movie_id == movie_id).first().rating
        self.assertEqual(usermovie_rating, 6)
        movie_id = 7
        mu.update_rating(user_id, movie_id, rating)
        usermovie_rating = mu.UserMovie.query.filter(mu.UserMovie.user_id == user_id,
                                                     mu.UserMovie.movie_id == movie_id).first()
        self.assertIsNone(usermovie_rating)

    def test_get_user(self):
        """Test fetching user"""
        user_id = 1
        self.assertEqual(mu.get_user(user_id).email, "Fred@Fred.com")
        user_id = 4
        self.assertIsNone(mu.get_user(user_id))

    def test_get_user_movies(self):
        """Test fetching all user's movies for user's page"""
        user_id = 2
        self.assertEqual(len(mu.get_user_movies(user_id)), 0)
        user_id = 3
        self.assertEqual(len(mu.get_user_movies(user_id)), 0)
        user_id = 1
        self.assertEqual(len(mu.get_user_movies(user_id)), 6)

    def test_is_movie_in_user_movies_list(self):
        """Test checking if movie exists in user's list of movie"""
        user_id = 1
        themoviedb_id = 381288
        self.assertTrue(mu.is_movie_in_user_movies_list(user_id, themoviedb_id))
        themoviedb_id = 155
        self.assertFalse(mu.is_movie_in_user_movies_list(user_id, themoviedb_id))
        user_id = 2
        self.assertFalse(mu.is_movie_in_user_movies_list(user_id, themoviedb_id))

    def test_get_user_genres(self):
        """Test fetching user's genre preference"""
        user_id = 1
        self.assertEqual(len(mu.get_user_genres(user_id)), 4)
        user_id = 2
        self.assertEqual(len(mu.get_user_genres(user_id)), 0)

    def test_add_user(self):
        """Test adding user to db"""
        info_user = ['oxana@oxana.com', 'oxana25', 'Cinemania']
        user_id = mu.add_user(info_user)
        self.assertTrue(mu.User.query.get(user_id))

def example_data():
    """Create the sample data for testing"""

    genre1 = Genre(name="Music",
                   themoviedb_id=10402)
    genre2 = Genre(name="War",
                   themoviedb_id=10752)
    genre3 = Genre(name="Comedy",
                   themoviedb_id=35)
    genre4 = Genre(name="Family",
                   themoviedb_id=10751)
    db.session.add_all([genre1, genre2, genre3, genre4])
    db.session.commit()

    fred = User(name="Fred",
                email="Fred@Fred.com",
                password="$2b$12$OQXSZA0n7p5Z8lTVuHhnOuA3TMSCA5/PvTwfqWr4Xh2jc9HKYSBdy",
                provider="Cinemania",
                dob="30-Aug-2000")
    ann = User(name=None,
               email="Ann@Ann.com",
               password="'$2b$12$rWDF8EBsY9g7PdQzMi8KluFvEkzfTctaYbZ9p5Vqjl5/l5M8G/u5i'",
               provider="Cinemania",
               dob=None)
    db.session.add_all([fred, ann])
    db.session.commit()

    movie1 = Movie(themoviedb_id=135397,
                   title="Jurassic World",
                   poster_url="https://image.tmdb.org/t/p/w500/jjBgi2r5cRt36xF6iNUEhzscEcb.jpg")
    movie2 = Movie(themoviedb_id=381288,
                   title="Split",
                   poster_url="https://image.tmdb.org/t/p/w500/rXMWOZiCt6eMX22jWuTOSdQ98bY.jpg")
    movie3 = Movie(themoviedb_id=283366,
                   title="Miss Peregrine's Home for Peculiar Children",
                   poster_url="https://image.tmdb.org/t/p/w500/uSHjeRVuObwdpbECaXJnvyDoeJK.jpg")
    movie4 = Movie(themoviedb_id=205596,
                   title="The Imitation Game",
                   poster_url="https://image.tmdb.org/t/p/w500/noUp0XOqIcmgefRnRZa1nhtRvWO.jpg")
    movie5 = Movie(themoviedb_id=226,
                   title="Boys Don't Cry",
                   poster_url="https://image.tmdb.org/t/p/w500/6bqIZTEuJnUrgnxcymciszvOz8J.jpg")
    movie6 = Movie(themoviedb_id=11858,
                   title="Renaissance Man",
                   poster_url="https://https://image.tmdb.org/t/p/w500/uaiykEOEFs91WclowDhsVYNdGfX.jpg")
    db.session.add_all([movie1, movie2, movie3, movie4, movie5, movie6])
    db.session.commit()


    fred_music = UserGenre(user_id=fred.user_id,
                           genre_id=genre1.genre_id)
    fred_war = UserGenre(user_id=fred.user_id,
                         genre_id=genre2.genre_id)
    fred_comedy = UserGenre(user_id=fred.user_id,
                            genre_id=genre3.genre_id)
    fred_family = UserGenre(user_id=fred.user_id,
                            genre_id=genre4.genre_id)

    fred_movie1 = UserMovie(user_id=fred.user_id,
                            movie_id=movie1.movie_id,
                            rating=5,
                            seen="f")
    fred_movie2 = UserMovie(user_id=fred.user_id,
                            movie_id=movie2.movie_id,
                            rating=None,
                            seen="f")
    fred_movie3 = UserMovie(user_id=fred.user_id,
                            movie_id=movie3.movie_id,
                            rating=8,
                            seen="t")
    fred_movie4 = UserMovie(user_id=fred.user_id,
                            movie_id=movie4.movie_id,
                            rating=2,
                            seen="t")
    fred_movie5 = UserMovie(user_id=fred.user_id,
                            movie_id=movie5.movie_id,
                            rating=3,
                            seen="f")
    fred_movie6 = UserMovie(user_id=fred.user_id,
                            movie_id=movie6.movie_id,
                            rating=9,
                            seen="t")
    db.session.add_all([fred_music, fred_war, fred_comedy, fred_family,
                        fred_movie1, fred_movie2, fred_movie3, fred_movie4, fred_movie5, fred_movie6])
    db.session.commit()


if __name__ == "__main__":
    unittest.main()
