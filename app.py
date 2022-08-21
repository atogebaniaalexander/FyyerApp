#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import date
import imp
import json
from operator import le
import sys
from unicodedata import name
from urllib import response
from xmlrpc.client import DateTime
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import func
from forms import *
from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  try:
    data = []
    results = {}
    query_outcome = db.session.query(
      Venue.id,
      Venue.name,
      Venue.city,
      Venue.state,
      func.accountFor(Venue.id)).outerjoin(Show, Venue.id==Show.venue_id).group_by(Venue.id,Venue.name,Venue.city,Venue.state).all() 
    for venue_data in results:
      (city, state, name, id, show_total) = venue_data
      location = (city,state)
      if location not in results:
        results[location] = []
      results[location].append(
        {
          "id":id,
          "name":name,
          "num_upcoming_shows":show_total
        })
      for key, value in results.items():
            data.append(
                {"city": key[0],
                 "state": key[1],
                 "venues": [{"id": show['id'], "name": show['name'], "num_upcoming_shows": show['num_upcoming_shows']} for show in value]
                 })
      
    
  except Exception:
    flash('An error occured venues was not successfully listed!')
    print(sys.exc_info())

  return render_template('pages/venues.html', areas=data)

  
  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    search_key = request.form.get('search_term', '')
    response = { }
    data = []
    venues = Venue.query.filter(
        Venue.name.ilike(f'%{search_key}%')
    ).all()
    count = len(venues)
    if count > 0:
      for venue in venues:
        data.append({
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows":len(venue.shows)
        })
      response = {
        "count":count,
        "data":data
      }
  except Exception:
    flash(
            f'An error occured, could not search with {search_key} was not successfully!')
    print(sys.exc_info())


  return render_template('pages/search_venues.html', results=response, search_term=search_key)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  try:
    data = {}
    venue = Venue.query.get(venue_id)

    data = {
      "id":venue.id,
      "name":venue.name,
      "city":venue.city,
      "state":venue.state,
      "address":venue.address,
      "phone":venue.phone,
      "image_link":venue.image_link,
      "facebook_link":venue.facebook_link,
      "genres":venue.genres.split(','),
      "venue_website":venue.venue_website,
      "searching_talent":venue. searching_talent,
      "talent_description":venue.  talent_description
    }
    upcoming_shows = []
    past_shows = []
    all_shows = db.session.query(
      Artist,Show
    ).join(Show).filter(Show.venue_id == venue_id).all()

    for artist, show in all_shows:
      if datetime.date(show.show_start_time) >= DateTime.today():
        upcoming_shows.append({
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.show_start_time
        })
      else:
        past_shows.append({
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.show_start_time
        })

    data['upcoming_shows']=upcoming_shows
    data['upcoming_shows_total']=len(data['upcoming_shows'])

    data['past_shows']=past_shows
    data['past_shows_total']=len(data['past_shows'])

  except Exception:
    flash(f'Details for venue: {venue_id} was not successfully fetched!')
    print(sys.exc_info())
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue~
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm()

    if form.validate_on_submit():
        print("Form Valid")
    else:
        return render_template('forms/new_venue.html', form=form)
    venue_exists = Venue.query.filter(
      Venue.name.ilike(f'%{form.name.data}%')
    ).all()
    if len(venue_exists) > 0:
      form.name.errors.append(
        'Venue name' + request.form['name'] + 'already exists!'
      )
      return render_template('forms/new_venue.html',form=form)

    genres = ",".join(form.genres.data)
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=genres,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data, 
        is_talent_seeking=form.seeking_talent.data,
        talent_seeking_description=form.seeking_description.data
        )
    db.session.add(venue)
    db.session.commit()
    
    flash('Venue ' + request.form['name'] + ' was successfully created!')
  except Exception:
    db.session.rollback()
    flash('An error occured Venue ' + request.form['name'] + ' was not successfully created!')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash(f'Venue: {venue_id} was successfully deleted!')
  except BaseException:
      flash(f'Venue: {venue_id} was not successfully deleted!')
      print(sys.exc_info())
      db.session.rollback()
  finally:
        db.session.close()
  return jsonify({'Success:True'})

@app.route('/venues/<venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    try:
      venue = Venue.query.get(venue_id)

      form.name.data = venue.name
      form.genres.data = venue.genres.split(',')
      form.address.data = venue.address
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.website_link.data = venue.website_link
      form.facebook_link.data = venue.facebook_link
      form.seeking_talent.data = venue.is_talent_seeking
      form.seeking_description.data = venue.talent_seeking_description
      form.image_link.data = venue.image_link
    except ~Exception:
        flash(f'Venue: {venue_id} was not successfully loaded!')
        print(sys.exc_info())
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
      venue = Venue.query.get(venue_id)
      form = VenueForm()

      if form.validate_on_submit():
        print("Form Valid")
      else:
          return render_template(
                'forms/edit_venue.html', form=form, venue=venue)

      existing_venue = Venue.query.filter(
            Venue.name.ilike(f'%{form.name.data}%')).all()
      if len(existing_venue) > 0 and form.name.data.lower() != venue.name.lower():
            form.name.errors.append(
                'Venue name ' +
                request.form['name'] +
                ' already exists!')
            return render_template(
                'forms/edit_venue.html', form=form, venue=venue)

      genres = ",".join(form.genres.data)

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.genres = genres
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      venue.is_talent_seeking = form.seeking_talent.data
      venue.talent_seeking_description = form.seeking_description.data

      db.session.commit()
      flash(f'Venue: {venue_id} was successfully edited!')
    except BaseException:
      flash(f'Venue: {venue_id} was not successfully edited!')
      print(sys.exc_info())
      db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))




