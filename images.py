import urllib
import requests
import random
from PIL import Image
import sys
# import os.path
import os
import json
import shutil

config={}

config['api_key'] = {}
config['api_key']['themoviedb'] = '581f16d1449a5be365c74560b2f4c7f5'
config['url'] = {}
config['url']['popular'] = "https://api.themoviedb.org/3/movie/popular?api_key={0}".format(config['api_key']['themoviedb'])
config['url']['movie'] = "https://api.themoviedb.org/3/movie"
config['url']['poster'] = "https://image.tmdb.org/t/p/w500"
config['url']['youtube'] = "https://www.youtube.com/embed"
config['url']['profile'] = "https://image.tmdb.org/t/p/w500"
config['url']['wikipedia'] = "https://en.wikipedia.org/wiki"
config['url']['person_base'] = "https://api.themoviedb.org/3/person/"
config['url']['person_credits'] = "/movie_credits?api_key={0}".format(config['api_key']['themoviedb'])
config['url']['genres'] = "https://api.themoviedb.org/3/discover/movie?api_key={0}&with_genres=".format(config['api_key']['themoviedb'])
config['url']['person_base'] = "https://api.themoviedb.org/3/person/"

def file_exists(path):
    return os.path.exists(path)

def resize(source_path, destination_path):
    basewidth = 500
    image = Image.open(source_path)
    wpercent = (basewidth / float(image.size[0]))
    print source_path, destination_path
    hsize = int((float(image.size[1]) * float(wpercent)))
    img = image.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(destination_path, "JPEG")
    # image.save(destination_path, "JPEG")

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


def save_posters_for_animation(config):
    """ Save 40 random movie posters in static/posters from themoviedb (popular only)
        for animation on homepage 
        url for request is read from global config
    """

    root = ""                   # localhost:5000
    # root = "/var/www/cinemania/"  #for deployment
    temp_path = root + "static/temp/"
    posters_file = root + "static/posters/posters.json"
    posters_path = root + "static/posters/"
    # web_posters_path = "http://cinemania.matveyuk.com/static/posters/"        #for deployment
    web_posters_path = "static/posters/"            # localhost:5000


    # create directory
    if file_exists(temp_path):
        shutil.rmtree(temp_path)
    os.mkdir(temp_path)

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

    new_posters = {}
    
    for poster in posters:
        filename = poster.split("?")[0].split("/")[-1]
        movie_name = posters[poster]
        source = temp_path + filename
        destination = temp_path + "500_" + filename
        if not file_exists(destination):
            print "Downloading ", source
            urllib.urlretrieve(poster, source)
            resize(temp_path + filename, destination)
        os.remove(source)
        new_posters[web_posters_path + "500_" + filename] = movie_name

    # delete current posters directory
    if file_exists(posters_path):
        shutil.rmtree(posters_path)
    #rename temp to posters directory 
    os.rename(temp_path, posters_path)

    with open(posters_file, 'w') as f:
        json.dump(new_posters, f)
        # json.dump(posters, f)


save_posters_for_animation(config)



