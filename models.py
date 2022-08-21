from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.



#------------------------ venue model ----------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    venue_website = db.Column(db.String(120))
    searching_talent = db.Column(db.Boolean, nullable=False, default=False)
    talent_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f'Venue id: {self.id} name: {self.name} city: {self.city} state: {self.state}'
#------------------------- artist model --------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    artist_website = db.Column(db.String(120))
    searching_venue = db.Column(db.Boolean, nullable=False, default=False)
    venue_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'Artist id: {self.id} name: {self.name} city: {self.city} state: {self.state}'


#------------------------- show model --------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False) 
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False) 
    show_start_time = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'Show artist_id: {self.artist_id} venue_id: {self.venue_id}'