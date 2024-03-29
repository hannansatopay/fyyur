#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', backref='Venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate --> DONE


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', backref='Artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate --> DONE


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

db.create_all()

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

#----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  venue_info = {}
  venue_obj = []
  venue_details = {}
  dif_cities = db.session.query(Venue.city).group_by(Venue.city).all()
  for dif_city in dif_cities:
    venue_info["city"] = dif_city[0]
    city_state = db.session.query(Venue.state).filter_by(city=dif_city).first()
    venue_info["state"] = city_state[0]
    city_venues = db.session.query(Venue.id,Venue.name).filter_by(city=dif_city).all()
    for city_venue in city_venues:
      venue_details["id"] = city_venue[0]
      venue_details["name"] = city_venue[1]
      today = datetime.now()
      city_filter = city_venue[0]
      num_upcoming_shows = db.session.query(func.count(Show.id)).filter(Show.start_time>today,Show.venue_id==city_filter).group_by(Show.venue_id).first()
      if num_upcoming_shows:
        venue_details["num_upcoming_shows"] = num_upcoming_shows[0]
        print(venue_details)
      else:
        venue_details["num_upcoming_shows"] = 0
      venue_obj.append(venue_details)
      venue_info["venues"] = venue_obj
  data.append(venue_info)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  data = []
  venue_info = {}
  venue_term = request.form.get('search_term')
  search = "%{}%".format(venue_term)
  venue_count = db.session.query(func.count(Venue.id)).filter(Venue.name.ilike(search)).first()
  response["count"] = venue_count[0]
  venue_ids = db.session.query(Venue.id).filter(Venue.name.ilike(search)).all()
  for venue_id in venue_ids:
    num_upcoming_shows = db.session.query(func.count(Show.id)).filter(Show.venue_id==venue_id).first()
    venue_data_name = db.session.query(Venue.name).filter(Venue.id==venue_id[0]).first()
    venue_info["id"] = venue_id[0]
    venue_info["name"]= venue_data_name[0]
    venue_info["num_upcoming_shows"]= num_upcoming_shows[0]
    data.append(venue_info)
    response["data"]=data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows = []
  upcoming_shows = []
  data = {}
  venue_info = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state,Venue.address, Venue.genres, Venue.phone, Venue.image_link,Venue.seeking_description, Venue.facebook_link, Venue.seeking_talent, Venue.website).filter(Venue.id == venue_id).first()
  data["id"] = venue_info[0]
  data["name"] = venue_info[1]
  data["city"] = venue_info[2]
  data["state"] = venue_info[3]
  data["address"] = venue_info[4]
  data["genre"] = venue_info[5]
  data["phone"] = venue_info[6]
  data["image_link"] = venue_info[7]
  data["seeking_description"] = venue_info[8]
  data["facebook_link"] = venue_info[9]
  data["seeking_talent"] = venue_info[10]
  data["website"] = venue_info[11]

  now = datetime.now()

  # past shows
  past_shows_count = db.session.query(func.count(Show.id)).filter(Show.venue_id == venue_id, Show.start_time < now).first()
  data["past_shows_count"] = past_shows_count[0]
  past_shows_data = db.session.query(Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Artist).filter(Show.venue_id == venue_id, Show.start_time < now).all()
  for past_show_data in past_shows_data:
    p_s_d = {}
    p_s_d["artist_id"] = past_show_data[0]
    p_s_d["artist_name"] = past_show_data[1]
    p_s_d["artist_image_link"] = past_show_data[2]
    new_date_format = str(past_show_data[3])
    new_date = format_datetime(new_date_format, format='medium')
    p_s_d["start_time"] = new_date
    past_shows.append(p_s_d)
  data["past_shows"] = past_shows

  # future shows
  upcoming_shows_count = db.session.query(func.count(Show.id)).filter(Show.venue_id == venue_id, Show.start_time > now).first()
  data["upcoming_shows_count"] = upcoming_shows_count[0]
  upcoming_shows_data = db.session.query(Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Artist).filter(Show.venue_id == venue_id, Show.start_time > now).all()
  for upcoming_show_data in upcoming_shows_data:
    u_s_d = {}
    u_s_d["artist_id"] = upcoming_show_data[0]
    u_s_d["artist_name"] = upcoming_show_data[1]
    u_s_d["artist_image_link"] = upcoming_show_data[2]
    new_date_format = str(upcoming_show_data[3])
    new_date = format_datetime(new_date_format, format='medium')
    u_s_d["start_time"] = new_date
    upcoming_shows.append(u_s_d)
  data["upcoming_shows"] = upcoming_shows

  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  try:
    venue = Venue(name=name, city=city, state=state, phone=phone,address=address, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    print(venue)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ID ' + venue_id + ' was successfully deleted!')
  except:
    flash('An error occurred. Venue ID '+venue_id+' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  data = []
  artist_info = {}
  artist_term = request.form.get('search_term')
  search = "%{}%".format(artist_term)
  artist_count = db.session.query(func.count(Artist.id)).filter(Artist.name.ilike(search)).first()
  response["count"] = artist_count[0]
  artist_ids = db.session.query(Artist.id).filter(Artist.name.ilike(search)).all()
  for artist_id in artist_ids:
    num_upcoming_shows = db.session.query(func.count(Show.id)).filter(Show.artist_id == artist_id).first()
    artist_data_name = db.session.query(Artist.name).filter(Artist.id == artist_id[0]).first()
    artist_info["id"] = artist_id[0]
    artist_info["name"] = artist_data_name[0]
    artist_info["num_upcoming_shows"] = num_upcoming_shows[0]
    data.append(artist_info)
    response["data"] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  past_shows = []
  upcoming_shows = []
  data ={}
  artist_info=db.session.query(Artist.id,Artist.name,Artist.city,Artist.state,Artist.genres,Artist.phone,Artist.image_link,Artist.seeking_description,Artist.facebook_link,Artist.seeking_venue,Artist.website).filter(Artist.id==artist_id).first()
  data["id"] = artist_info[0]
  data["name"] = artist_info[1]
  data["city"] = artist_info[2]
  data["state"] = artist_info[3]
  data["genre"] = artist_info[4]
  data["phone"] = artist_info[5]
  data["image_link"] = artist_info[6]
  data["seeking_description"] = artist_info[7]
  data["facebook_link"] = artist_info[8]
  data["seeking_venue"] = artist_info[9]
  data["website"] = artist_info[10]

  now = datetime.now()

  # past shows
  past_shows_count = db.session.query(func.count(Show.id)).filter(Show.artist_id==artist_id, Show.start_time< now).first()
  data["past_shows_count"] = past_shows_count[0]
  past_shows_data = db.session.query(Show.venue_id, Venue.name, Venue.image_link, Show.start_time).join(Venue).filter(Show.artist_id == artist_id, Show.start_time < now).all()
  for past_show_data in past_shows_data:
    p_s_d = {}
    p_s_d["venue_id"] = past_show_data[0]
    p_s_d["venue_name"] = past_show_data[1]
    p_s_d["venue_image_link"] = past_show_data[2]
    new_date_format = str(past_show_data[3])
    new_date = format_datetime(new_date_format, format='medium')
    p_s_d["start_time"] = new_date
    past_shows.append(p_s_d)
  data["past_shows"] = past_shows

  # future shows
  upcoming_shows_count = db.session.query(func.count(Show.id)).filter(Show.artist_id==artist_id, Show.start_time> now).first()
  data["upcoming_shows_count"] = upcoming_shows_count[0]
  upcoming_shows_data = db.session.query(Show.venue_id, Venue.name, Venue.image_link, Show.start_time).join(Venue).filter(Show.artist_id == artist_id, Show.start_time > now).all()
  for upcoming_show_data in upcoming_shows_data:
    u_s_d = {}
    u_s_d["venue_id"] = upcoming_show_data[0]
    u_s_d["venue_name"] = upcoming_show_data[1]
    u_s_d["venue_image_link"] = upcoming_show_data[2]
    new_date_format = str(upcoming_show_data[3])
    new_date = format_datetime(new_date_format, format='medium')
    u_s_d["start_time"] = new_date
    upcoming_shows.append(u_s_d)
  data["upcoming_shows"] = upcoming_shows

  return render_template('pages/show_artist.html', artist=data)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    db.session.commit()
    flash('Artist ' + request.form.get('name') + ' was successfully updated!')
  except:
    flash('An error occurred. Artist ' +request.form.get('name') + ' could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.get('genres')
    venue.facebook_link = request.form.get('facebook_link')
    db.session.commit()
    flash('Venue ' + request.form.get('name') + ' was successfully updated!')
  except:
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  name =  request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone =  request.form.get('phone')
  genres =  request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  try:
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  results = db.session.query(Show.venue_id,Venue.name,Show.artist_id,Artist.name,Artist.image_link,Show.start_time).all()
  for result in results:
    show_info = {}
    show_info["venue_id"] = result[0]
    show_info["venue_name"] = result[1]
    show_info["artist_id"] = result[2]
    show_info["artist_name"] = result[3]
    show_info["artist_image_link"]= result[4]
    new_date_format = str(result[5])
    new_date = format_datetime(new_date_format, format='medium')
    show_info["start_time"]= new_date
    data.append(show_info)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred, and show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
