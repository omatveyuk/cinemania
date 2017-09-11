"""Flask server for Cinemania game"""

import os                   #to access my OS environment variables
from flask import Flask, session, request, redirect, render_template, flash, jsonify
import jinja2
from flask_debugtoolbar import DebugToolbarExtension
from oauth import FacebookSignIn
import requests

import request_helper as rh
from model_movie import Movie, Person, Review
import model_movie
import model_user as mu

from rq import Queue
from rq.job import Job
from worker import conn


app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "shhhhhhhhhhhhhh"

config = {}
mu.connect_to_db(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

q=Queue(connection=conn)

config['api_key'] = {}
config['api_key']['themoviedb'] = '581f16d1449a5be365c74560b2f4c7f5'
config['url'] = {}
config['url']['popular'] = "https://api.themoviedb.org/3/movie/popular?api_key={0}".format(config['api_key']['themoviedb'])
config['url']['movie'] = "https://api.themoviedb.org/3/movie"
config['url']['poster'] = "https://image.tmdb.org/t/p/w500"
config['url']['youtube'] = "https://www.youtube.com/embed"
config['url']['profile'] = "https://image.tmdb.org/t/p/w500"
config['url']['wikipedia'] = "https://en.wikipedia.org/wiki"
config['url']['genres'] = "https://api.themoviedb.org/3/discover/movie?api_key={0}&with_genres=".format(config['api_key']['themoviedb'])
config['url']['person_base'] = "https://api.themoviedb.org/3/person/"
config['url']['person_credits'] = "/movie_credits?api_key={0}".format(config['api_key']['themoviedb'])

def foo():
    pass
@app.route('/random_movie')
def get_random_movie():
    """Return random movie from themoviedb API."""

    if "random_movie_id" not in session:
        # Get random movie id from themoviedb API
        movie_id = rh.get_random_movie_id(config)
    else:
        movie_id = session["random_movie_id"]

    # Create movie object which contain information about movie"
    movie = Movie(movie_id)
    movie.load(config)

    # if user login add movie to user's movie list
    if "logged_in_user_id" in session:
        mu.add_movie(movie, session["logged_in_user_id"])

    session["random_movie_id"] = movie_id
    return render_template("movie_details.html", movie=movie)


@app.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    """Return movie from themoviedb API by given movie id."""
    # Create movie object which contain information about movie
    movie = Movie(movie_id)
    movie.load(config)

    # Get user's rating for movie
    user_movierating = None
    if "logged_in_user_id" in session:
        user_id = session["logged_in_user_id"]
        user_movierating = mu.get_user_movie_rating(movie_id, user_id)

    return render_template("movie_details.html", movie=movie,
                            user_movierating=user_movierating)


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Return page showing the user's movie list."""
    if user_id == session.get("logged_in_user_id", 0):
        user = mu.get_user(user_id)
        movies = mu.get_user_movies(user_id)
        genres = mu.get_user_genres(user_id)

        return render_template("user_details.html",
                               user=user,
                               movies=movies,
                               genres=genres)
    flash("Invalid credentials.")
    return redirect('/')



@app.route("/change_rating.json", methods=['POST'])
def change_movie_rating():
    """Edit rating."""
    #Get values from form
    user_id = session["logged_in_user_id"]
    rating = request.form.get("rating")
    movie_id = request.form.get("movie_id")

    #Update rating in db
    mu.update_rating(user_id, movie_id, rating)

    return jsonify({'movie_id': movie_id, 'rating': rating})


@app.route("/cast_graph.json")
def get_cast_graph():
    """Collect information for drawing cast graph
       Return json:
        {"nodes": [{"name": actor's name,
                    "url": url actor's photo,
                    "wiki": wikipedia link}, ],
         "links": [{"source": actor1's index in "nodes",
                    "target": actor2's index in "nodes",
                    "movies": intersection of movies }, ]
        }
    """
    movie_id = request.args.get("movie_id")

    # Create Movie object which contains only movie, actors and directors
    movie = Movie(movie_id)
    movie.load_crew(config)

    # Create cast graph (5 actors and director)
    cast_graph = rh.create_cast_graph_json(config, movie)

    return jsonify(cast_graph)


@app.route("/register.json", methods=["GET"])
def register_form():
    """Send genres and user's preferences to registration form"""
    genres = mu.Genre.query.all()

    if "logged_in_user_id" in session:
        user_id = session["logged_in_user_id"]
        user = mu.get_user(user_id)
        user_genres = mu.get_user_genres(user_id)
        return jsonify(rh.create_info_user_json(genres, user, user_genres))
    return jsonify({"User": "not in session"})


@app.route("/register.json", methods=["POST"])
def register_process():
    """Add user's preferences and informatio about user to db."""
    user_id = session["logged_in_user_id"]

    name = request.form.get("name")
    if name == '':
        name = None

    dob = request.form.get("dob")
    if dob == '':
        dob = None

    genres = request.form.getlist("genres[]")

    info_user = [user_id, name, dob, genres]
    mu.add_info_user(info_user)

    return jsonify({"AddSettings": "true"})


@app.route("/signup.json", methods=["POST"])
def signup_form():
    """Sign up"""
    email = request.form.get("e-mail")
    password = request.form.get("password")
    provider = 'Cinemania'
    info_user = [email, password, provider]

    user_id = mu.add_user(info_user)
    if user_id:
        flash("User successfully added")
        session["logged_in_user_id"] = user_id
        return jsonify({"AddUser": "true"})

    flash("User with the e-mail already exists")
    return jsonify({"AddUser": "false"})


@app.route("/login.json", methods=["POST"])
def login_form():
    """Log in to Cinemania"""
    email = request.form.get("e-mail")
    password = request.form.get("password")

    user_id = mu.is_user(email, password)
    if user_id:
        session["logged_in_user_id"] = user_id
        flash("Login successful")
        return jsonify({"isUser": "true"})

    flash("Invalid user. Wrong e-mail, password or  maybe, you registered through Facebook?")
    return jsonify({"isUser": "false"})


@app.route("/logout")
def logout():
    """Logout"""
    session.pop('logged_in_user_id', None)
    flash('You were logged out')
    return redirect('/')


@app.route("/authorize")
def oauth_authorize():
    """Facebook Authorize"""
    if "logged_in_user_id" in session:
        return redirect('/')
    oauth = FacebookSignIn().authorize()
    return oauth


@app.route('/callback')
def oauth_callback():
    """Login with Facebook (if user doesn't exist add new user)"""
    if "logged_in_user_id" in session:
        return redirect('/')

    social_id, email = FacebookSignIn().callback()
    print "SERVER**************"
    print social_id, email
    if social_id is None:
        flash('Authentication failed.')
        return redirect('/')
    if email is None:
        flash('Sorry, your email is required to continue. Enable Cinemania app in Facebook to share email address.')
        return redirect('/')

    # User is already in the db
    user_id = mu.is_user(email, social_id)
    if user_id:
        session["logged_in_user_id"] = user_id
        flash("Login successful")
        return redirect('/')
    print "I'm here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    # Add user to the db
    info_user = [email, social_id, 'Facebook']
    user_id = mu.add_user(info_user)
    if user_id:
        session["logged_in_user_id"] = user_id
        flash("User successfully added")
        return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    mu.connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")
