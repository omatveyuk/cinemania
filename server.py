"""Flask server for Cinemania game"""

import os                   #to access my OS environment variables
from flask import Flask, session, request, redirect, render_template, flash, jsonify
import jinja2
from flask_debugtoolbar import DebugToolbarExtension
import requests
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

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
    #session["logged_in_user_id"] = 2
    #print('\n\n', session["logged_in_user_id"])
    #del session["logged_in_user_id"]
    #print('/n/n*********************************************************')

    #return render_template("homepage.html", user_id=session["logged_in_user_id"])
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

    usermovie_rating = None
    print "session[logged_in_user_id]: ", session["logged_in_user_id"]
    if "logged_in_user_id" in session:
        id_movie_db = db.session.query(mu.Movie).filter(mu.Movie.themoviedb_id == movie_id).first().movie_id
        user_movierating = db.session.query(mu.UserMovie).filter(mu.UserMovie.user_id == session["logged_in_user_id"],
                                                                  mu.UserMovie.movie_id == id_movie_db).first().rating

    print ("\n\n")
    print "user_id: ", session["logged_in_user_id"]
    print "movie_id: ", movie_id
    print "id_movie_db: ", id_movie_db
    print "rating: ", user_movierating
    print ("\n***************************************")

    return render_template("movie_details.html", movie=movie, user_movierating=user_movierating)


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Return page showing the user's movie list."""
    user = mu.User.query.get(user_id)
    movies = db.session.query(mu.UserMovie.movie_id,
                              mu.UserMovie.rating,
                              mu.UserMovie.seen,
                              mu.Movie.title,
                              mu.Movie.poster_url,
                              mu.Movie.themoviedb_id).join(mu.Movie).filter(mu.UserMovie.user_id == user_id).order_by(mu.Movie.title).all()
    genres = db.session.query(mu.UserGenre.genre_id,
                              mu.Genre.name).join(mu.Genre).filter(mu.UserGenre.user_id == user_id).all()

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

    #Change rating
    usermovie_rating = mu.UserMovie.query.filter(mu.UserMovie.user_id == user_id,
                                                 mu.UserMovie.movie_id == movie_id).first()
    if usermovie_rating:
        usermovie_rating.rating = rating
        flash("Rating updated.")
    db.session.commit()

    return jsonify({'movie_id': movie_id, 'rating': rating})


@app.route("/register", methods=["GET"])
def register_form():
    genres = mu.Genre.query.all()
    return render_template("register_form.html", genres=genres)


@app.route("/register", methods=["POST"])
def register_process():
    """Add new user to db."""
    name = request.form.get("username")
    email = request.form.get("e-mail")
    password = request.form.get("password")
    dob = request.form.get("dob")
    #CHECK ON FILL DOB!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    genres = request.form.getlist('genre')

    user = mu.User.query.filter_by(email=email).first()

    if user is None:
        user = mu.User(name=name, email=email, password=password, dob=dob)
        db.session.add(user)
        db.session.commit()

        user_id = mu.User.query.filter(mu.User.email == email,
                                       mu.User.password == password).first().user_id
        session["logged_in_user_id"] = user_id
        
        for genre in genres:
            genre_id = mu.Genre.query.filter_by(name=genre).first().genre_id
            usergenre_id = mu.UserGenre.query.filter(mu.UserGenre.user_id == user_id,
                                                     mu.UserGenre.genre_id == genre_id).first()
            if usergenre_id is None:
                usergenre = mu.UserGenre(user_id=user_id, genre_id=genre_id)
                db.session.add(usergenre)
                db.session.commit()

        flash("User sucsuccessfully added")

    else:
        flash("User already exists")

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

    try:
        user = mu.User.query.filter_by(email=email).one()
    except NoResultFound:
        flash("User is not found in our base")
        return redirect('/login')

    if password == user.password:
        session["logged_in_user_id"] = user.user_id
        print("\n\n")
        print session["logged_in_user_id"]
        print("\n***********************************************")
        flash("Login successful")
        return redirect('/')
    else:
        flash("Incorrect password")
        return redirect('/login')


@app.route("/logout")
def logout():
    session.pop('logged_in_user_id', None)
    flash('You were logged out')
    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    #app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    #DebugToolbarExtension(app)
    configure()
    app.run(host="0.0.0.0")
