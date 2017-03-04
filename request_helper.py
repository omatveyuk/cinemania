""" Request helper """

import requests
import random
from flask import session
import model_user as mu
from model_movie import PersonNode


def get_movie_by_id(config, movie_id):
    """ Get information about movie from request to themoviedb by movie id """
    url = "{0}/{1}?api_key={2}".format(config['url']['movie'],
                                       movie_id,
                                       config['api_key']['themoviedb'])
    r_movies = requests.get(url)
    movies = r_movies.json()
    return movies


def get_crew_by_id(config, movie_id):
    """ Get information about actors, director, writer from request to themoviedb by movie id"""
    url = "{0}/{1}/credits?api_key={2}".format(config['url']['movie'],
                                        movie_id,
                                        config['api_key']['themoviedb'])
    r_crew = requests.get(url)
    crew = r_crew.json()
    return crew


def get_reviews_by_id(config, movie_id):
    """ Get review for movie from request to themoviedb by movie id"""
    url = "{0}/{1}/reviews?api_key={2}".format(config['url']['movie'],
                                        movie_id,
                                        config['api_key']['themoviedb'])
    r_reviews = requests.get(url)
    reviews = r_reviews.json()
    return reviews


def get_videos_by_id(config, movie_id):
    """ Get video of movie from request to themoviedb by movie id"""
    url = "{0}/{1}/videos?api_key={2}".format(config['url']['movie'],
                                        movie_id,
                                        config['api_key']['themoviedb'])
    r_videos = requests.get(url)
    videos = r_videos.json()
    return videos


def get_random_movie_id(config):
    """ Return random movie id from themoviedb
        url for requests is read from global config
    """
    if "logged_in_user_id" in session:
        movie_id = get_random_movie_id_session(config)
        return movie_id

    url = config['url']['popular']
    return get_random_movie_id_based_url(url)


def get_random_movie_id_session(config):
    """Return movie id which randomly choosen from themoviedb
       (popular movies and movies based on genre's preference of user
        url for requests is read from global config
        If all movies from requests are already in the user's movie list
        make another round of new requests
    """
    user_id = session["logged_in_user_id"]

    while True:
        # get random movie id from popular movie request
        url = config['url']['popular']
        movies_id = [get_random_movie_id_based_url(url)]

        # get random movie ids from all genres requests based on user's preference
        url = config['url']['genres']
        movies_id.extend(get_random_movie_id_genres(url))

        # get random movie id
        while len(movies_id) > 0:
            random_index = random.randint(0, len(movies_id)-1)
            if not mu.is_movie_in_user_movies_list(user_id, movies_id[random_index]):
                return movies_id[random_index]
        

def get_random_movie_id_genres(url_genres):
    """ Return list of random movie ids based on genres which user prefers."""
    user_id = session["logged_in_user_id"]
    genres = mu.get_user_genres(user_id)
    movies_id = []

    for genre in genres:
        url = "{0}{1}".format(url_genres, genre[2])
        movies_id.append(get_random_movie_id_based_url(url))

    return movies_id    


def get_random_movie_id_based_url(url):
    """ Return random movie id from themoviedb based on url for request
        Response does not contain full information about movie
    """
    # request for total number of movies in themoviedb (url)
    r_movies = requests.get(url)
    movies = r_movies.json()

    total_results = movies["total_results"]
    # disadventage of API: gives only 1000 pages for request
    if total_results > 20000:
        total_results = 20000
    random_index = random.randint(1, total_results)

    # 20 movies on page is requirement of API
    page = random_index / 20 + 1
    id_on_page = random_index % 20 - 1

    # optimization: if page > 1 make another request for the page 
    # given total number of movies and random id, find page and slot on the page
    if page > 1:
        url = "{0}&page={1}".format(url, page)
        r_movies = requests.get(url)
        movies = r_movies.json()

    movie_id = movies['results'][id_on_page]["id"]
    #movie_id = 155 #238 #gold father #155 #nolan   33 550

    return movie_id


def get_twenty_posters(config, page, posters):
    """Return 20 movie posters from responde page of popular movie
       and total number of pages
    """
    url = config['url']['popular']
    if page > 1:
        url = "{0}&page={1}".format(url, page)

    r_movies = requests.get(url)
    movies = r_movies.json()
    for item in movies['results']:
        if item['poster_path']:
            posters['{0}{1}'.format(config['url']['poster'],
                                    item['poster_path'])] = item['original_title']
    return [posters, movies['total_pages']]


