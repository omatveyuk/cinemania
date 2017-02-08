""" Request helper """

import requests
import random


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
    print ('******************************************************')
    print url
    r_videos = requests.get(url)
    videos = r_videos.json()
    print videos
    print ('******************************************************')
    return videos

def get_random_movie_id(config):
    """ Return random movie id from themoviedb (popular only)
        url for request is read from global config
    """

    # request for total number of movies in themoviedb (popular only)
    url = config['url']['popular']
    r_movies = requests.get(url)
    movies = r_movies.json()
    total_results = movies["total_results"]
    random_id = random.randint(1, total_results)

    # 20 movies on page is requirement of API
    page = random_id / 20 + 1
    id_on_page = random_id % 20 - 1

    # optimization: if page > 1 make another request for the page 
    # given total number of movies and random id, find page and slot on the page
    if page > 1:
        url = "{0}&page={1}".format(url, page)
        r_movies = requests.get(url)
        movies = r_movies.json()

    movie_id = movies['results'][id_on_page]["id"]
    #movie_id = 33 #550
    return movie_id