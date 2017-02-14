"""Flask server for Cinemania game"""

import os                   #to access my OS environment variables
from flask import Flask, session, request, render_template, flash, jsonify
import jinja2
from flask_debugtoolbar import DebugToolbarExtension
import requests

import request_helper as rh
from model_movie import Movie, Person, Review
import model_movie
from model_user import connect_to_db, db
import model_user as mu   # will use User, Movie, Genre, UserGenre, UserMovie


app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "shhhhhhhhhhhhhh"

config = {}

def configure():
    config['api_key'] = {}
    config['api_key']['themoviedb'] = os.environ['THEMOVIEDB_API_KEY']
    config['url'] = {}
    config['url']['popular'] = "https://api.themoviedb.org/3/movie/popular?api_key={0}".format(config['api_key']['themoviedb'])
    config['url']['movie'] = "https://api.themoviedb.org/3/movie"
    config['url']['poster'] = "https://image.tmdb.org/t/p/w500"
    config['url']['youtube'] = "https://www.youtube.com/embed"
    config['url']['profile'] = "https://image.tmdb.org/t/p/w500"
    config['url']['wikipedia'] = "https://en.wikipedia.org/wiki"

@app.route('/')
def index():
    session["logged_in_user_id"] = 3
    #print('/n/n', session["logged_in_user_id"])
    #del session["logged_in_user_id"]
    #print('/n/n*********************************************************')

    #return render_template("homepage.html", user_id=session["logged_in_user_id"])
    return render_template("homepage.html")

@app.route('/posters.json')
def get_posters():
    """Get 40 posters for animation"""
    return jsonify(rh.get_posters_for_animation(config))


@app.route('/random_movie')
def get_random_movie():
    """Return random movie from themoviedb API."""
    # Get random movie id from themoviedb API
    movie_id = rh.get_random_movie_id(config)

    # Create movie object which contain information about movie
    movie = Movie(movie_id)
    movie.load(config)

    return render_template("movie_details.html", movie=movie)


@app.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    """Return movie from themoviedb API by given movie id."""
    # Create movie object which contain information about movie
    movie = Movie(movie_id)
    movie.load(config)

    return render_template("movie_details.html", movie=movie)


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Return page showing the user's list of movies."""
    user = mu.User.query.get(user_id)
    movies = db.session.query(mu.UserMovie.movie_id,
                              mu.UserMovie.rating,
                              mu.UserMovie.seen,
                              mu.Movie.title,
                              mu.Movie.poster_url,
                              mu.Movie.themoviedb_id).join(mu.Movie).filter(mu.UserMovie.user_id == user_id).all()
    genres = db.session.query(mu.UserGenre.genre_id,
                              mu.Genre.name).join(mu.Genre).filter(mu.UserGenre.user_id == user_id).all()

    return render_template("user_details.html",
                           user=user,
                           movies=movies,
                           genres=genres,
                           posters_url=config['url']['poster'])


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    configure()
    app.run(host="0.0.0.0")
