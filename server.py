"""Flask server for Cinemania game"""

import os                   #to access my OS environment variables
from flask import Flask, request, render_template, flash, jsonify
import jinja2
from flask_debugtoolbar import DebugToolbarExtension
import requests

import request_helper
from model_movie import Movie, Person, Review
import model_movie


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
    return render_template("homepage.html")

@app.route('/random_movie')
def get_random_movie():
    """Return random movie from themoviedb API."""

    # Get random movie id from themoviedb API
    movie_id = request_helper.get_random_movie_id(config)

    # Create movie object which contain information about movie
    movie = Movie(movie_id)
    movie.create(config)

    return render_template("movie.html", movie=movie)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    configure()
    app.run(host="0.0.0.0")
