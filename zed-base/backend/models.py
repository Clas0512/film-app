from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Film(db.Model):
    __tablename__ = 'films'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_title = db.Column(db.String(255))
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    release_date = db.Column(db.Date)
    duration_minutes = db.Column(db.Integer)
    rating = db.Column(db.Float)
    age_rating = db.Column(db.String(10))
    language = db.Column(db.String(50))
    country = db.Column(db.String(100))
    budget = db.Column(db.BigInteger)
    revenue = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cast = db.relationship('FilmArtist', back_populates='film')
    genres = db.relationship('FilmGenre', back_populates='film')

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    full_name = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    gender = db.Column(db.String(20))
    nationality = db.Column(db.String(100))
    biography = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    film_credits = db.relationship('FilmArtist', back_populates='artist')

class FilmArtist(db.Model):
    __tablename__ = 'film_artists'
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    role_type = db.Column(db.String(50))  # e.g., Actor, Director, Producer
    character_name = db.Column(db.String(200))
    billing_order = db.Column(db.Integer)

    film = db.relationship('Film', back_populates='cast')
    artist = db.relationship('Artist', back_populates='film_credits')

class FilmGenre(db.Model):
    __tablename__ = 'film_genres'
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'), primary_key=True)
    genre_name = db.Column(db.String(100), primary_key=True)

    film = db.relationship('Film', back_populates='genres')

class UserReview(db.Model):
    __tablename__ = 'user_reviews'
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('films.id'))
    user_id = db.Column(db.Integer) # Simplified for now
    user_rating = db.Column(db.Float)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
