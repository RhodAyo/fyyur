#----------------------------------------------------------------------------#
# Code refactored by Ayomide Oluwole
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from forms import ArtistForm
from flask_migrate import Migrate
from models import *
from sqlalchemy import all_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db.init_app(app)
migrate = Migrate(app,db)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:rhodayo10.@localhost:5432/fyyur'



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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue_list = db.session.query(Venue).join(Show).all()
  venue_show = db.session.query(Venue).all()
  upcoming_shows_result = db.session.query(Show).join(Venue).join(Artist).filter(Show.artist_id==Artist.id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_count = db.session.query(Show).join(Venue).join(Artist).filter(Show.artist_id==Artist.id).filter(Show.start_time>datetime.now()).count()
  upcoming_shows = []
  data=[]
  for venuelists in venue_show:
    data.append({
      "city": venuelists.city,
      "state": venuelists.state,
      "venues": [{
        "id": venuelists.id,
        "name": venuelists.name,
        "num_upcoming_shows": upcoming_shows_count ,
    }]
  })
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  place = db.session.query(Venue).all()
  search = request.form.get('search_term', '')
  result = db.session.query(Venue).filter(Venue.name.ilike("%{}%".format(search))).all()
  counts = db.session.query(Venue).filter(Venue.name.ilike("%{}%".format(search))).count()

  places=[]
  for location in result:
    places.append({
        "id": location.id,
        "name": location.name,
        "num_upcoming_shows": 0

    })
  response={
    "count": counts,
    "data": places,
  }

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  place = Venue.query.get(venue_id)
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==place.id).filter(Show.start_time<datetime.now()).all()
  past_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==place.id).filter(Show.start_time<datetime.now()).count()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==place.id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==place.id).filter(Show.start_time>datetime.now()).count()

  pastshows = []
  for past in past_shows:
    pastshows.append({
      "artist_id": past.artist_id,
      "artist_name": past.artist.name,
      "artist_image_link": past.artist.image_link,
      "start_time": past.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  upcomingshows = []
  for upcoming in upcoming_shows:
    upcomingshows.append({
      "artist_id": upcoming.artist_id,
      "artist_name": upcoming.artist.name,
      "artist_image_link": upcoming.artist.image_link,
      "start_time": upcoming.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  data1={
    "id": place.id,
    "name": place.name,
    "genres": place.genre,
    "address": place.address,
    "city": place.city,
    "state": place.state,
    "phone": place.phone,
    "website": place.website_link,
    "facebook_link": place.facebook_link,
    "seeking_talent": place.talent,
    "seeking_description": place.description,
    "image_link": place.image_link,
    "past_shows": pastshows,
    "upcoming_shows": upcomingshows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
 
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
      newvenue = Venue()
      newvenue.name = request.form.get("name")
      newvenue.city = request.form.get("city")
      newvenue.state = request.form.get("state")
      newvenue.address = request.form.get("address")
      newvenue.phone = request.form.get("phone")
      newvenue.genre = request.form.getlist("genres")
      newvenue.facebook_link = request.form.get("facebook_link")
      newvenue.image_link = request.form.get("image_link")
      newvenue.website_link = request.form.get("website_link")
      newvenue.talent = True if 'seeking_talent' in request.form else False
      newvenue.description = request.form.get("seeking_description")
    # TODO: modify data to be the data object returned from db insertion
      db.session.add(newvenue)
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

  
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue_delete=Venue.query.get_or_404(venue_id)
  try:
    db.session.delete(venue_delete)
    db.session.commit()
    flash("Venue deleted successfully!")
  except:
    db.session.rollback()
    flash("Error deleting Venue!")
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  singer = db.session.query(Artist).all()
  search = request.form.get('search_term', '')
  result = db.session.query(Artist).filter(Artist.name.ilike("%{}%".format(search))).all()
  counts = db.session.query(Artist).filter(Artist.name.ilike("%{}%".format(search))).count()
  # upcomingcount = 0
  # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  # starttime = db.session.query(Show).start_time
  # times= []
  # for newtime in starttime:
  #   times.append({
  #     "newtime" : newtime.start_time,
  #   })
  #     "newtime" : newtime.start_time,
  #     if newtime > current_time:
  #       upcomingcount += 1
  #     else:
  #       upcomingcount = 0
  # }
  # Artist.query.filter(Post.title.ilike('%some_phrase%'))
  # Artist.query.filter(Post.title.ilike('%{some_phrase}%'))
  artistes=[]
  for sing in result:
    artistes.append({
      "id": sing.id,
      "name": sing.name,
      "num_upcoming_shows": 0,
    })
  response={
    "count": counts,
    "data": artistes,
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  art = Artist.query.get(artist_id)
  past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==art.id).filter(Show.start_time<datetime.now()).all()
  past_shows_count = db.session.query(Show).join(Artist).filter(Show.artist_id==art.id).filter(Show.start_time<datetime.now()).count()
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==art.id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_count = db.session.query(Show).join(Artist).filter(Show.artist_id==art.id).filter(Show.start_time>datetime.now()).count()

  pastshows = []
  for past in past_shows:
    pastshows.append({
      "artist_id": past.venue_id,
      "artist_name": past.venue.name,
      "artist_image_link": past.venue.image_link,
      "start_time": past.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  upcomingshows = []
  for upcoming in upcoming_shows:
    upcomingshows.append({
      "artist_id": upcoming.venue_id,
      "artist_name": upcoming.venue.name,
      "artist_image_link": upcoming.venue.image_link,
      "start_time": upcoming.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  data1={
    "id": art.id,
    "name": art.name,
    "genres": art.genre,
    "city": art.city,
    "state": art.state,
    "phone": art.phone,
    "website": art.website_link,
    "facebook_link": art.facebook_link,
    "seeking_venue": art.venues,
    "seeking_description": art.description,
    "image_link": art.image_link,
    "past_shows": pastshows,
    "upcoming_shows": upcomingshows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
 
  return render_template('pages/show_venue.html', venue=data1)

  # data1={
  #   "id": d.id,
  #   "name": d.name,
  #   "genres": d.genre,
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1]))
  # return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  artist =Artist.query.get(artist_id)
  form=ArtistForm(obj=artist)

  # if artist:
  #   form.name.data = artist.name,
  #   form.genres.data = artist.genre,
  #   form.city.data = artist.city,
  #   form.state.data = artist.state,
  #   form.phone.data = artist.phone,
  #   form.website_link.data = artist.website_link,
  #   form.facebook_link.data = artist.facebook_link,
  #   form.seeking_venue.data = artist.venues,
  #   form.seeking_description.data = artist.description,
  #   form.image_link.data = artist.image_link,

  # TODO: populate form with fields from artist with ID <artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form =ArtistForm()
  artist =Artist.query.get(artist_id)
  
  try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genre = form.genres.data                                                                       
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.website_link = form.website_link.data
      artist.venues = form.seeking_venue.data
      artist.description = form.seeking_description.data
    # TODO: modify data to be the data object returned from db insertion
      db.session.commit()
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name']+ ' could not be updated.')
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  venues =Venue.query.get(venue_id)
  form=VenueForm(obj=venues)
  # venues =db.query.session(Venue).all()

  # if venues:
  #   form.name.data = venues.name,
  #   form.genres.data = venues.genre,
  #   form.address.data = venues.address,
  #   form.city.data = venues.city,
  #   form.state.data = venues.state,
  #   form.phone.data = venues.phone,
  #   form.website_link.data = venues.website_link,
  #   form.facebook_link.data = venues.facebook_link,
  #   form.seeking_talent.data = venues.talent,
  #   form.seeking_description.data = venues.description,
  #   form.image_link.data = venues.talent,

  return render_template('forms/edit_venue.html', form=form, venue=venues)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form =VenueForm(request.form)
  venues =Venue.query.get(venue_id)
  
  try:
      venues.name = form.name.data
      venues.city = form.city.data
      venues.state = form.state.data
      venues.address = form.address.data
      venues.phone = form.phone.data
      venues.genre = form.genres.data
      venues.facebook_link = form.facebook_link.data
      venues.image_link = form.image_link.data
      venues.website_link = form.website_link.data
      venues.talent =  form.seeking_talent.data 
      venues.description = form.seeking_description.data
    # TODO: modify data to be the data object returned from db insertion
      db.session.add(venues)
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name']+ ' could not be updated.')
  finally:
      db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
    
    try:
      newartist = Artist()
      newartist.name = request.form.get("name")
      newartist.city = request.form.get("city")
      newartist.state = request.form.get("state")
      newartist.phone = request.form.get("phone")
      newartist.genre = request.form.getlist("genres")
      newartist.facebook_link = request.form.get("facebook_link")
      newartist.image_link = request.form.get("image_link")
      newartist.website_link = request.form.get("website_link")
      newartist.venues = True if 'seeking_venue' in request.form else False
      newartist.description = request.form.get("seeking_description")
    # TODO: modify data to be the data object returned from db insertion
      db.session.add(newartist)
      db.session.commit()
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  showlist = db.session.query(Show).join(Venue).join(Artist).all()
  # TODO: replace with real venues data.
  # An array called Data to hold venue details via the ID and name, artist on id and name and show start time.
  data=[] 
  # looping through the showlist query, append list to data Array
  for lists in showlist:
      data.append({
        "venue_id": lists.venue.id,
        "venue_name": lists.venue.name,
        "artist_id": lists.artist.id,
        "artist_name": lists.artist.name,
        "artist_image_link": lists.artist.image_link,
        "start_time": lists.start_time.strftime("%Y-%m-%d %H:%M:%S"),
  })
  # , {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # },
  #  {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
      newshow = Show()
      newshow.start_time = request.form.get("start_time")
      newshow.venue_id = request.form.get("venue_id")
      newshow.artist_id = request.form.get("artist_id")
    # TODO: modify data to be the data object returned from db insertion
      db.session.add(newshow)
      db.session.commit()
    # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
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
