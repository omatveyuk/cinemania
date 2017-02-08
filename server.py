"""Flask server for Cinemania game"""

import os                   #to access my OS environment variables
from flask import Flask, request, render_template, flash, jsonify
import jinja2
from flask_debugtoolbar import DebugToolbarExtension
import requests

import request_helper
from model import Movie, Person, Review
import model



app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "shhhhhhhhhhhhhh"

# Normally, if you refer to an undefined variable in a Jinja template,
# Jinja silently ignores this. This makes debugging difficult, so we'll
# set an attribute of the Jinja environment that says to make this an
# error.
#app.jinja_env.undefined = jinja2.StrictUndefined
#loader=jinja2.FileSystemLoader('templates')

config = {}

def configure():
    config['api_key'] = {}
    config['api_key']['themoviedb'] = os.environ['THEMOVIEDB_API_KEY']
    config['url'] = {}
    config['url']['popular'] = "https://api.themoviedb.org/3/movie/popular?api_key={0}".format(config['api_key']['themoviedb'])
    config['url']['movie'] = "https://api.themoviedb.org/3/movie"
    config['url']['poster'] = "https://image.tmdb.org/t/p/w500"
    config['url']['youtube'] = "https://www.youtube.com/watch?v="
    config['url']['profile'] = "https://image.tmdb.org/t/p/w500"

@app.route('/')
def index():
    """Show our homepage page."""
    #return "Cinemania"
    return render_template("homepage.html")

@app.route('/random_movie')
def get_random_movie():
    """Return random movie from themoviedb API."""

    # Get random movie id from themoviedb API
    movie_id = request_helper.get_random_movie_id(config)
    movie = Movie(movie_id)

    # Load information about movie from themoviedb API
    movie.load_info(config)

    # Load trailer of movie from themoviedb API
    movie.load_trailer(config)

    # Load information about actors, director, writer from themoviedb API
    movie.load_crew(config)

    # Load review about movie from themoviedb API
    movie.load_reviews(config)

    #self.imdb_rating = None


    #if not movie.exists():
    #    return "Error"

    html = 'cinemnia: {0} ({10})<br> Production country: {1}<br> Production companies: {2}<br>'
    html += 'Release date: {3}<br> IMDB id: {4}<br> Genres: {5}<br> Runtime: {6}<br>'
    html += 'Poster: {7}<br> Vote average: {8}<br> Vote count: {9}<br><br>'
    html += 'Actors:<br>'
    for actor in movie.actors:
        html += str(actor.id) + ' ' + str(actor.name) + ' ' + str(actor.profile_url) + '<br>'
    html += 'Directors:<br>'
    for director in movie.directors:
        html += str(director.id) + ' ' + str(director.name) + ' ' + str(director.profile_url) + '<br>'
    html += 'Writers:<br>'
    for writer in movie.writers:
        html += str(writer.id) + ' ' + str(writer.name) + ' ' + str(writer.profile_url) + '<br>'
    html += '<br>Reviews (pages=' + str(movie.tototal_pages_reviews) + '):<br>'
    for review in movie.reviews:
        html += str(review.name).upper() + ': ' + str(review.text) + '<br>'
    html += '<br>Video:<br>'
    for video in movie.trailer_url:
        html += video + '<br>'
    html = html.format(movie.title,
                       movie.production_countries,
                       movie.production_companies,
                       movie.release_date,
                       movie.imdb_id,
                       movie.genres,
                       movie.runtime,
                       movie.poster_url,
                       movie.vote_average,
                       movie.vote_count,
                       movie.id)
    #return html
    return render_template("movie.html", movie=movie)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    configure()
    app.run(host="0.0.0.0")
