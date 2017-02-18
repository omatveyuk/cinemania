"""Flask server for Cinemania game"""

import os                   #to access my OS environment variables
from flask import Flask, session, request, redirect, render_template, flash, jsonify
import jinja2
from flask_debugtoolbar import DebugToolbarExtension
import requests

import request_helper as rh
from model_movie import Movie, Person, Review
import model_movie
import model_user as mu


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


@app.route('/posters.json')
def get_posters():
    """Get 40 posters for animation."""
    return jsonify(rh.get_posters_for_animation(config))


@app.route('/random_movie')
def get_random_movie():
    """Return random movie from themoviedb API."""
    # Get random movie id from themoviedb API
    movie_id = rh.get_random_movie_id(config)

    # Create movie object which contain information about movie
    movie = Movie(movie_id)
    movie.load(config)

    # if user login add movie to user's movie list
    if "logged_in_user_id" in session:
        mu.add_movie(movie, session["logged_in_user_id"])

    return render_template("movie_details.html", movie=movie)


@app.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    """Return movie from themoviedb API by given movie id."""
    # Create movie object which contain information about movie
    movie = Movie(movie_id)
    movie.load(config)

    # Get user's rating for movie
    user_movierating = mu.get_user_movie_rating(movie_id)

    return render_template("movie_details.html", movie=movie, user_movierating=user_movierating)


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Return page showing the user's movie list."""
    user = mu.get_user(user_id)
    movies = mu.get_user_movies(user_id)
    genres = mu.get_user_genres(user_id)

    return render_template("user_details.html",
                           user=user,
                           movies=movies,
                           genres=genres)


@app.route("/change_rating.json", methods=['POST'])
def change_movie_rating():
    """Edit rating."""
    #Get values from form
    user_id = session["logged_in_user_id"]
    rating = request.form.get("rating")
    movie_id= request.form.get("movie_id")

    #Update rating in db
    mu.update_rating(user_id, movie_id, rating)

    return jsonify({'movie_id': movie_id, 'rating': rating})


@app.route("/register", methods=["GET"])
def register_form():
    genres = mu.Genre.query.all()
    return render_template("register_form.html", genres=genres)


@app.route("/register", methods=["POST"])
def register_process():
    """Add new user to db."""
    name = request.form.get("username")
    if name == '':
        name = None
    email = request.form.get("e-mail")
    password = request.form.get("password")
    dob = request.form.get("dob")
    if dob == '':
        dob = None
    genres = request.form.getlist('genre')

    info_user = [name, email, password, dob, genres]
    mu.add_user(info_user)

    return redirect("/")


@app.route("/login", methods=["GET"])
def show_login():
    """Show login form."""
    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login_form():
    #get user-provided email and password from request.form
    email = request.form.get("e-mail")
    password = request.form.get("password")

    if mu.is_user(email, password):
        return redirect('/')
    return redirect('/login')


@app.route("/logout")
def logout():
    session.pop('logged_in_user_id', None)
    flash('You were logged out')
    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    mu.connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    configure()
    app.run(host="0.0.0.0")