def get_posters_for_animation(config):
    """ Return 40 random movie posters from themoviedb (popular only)
        for animation on homepage
        url for request is read from global config
    """
    posters = {}
    # request for first 20 posters and number of total pages of movies
    # in themoviedb (popular only).
    # 20 movies on page is requirement of API
    posters, total_pages = get_twenty_posters(config, 1, posters)

    # more 20 posters
    # disadventage of API: gives only 1000 pages for request
    if total_pages > 1000:
        total_pages = 1000
    random_page = random.randint(2, total_pages)
    posters = get_twenty_posters(config, random_page, posters)[0]

    return posters


def create_person_node(config, person, movie_id):
    """Return person node for cast graph
        person: Person's object 
        movie_id: movie on current page"""
    url = config['url']['person_base']+str(person.id)+config['url']['person_credits']
    r_movies = requests.get(url)
    movies = {}

    # list movies excludes movie of current page
    for movie in r_movies.json()["cast"]:
        if int(movie["id"]) != int(movie_id):
            movies[movie["id"]] = movie["title"]
    for movie in r_movies.json()["crew"]:
        if int(movie["id"]) != int(movie_id):
            movies[movie["id"]] = movie["title"]

    return PersonNode(person, movies)


def create_nodes_for_graph(config, movie):
    """Return list of person nodes for actors and directors
        movie is Movie's object"""
    number_actors = 0
    movie_credits = []
    id_persons = []
    # Actors (total max 5)
    for person in movie.actors:
        number_actors += 1
        person_node = create_person_node(config, person, movie.id)
        movie_credits.append(person_node)
        id_persons.append(person.id)
        if number_actors == 5:
            break

    # First Director
    if movie.directors:
        # check duplicates of person if director is actor in own movie
        if movie.directors[0].id not in id_persons:
            person_node = create_person_node(config, movie.directors[0], movie.id)
            movie_credits.append(person_node)

    return movie_credits


def create_cast_graph_json(config, movie):
    """Return dictionary cast connections in over movie
        {"nodes": [{"name": actor's name,
                    "url": url actor's photo,
                    "wiki": wikipedia link}, ],
         "links": [{"source": actor1's index in "nodes",
                    "target": actor2's index in "nodes", 
                    "movies": intersection of movies }, ]
        }
       Input: movie is Movie's object
    """
    cast_graph = {"nodes": [], "links": []}
    #Create person nodes for less or 5 actors and first director
    person_nodes = create_nodes_for_graph(config, movie)

    # Nodes
    for person_node in person_nodes:
        node = {"name": person_node.person.name,
                "url": person_node.person.profile_url,
                "wiki": person_node.person.wikipedia_url
               }
        cast_graph["nodes"].append(node)       

    # Add links to the graph between two persons
    for i in xrange(len(person_nodes)-1):
        for j in xrange(i+1, len(person_nodes)):
            # find movie ids where two persons worked together
            list_movies_person1 = set(person_nodes[i].movies.keys())
            list_movies_person2 = set(person_nodes[j].movies.keys())
            intersection = list_movies_person1 & list_movies_person2
            if intersection:
                intersection_movies = []
                for movie_id in intersection:
                    intersection_movies.append(person_nodes[i].movies[movie_id])

                link = {"source": i,
                        "target": j,
                        "movies":intersection_movies}
                cast_graph["links"].append(link)

    return cast_graph   


def create_info_user_json(genres, user, user_genres):
    """Create dictionary (name, dob, user's genres) for json""" 
    info_user_json = {"genres": [],
                      "name": '',
                      "dob": ''}

    if user.name == None:
        info_user_json["name"] = ''
    else:
        info_user_json["name"] = user.name
    if user.dob == None:
        info_user_json["dob"] = ''
    else:
        info_user_json["dob"] = user.dob.strftime("%Y-%m-%d")

    user_id_genres = set([genre[0] for genre in user_genres])
    for genre in genres:
        if genre.genre_id in user_id_genres:
            info_user_json["genres"].append({"id": genre.genre_id,
                                             "name": genre.name,
                                             "checked": "checked"})
        else:
            info_user_json["genres"].append({"id": genre.genre_id,
                                             "name": genre.name,
                                             "checked": ""})

    return info_user_json




























