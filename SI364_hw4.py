## SI 364 - Fall 2017
## HW 4

## Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecure'
## TODO SI364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your Postgres database should be your uniqname, plus HW4, e.g. "jczettaHW4" or "maupandeHW4"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/msettonHW4"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use

## Set up Shell context so it's easy to use the shell to debug
def make_shell_context():
    return dict(app=app, db=db) ## TODO SI364: Add your models to this shell context function so you can use them in the shell
    # TODO SI364: Submit a screenshot of yourself using the shell to make a query for all the Tweets in the database.
    # Filling this in will make that easier!

# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))


#########
######### Everything above this line is important/useful setup, not problem-solving.
#########

##### Set up Models #####

## TODO SI364: Set up the following Model classes, with the respective fields (data types).

## The following relationships should exist between them:
# Tweet:User - Many:One
# Tweet:Hashtag - Many:Many

# - Tweet
## -- id (Primary Key)
## -- text (String, up to 285 chars)
## -- user_id (Integer, ID of user posted)

# - User
## -- id (Primary Key)
## -- twitter_username (String, up to 64 chars) (Unique=True)

# - Hashtag
## -- id (Primary Key)
## -- text (Unique=True)

# Association Table: Tweet_Hashtag
# -- tweet_id
# -- hashtag_id

## NOTE: You'll have to set up database relationship code in either the Tweet table or the Hashtag table so that the association table for that many-many relationship will work properly!

## set up the associations table between Tweet and Hashtag
collections = db.Table('collections',db.Column('tweet_id',db.Integer, db.ForeignKey('Tweet.id')),db.Column('hashtag_id',db.Integer, db.ForeignKey('Hashtag.id')))

class Tweet(db.Model):
    __tablename__ = "Tweet"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(285))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    twitter_username = db.Column(db.String(64),unique=True)

class Hashtag(db.Model):
    __tablename__ = 'Hashtag'
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(284),unique=True)


##### Set up Forms #####

# TODO SI364: Fill in the rest of this Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

## -- tweet text
## -- the twitter username who should post it
## -- a list of comma-separated hashtags it should have

class TweetForm(FlaskForm):
    text = StringField("What text would you like saved?", validators=[Required()])
    username = StringField("Who should post it?", validators=[Required()])
    hashtags = StringField("Insert a list of comma-separated values it should have", validators=[Required()])
    submit = SubmitField('Submit')


##### Helper functions

### For database additions / get_or_create functions

## TODO SI364: Write get_or_create functions for each model -- Tweets, Hashtags, and Users.
## -- Tweets should be identified by their text and user id,(e.g. if there's already a tweet with that text, by that user, then return it; otherwise, create it)
## -- Users should be identified by their username (e.g. if there's already a user with that username, return it, otherwise; create it)
## -- Hashtags should be identified by their text (e.g. if there's already a hashtag with that text, return it; otherwise, create it)

## HINT: Your get_or_create_tweet function should invoke your get_or_create_user function AND your get_or_create_hashtag function. You'll have seen an example similar to this in class!

## NOTE: If you choose to organize your code differently so it has the same effect of not encounting duplicates / identity errors, that is OK. But writing separate functions that may invoke one another is our primary suggestion.
def get_or_create_user(db_session,user_name):
    user = db_session.query(User).filter_by(twitter_username=user_name).first()
    if user:
        return user
    else:
        user = User(twitter_username=user_name)
        db_session.add(user)
        db_session.commit()
        return user

def get_or_create_hashtag(db_session,hashtag):
    hashtag = db_session.query(Hashtag).filter_by(text=hashtag).first()
    if hashtag:
        return hashtag
    else:
        hashtag = Hashtag(text=hashtag)
        db_session.add(hashtag)
        db_session.commit()
        return hashtag

def get_or_create_tweet(db_session,tweet_text,user_name):
    tweet = db_session.query(User).filter_by(twitter_username=user_name).fisrt()
    if tweet:
        return tweet
    tweet = db_session.query(Tweet).filter_by(text=tweet_text).first()
    if tweet:
        return tweet
    else:
        user = get_or_create_user(db_session, user_name)
        tweet = Tweet(text=tweet_text,user_id=user.id)
        db_session.add(tweet)
        db_session.commit()
        return tweet

##### Set up Controllers (view functions) #####

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Main route

@app.route('/', methods=['GET', 'POST'])
def index():
    ## TODO SI364: Fill in the index route as described.
    # A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
    ## HINT: Check out the index.html template to make sure you're sending it the data it needs.
    # The index route should:
    # - Show the Tweet form.
    # - If you enter a tweet with identical text and username to an existing tweet, it should redirect you to the list of all the tweets and a message that you've already saved a tweet like that.
    tweets = Tweet.query.all()
    num_tweets = len(tweets)
    form = TweetForm()
    if form.validate_on_submit():
        username = db.session.query(User).filter_by(username=form.twitter_username.data)
        if username:
            if db.session.query(Tweet).filter_by(text=form.tweet_text.data,user_id=username.id):
                flash("You've already saved a tweet with this username and text!")
        get_or_create_tweet(db.session,form.tweet_text.data,form.twitter_username.data)
        return redirect(url_for('see_all_tweets'))
    return render_template('index.html', form=form, num_tweets=num_tweets)
    ## ^ HINT: Invoke your get_or_create_tweet function
    ## ^ HINT: Check out the get_flashed_messages setup in the songs app you saw in class

    # This  main page should ALSO show links to pages in the app (see routes below) that:
    # -- allow you to see all of the tweets posted
    # -- see all of the twitter users you've saved tweets for, along with how many tweets they have in your database

@app.route('/all_tweets')
def see_all_tweets():
    # TODO SI364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
    ## HINT: Check out the all_songs and all_artists routes in the songs app you saw in class.
    tweet_list = []
    tweets = Tweet.query.all()
    for t in tweets:
        text = t.text
        name = User.query.filter_by(id=t.id).first()
        user_name = name.twitter_username
        small_list = [text, user_name]
        tweet_list.append(small_list)
    return render_template('all_tweets.html', all_tweets=tweet_list)


@app.route('/all_users')
def see_all_users():
    # TODO SI364: Fill in this view function so it can successfully render the template all_users.html, which is provided. (See instructions for more detail.)
    ## HINT: Check out the all_songs and all_artists routes in the songs app you saw in class.
    user_list = []
    users = User.query.all()
    for u in users:
        user_id = u.id
        user_tweets = db.session.query(Tweet).filter_by(user_id=user_id)
        num = len(user_tweets)
        user_list.append([u.twitter_username, num])
    return render_template('all_users.html', usernames=user_list)


if __name__ == '__main__':
    db.create_all()
    manager.run() # Run with this: python main_app.py runserver
    # Also provides more tools for debugging
