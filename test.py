"""Testing"""

import unittest

from server import app
from flask_sqlalchemy import SQLAlchemy
from model_user import Movie, Genre, User, UserMovie, UserGenre, db, connect_to_db
#db = SQLAlchemy()

class CinemaniaTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True


    def test_homepage(self):
        """Test start page."""
        result = self.client.get("/")
        self.assertIn("Welcome", result.data)
        self.assertIn("to choose a movie randomly", result.data)

    def test_movie_page_random(self):
        """Test movie page for movie randomly choosen."""
        result = self.client.get("/random_movie")
        self.assertIn("Country:", result.data)

    def test_login(self):
        """Test Login page"""
        result = self.client.get("/login")
        self.assertIn("Would you like to register?", result.data)


class PartyTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, 'postgresql:///testdb')

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at the end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_register(self):
        """Test register page"""
        result = self.client.get("/register")
        self.assertIn("User name", result.data)

    def test_user_in_session(self):
        """Test that the user's page displays movies that already are seen
           from example_data()"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['logged_in_user_id'] = 3
        result = self.client.get('/users/3')
        self.assertIn("Your favorite genre:",  result.data)

    def test_register_successfully(self):
        """Test user was added successfully"""
        result = self.client.post("/register",
                                  data={"username": "oxana",
                                        "e-mail": "oxana@oxana.com",
                                        "password": "oxana71",
                                        "dob": None,
                                        "genres": ["Drama", "Animation"]},
                                  follow_redirects=True)
        self.assertIn("User sucsuccessfully added", result.data)

    def test_register_user_already_exists(self):
        """Test: user already exists"""
        result = self.client.post("/register",
                                  data={"username": "Fred",
                                        "e-mail": "Fred@Fred.com",
                                        "password": "Fred25",
                                        "dob": None,
                                        "genres": []},
                              follow_redirects=True)
        self.assertIn("User already exists", result.data)


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
                password="Fred25",
                dob="30-Aug-2000")
    ann = User(name=None,
               email="Ann@Ann.com",
                password="Ann25",
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
