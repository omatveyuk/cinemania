# Cinemania

http://cinemania.matveyuk.com

Cinemania is a web-application that helps movie lovers to discover movies. The application suggests a movie at random adding element of serendipity. Suggestions are driven by the user's genre preferences and popularity. 

When user lands on the movie page, besides the movie description, he sees the movie's ratings and reviews, the movie's trailer, links to the actors and directors Wikipedia pages, visual graph showing relationship between the main actors and the director and links to the Netflix and Hulu. Also, the user can rate individual movies, store and review the history of the movies discovered. To provide personalization, the app users are given an option to sign-in with e-mail and password or via OAuth.

Presentation [video](https://www.youtube.com/watch?v=JnnOQStrhmE) on youtube.

##Contents
* [Tech Stack](#technologies)
* [Features](#features)
* [Installing](#installing)
* [About Me](#aboutme)

## <a name="technologies"></a>Technologies
Backend: Python, Flask, PostgreSQL, SQLAlchemy, Redis<br/>
Frontend: JavaScript, jQuery, AJAX, Jinja2, Bootstrap, HTML5, CSS3, D3<br/>
APIs: Themoviedb, Facebook (OAuth)<br/>

## <a name="features"></a>Features

For personalized experience, users can log in to Cinemania through e-mail, password or via Facebook OAuth:

![homepage](http://res.cloudinary.com/oxanamatveyuk/image/upload/v1505973962/Screen_Shot_2017-09-20_at_10.54.18_PM_m8nvuk.png)

![login](http://res.cloudinary.com/oxanamatveyuk/image/upload/v1505973961/Screen_Shot_2017-09-20_at_10.54.52_PM_lpzlfi.png)

Using Redis for long-running task such as fetching a movie. Once a movie is chosen, the user is shown the movie detail page. The page is made of several sections: the movie header, the poster, links to the actors or directors Wikipedia pages, ratings and reviews, the overview and the trailer. Sentiment extraction algorithm determines positive or negative review:

![movie](http://res.cloudinary.com/oxanamatveyuk/image/upload/v1505973963/Screen_Shot_2017-09-20_at_11.02.29_PM_cbyrwo.png)

Users interested in knowing if the main actors and the director have appeared in other movies together, they can do so by looking at the relationship graph:

![graph](http://res.cloudinary.com/oxanamatveyuk/image/upload/v1505973962/Screen_Shot_2017-09-20_at_11.01.43_PM_rinyoj.png)

Finally, users can always re-visit movie's history in their profile and update ratings:

![profile](http://res.cloudinary.com/oxanamatveyuk/image/upload/v1505973965/Screen_Shot_2017-09-20_at_10.56.23_PM_kbgd5s.png)

## <a name="installing"></a>Installing

Clone this repo:
```
https://github.com/omatveyuk/cinemania.git
```

Create virtual environment on your laptop, inside a directory:
```
virtualenv env
source env/bin/activate
```

Install the requirements:
```
pip install -r requirements.txt
```

Setup Redis and make sure it starts
```
redis-server start
```

Get secret keys themoviedb API and Facebook API, and save it to secrets.sh:
```
export THEMOVIEDB_API_KEY="Your Key is Here"
export FACEBOOK_API_SECRET="Your Key is Here"
export FACEBOOK_ID="Your Key is Here"
```

Set up your database and seed initial data:
```
python model_user.py
python seed.py
```

For sentiment extraction from 
[https://archive.ics.uci.edu/ml/datasets/Sentiment+Labelled+Sentences#](https://archive.ics.uci.edu/ml/datasets/Sentiment+Labelled+Sentences#)
download training data set to training_data directory 

Start running your server:
```
source secrets.sh
python worker.py &
python server.py
```

Open up your browser and navigate to:
```
 'localhost:5000/'
```

Have a fun with Cinemania!️



## <a name="aboutme"></a>About Me
I live in the San Francisco Bay Area. I made this site because I wanted to connect my passion for coding and movies.
Visit me on [LinkedIn](https://www.linkedin.com/in/oxana-matveyuk).
