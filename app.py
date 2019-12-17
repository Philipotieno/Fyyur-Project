#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
import os
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for, jsonify)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = 'postgres://mitch:mufasa2019@localhost:5432/fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    
    venues = db.relationship('Venue', secondary='shows', back_populates='artists')
    shows = db.relationship('Show')
    
    def to_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres.split(','), # convert string to list
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
      }
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    web_site = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
      
    artists = db.relationship('Artist', secondary='shows', back_populates='venues')
    shows = db.relationship('Show')
  
    def to_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'genres': self.genres.split(','), # convert string to list
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'web_site': self.web_site,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
    }
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
  
class Show(db.Model):
  __tablename__ = 'shows'
  
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  venue = db.relationship('Venue')
  artist = db.relationship('Artist')
  
  def show_artist(self):
    return {
      'artist_id': self.artist_id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') # convert datetime to string
    }

  def show_venue(self):
    return {
      'venue_id': self.venue_id,
      'venue_name': self.venue.name,
      'venue_image_link': self.venue.image_link,
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')  # convert datetime to string
    }
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')
pass

####### Artists
# Create Artist

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    artist.genres = ','.join( tmp_genres )
    artist.facebook_link = request.form['facebook_link']
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print( sys.exc_info() )
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

# Get Artist
@app.route('/artists')
def artists():
  return render_template('pages/artists.html',
                         artists=Artist.query.all())
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given venue_id
  artist = Artist.query.get(artist_id)
  
  past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows ))
  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), artist.shows))
  
  past_shows = list(map(lambda x: x.show_venue(), past_shows))
  upcoming_shows = list( map( lambda x: x.show_venue(), upcoming_shows))
  
  data = artist.to_dict()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

# Update Artist
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print( sys.exc_info() )
  finally:
    db.session.close()
    if error:
      return redirect(url_for('server_error'))
    else:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  
  response = {}
  response['count'] = len(search_results)
  response['data'] = search_results

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

########  Venues
#  Create Venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed!')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues')
def venues():
  venues = Venue.query.order_by(Venue.state, Venue.city).all()

  data = []
  prev_city = None
  prev_state = None
  for venue in venues:
    venue_data = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len( list( filter( lambda x: x.start_time > datetime.today(), venue.shows ) ) )
    }
    if venue.city == prev_city and venue.state == prev_state:
      tmp['venues'].append(venue_data)
    else:
      if prev_city is not None:
        data.append(tmp)
      tmp = {}
      tmp['city'] = venue.city
      tmp['state'] = venue.state
      tmp['venues'] = [venue_data]
    prev_city = venue.city
    prev_state = venue.state

  data.append(tmp)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term' )
  venues = Venue.query.filter( Venue.name.ilike( '%{}%'.format( search_term) ) ).all()

  data = []
  for venue in venues:
    tmp = {}
    tmp['id'] = venue.id
    tmp['name'] = venue.name
    tmp['num_upcoming_shows'] = len( venue.shows )
    data.append(tmp)

  response = {}
  response['count'] = len( data )
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  past_shows = list( filter( lambda x: x.start_time < datetime.today(), venue.shows ) )
  upcoming_shows = list( filter( lambda x: x.start_time >= datetime.today(), venue.shows ) )

  past_shows = list( map( lambda x: x.show_artist(), past_shows) )
  upcoming_shows = list( map( lambda x: x.show_artist(), upcoming_shows) )

  data = venue.to_dict()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/<venue_id>', methods=['DELETE'])
##This endpoint can be tested on postman http://0.0.0.0:8080/venues/venue_id
def delete_venue(venue_id):
  success = True
  status = 200
  
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except :
    success = False
    status = 500
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if success:
      flash('Venue had been deleted')
    else:
      flash('Venue could not be deleted')
    return jsonify({'success': success}), status

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id).to_dict()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  error = False
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres ) # convert list to string
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print( sys.exc_info() )
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Shows
@app.route('/shows')
def shows():
  shows = Show.query.all()

  data = []
  for show in shows:
    data.append( {
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print( sys.exc_info() )
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Requested show could not be listed.')
    else:
      flash('Requested show was successfully listed')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
