import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Film, Artist, FilmArtist, FilmGenre, UserReview
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration - Use SQLite as fallback (no server required)
# Set DATABASE_URL in environment to use PostgreSQL, otherwise SQLite
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Use SQLite as default - no server required
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'films.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables when app starts
with app.app_context():
    db.create_all()

@app.route('/api/films/search', methods=['GET'])
def search_films():
    try:
        query_param = request.args.get('q', '')
        year = request.args.get('year')
        rating = request.args.get('rating')
        cast_name = request.args.get('cast')

        query = Film.query

        if query_param and query_param.strip():
            query = query.filter(Film.title.ilike("%{}%".format(query_param)))
        
        if year and year.strip():
            try:
                query = query.filter(Film.release_year == int(year))
            except ValueError:
                pass

        if rating and rating.strip():
            try:
                query = query.filter(Film.rating >= float(rating))
            except ValueError:
                pass

        if cast_name and cast_name.strip():
            # Filter films by cast name
            query = query.join(FilmArtist).join(Artist).filter(
                (Artist.first_name.ilike("%" + cast_name + "%")) | 
                (Artist.last_name.ilike("%" + cast_name + "%")) |
                (Artist.full_name.ilike("%" + cast_name + "%"))
            )

        films = query.all()
        
        results = []
        for film in films:
            results.append({
                'id': film.id,
                'title': film.title,
                'release_year': film.release_year,
                'rating': film.rating,
                'description': film.description,
                'cast': [{'name': fa.artist.full_name, 'role': fa.role_type} for fa in film.cast]
            })

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artists/search', methods=['GET'])
def search_artists():
    query_param = request.args.get('q', '')
    
    query = Artist.query
    if query_param:
        query = query.filter(
            (Artist.first_name.ilike("%" + query_param + "%")) | 
            (Artist.last_name.ilike("%" + query_param + "%")) |
            (Artist.full_name.ilike("%" + query_param + "%"))
        )
    
    artists = query.all()
    results = []
    for artist in artists:
        results.append({
            'id': artist.id,
            'full_name': artist.full_name,
            'nationality': artist.nationality,
            'biography': artist.biography
        })
    
    return jsonify(results)

@app.route('/api/init-db', methods=['POST'])
def init_db():
    db.create_all()
    return jsonify({'message': 'Database initialized successfully'})

# ============ DATA ENTRY ENDPOINTS ============

@app.route('/api/films', methods=['POST'])
def add_film():
    """Add a new film to the database"""
    try:
        data = request.get_json()
        
        film = Film(
            title=data.get('title'),
            original_title=data.get('original_title'),
            description=data.get('description'),
            release_year=data.get('release_year'),
            release_date=data.get('release_date'),
            duration_minutes=data.get('duration_minutes'),
            rating=data.get('rating'),
            age_rating=data.get('age_rating'),
            language=data.get('language'),
            country=data.get('country'),
            budget=data.get('budget'),
            revenue=data.get('revenue')
        )
        
        db.session.add(film)
        db.session.commit()
        
        # Add genres if provided
        if 'genres' in data:
            for genre_name in data['genres']:
                genre = FilmGenre(film_id=film.id, genre_name=genre_name)
                db.session.add(genre)
            db.session.commit()
        
        return jsonify({'message': 'Film added successfully', 'id': film.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/artists', methods=['POST'])
def add_artist():
    """Add a new artist to the database"""
    try:
        data = request.get_json()
        
        artist = Artist(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            full_name=data.get('full_name'),
            birth_date=data.get('birth_date'),
            death_date=data.get('death_date'),
            gender=data.get('gender'),
            nationality=data.get('nationality'),
            biography=data.get('biography')
        )
        
        db.session.add(artist)
        db.session.commit()
        
        return jsonify({'message': 'Artist added successfully', 'id': artist.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/films/<int:film_id>/cast', methods=['POST'])
def add_cast_member(film_id):
    """Add a cast member (artist) to a film"""
    try:
        data = request.get_json()
        artist_id = data.get('artist_id')
        
        # Check if film and artist exist
        film = Film.query.get(film_id)
        artist = Artist.query.get(artist_id)
        
        if not film:
            return jsonify({'error': 'Film not found'}), 404
        if not artist:
            return jsonify({'error': 'Artist not found'}), 404
        
        # Check if relationship already exists
        existing = FilmArtist.query.filter_by(film_id=film_id, artist_id=artist_id).first()
        if existing:
            return jsonify({'error': 'This artist is already in the cast'}), 400
        
        cast_member = FilmArtist(
            film_id=film_id,
            artist_id=artist_id,
            role_type=data.get('role_type', 'Actor'),
            character_name=data.get('character_name'),
            billing_order=data.get('billing_order')
        )
        
        db.session.add(cast_member)
        db.session.commit()
        
        return jsonify({'message': 'Cast member added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/films/<int:film_id>/genres', methods=['POST'])
def add_film_genre(film_id):
    """Add a genre to a film"""
    try:
        data = request.get_json()
        genre_name = data.get('genre_name')
        
        film = Film.query.get(film_id)
        if not film:
            return jsonify({'error': 'Film not found'}), 404
        
        existing = FilmGenre.query.filter_by(film_id=film_id, genre_name=genre_name).first()
        if existing:
            return jsonify({'error': 'Genre already exists for this film'}), 400
        
        genre = FilmGenre(film_id=film_id, genre_name=genre_name)
        db.session.add(genre)
        db.session.commit()
        
        return jsonify({'message': 'Genre added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/films/<int:film_id>/reviews', methods=['POST'])
def add_review(film_id):
    """Add a user review for a film"""
    try:
        data = request.get_json()
        
        film = Film.query.get(film_id)
        if not film:
            return jsonify({'error': 'Film not found'}), 404
        
        review = UserReview(
            film_id=film_id,
            user_id=data.get('user_id', 1),
            user_rating=data.get('user_rating'),
            review=data.get('review')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({'message': 'Review added successfully', 'id': review.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============ GET ENDPOINTS FOR DATA MANAGEMENT ============

@app.route('/api/films', methods=['GET'])
def get_all_films():
    """Get all films (for dropdown/selection in UI)"""
    try:
        films = Film.query.all()
        results = []
        for film in films:
            results.append({
                'id': film.id,
                'title': film.title,
                'release_year': film.release_year,
                'rating': film.rating
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artists', methods=['GET'])
def get_all_artists():
    """Get all artists (for dropdown/selection in UI)"""
    try:
        artists = Artist.query.all()
        results = []
        for artist in artists:
            results.append({
                'id': artist.id,
                'full_name': artist.full_name,
                'nationality': artist.nationality
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/films/<int:film_id>', methods=['GET'])
def get_film(film_id):
    """Get detailed information about a specific film"""
    try:
        film = Film.query.get(film_id)
        if not film:
            return jsonify({'error': 'Film not found'}), 404
        
        return jsonify({
            'id': film.id,
            'title': film.title,
            'original_title': film.original_title,
            'description': film.description,
            'release_year': film.release_year,
            'release_date': film.release_date,
            'duration_minutes': film.duration_minutes,
            'rating': film.rating,
            'age_rating': film.age_rating,
            'language': film.language,
            'country': film.country,
            'budget': film.budget,
            'revenue': film.revenue,
            'genres': [g.genre_name for g in film.genres],
            'cast': [{
                'artist_id': fa.artist_id,
                'name': fa.artist.full_name,
                'role_type': fa.role_type,
                'character_name': fa.character_name,
                'billing_order': fa.billing_order
            } for fa in film.cast]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