#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    data = []
    artists = Artist.query.all()
    data = [{
              "id": artists.id,
              "name": artists.name}]
    for item in artists:
      if len(data) > 0:
        flash('Artists successfully listed!')
  except Exception:
    flash('Artists was not successfully listed!')
    print(sys.exc_info())

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
 try:
   search_key = request.form.get('search', '')
   response = {}
   data = []
   artists = Artist.query.filter(
     Artist.name.ilike(f'%{search_key}%')).all()
   count = len(artists)

   if count > 0:
     for artist in artists:
       data.append({
         "id":artist.id,
         "name":artist.name,
         "nums_upcoming_shows": len(artist.shows)
       })
     response = {
       "count": count,
       "data": data
     }
 except Exception:
   flash(
        f'An error occured, could not search with {search_key} was not successfully!')
   print(sys.exc_info())
 return render_template('pages/search_artists.html', results=response, search_term=search_key)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  try:
    data = {}
    artist = Artist.query.get(artist_id)
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "artist_website": artist.artist_website,
      "facebook_link": artist.facebook_link,
      "searching_venue ": artist.searching_venue,
      "venue_description": artist.venue_description,
      "image_link": artist.image_link,
    }
    upcoming_shows = []
    past_shows = []
    all_shows = db.session.query(
            Venue, Show).join(Show).filter(
            Show.artist_id == artist_id).all()
    for venue, show in all_shows:
      if datetime.date(show.start_time) >= date.today():
          upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.show_start_time
      })
      else:
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.show_start_time
        })


    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)

    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)

  except Exception:
     flash(f'Details for venue: {artist_id} was not successfully fetched!')
     print(sys.exc_info())

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  try:
      artist = Artist.query.get(artist_id)
      form.name.data = artist.name
      form.city.data = artist.city
      form.state.data = artist.state
      form.phone.data = artist.phone
      form.genres.data = artist.genres.split(',')
      form.image_link.data = artist.image_link
      form.facebook_link.data = artist.facebook_link
      form.website_link.data = artist.artist_website
      form.seeking_venue.data = artist.searching_venue
      form.seeking_description.data = artist.venue_description
  except Exception:
      flash(f'Artist: {artist_id} was not successfully loaded!')
      print(sys.exc_info())

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    if form.validate_on_submit():
        print("Form Valid")
    else:
        return render_template(
            'forms/edit_artist.html', form=form, artist=Artist)
    try:
      artist = Artist.query.get(artist_id)
      artist_exists = Artist.query.filter(
        Artist.name.ilike(f'%{form.name.data}%')).all()
      if len(artist_exists) > 0 and form.name.data.lower() !=artist.name.lower():
        print(form.name.data.lower(), artist.name.lower())
        form.name.errors.append(
                'Artist name ' +
                request.form['name'] +
                ' already exists!')
        return render_template(
                'forms/edit_artist.html', form=form, artist=artist)
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = ",".join(form.genres.data)
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.is_venue_seeking = form.seeking_venue.data
      artist.venue_seeking_description = form.seeking_description.data  

      db.session.commit()
      flash(f'Artist: {artist_id} was successfully edited!')
    except Exception:
      flash(f'Artist: {artist_id} was not successfully edited!')
      print(sys.exc_info())
      db.session.rollback()
    finally:
      db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
      form = ArtistForm()
      if form.validate_in_submit():
         print("Form Valid")
      else:
            return render_template('forms/new_artist.html', form=form)
      artist_exists = Artist.query.filter(Artist.name.ilike(f'%{form.name.data}%')).all()
      if len(artist_exists) > 0:
        form.name.errors.append(
          'Artist name' +
           request.form['name'] + 'already exists!'
        )
        return render_template('forms/new_artist.html', form=form)
      genres = ",".join(form.genres.data)

      artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, genres=genres,
                        image_link=form.image_link.data, facebook_link=form.facebook_link.data, website_link=form.website_link.data, is_venue_seeking=form.seeking_venue.data,
                        venue_seeking_description=form.seeking_description.data)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception:
      db.session.rollback()
      flash(
            'An error occured Artist ' +
            request.form['name'] +
            ' was not successfully listed!')
      print(sys.exc_info())
    finally:
      db.session.close()

    
    return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash(f'Artist: {artist_id} was successfully deleted!')
    except Exception:
        flash(f'Artist: {artist_id} was not successfully deleted!')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'Success': True})

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  try:
    data = []

    show_details = db.session.query(Show, Venue, Artist).select_from(
            Show).join(Venue).join(Artist).all()

    for show, venue, artist in show_details:
        data.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time
    })

  except Exception:
        flash(f'An error occured, could not get all shows successfully!')
        print(sys.exc_info())
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  venues = Venue.query.all()
  artists = Artist.query.all()

  form.venue_id.choices = []
  form.artist_id.choices = []

  for venue in venues:
    form.venue_id.choices.append({venue.id,venue.name})
  for artist in artists:
    form.artist_id.choices.append({artist.id,artist.name})

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm()

    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    start_time = form.start_time.data

    show = Show(
      venue_id=venue_id,
      artist_id=artist_id,
      start_time=start_time)

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception:
    db.session.rollback()
    flash('An error occured Show was not successfully listed!')
    print(sys.exc_info())
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
