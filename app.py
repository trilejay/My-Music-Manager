from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask import request
import os


app = Flask(__name__)
app.secret_key = "hello"

app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = 'Moogle14!'
app.config['MYSQL_DB'] = ''
app.config['MYSQL_CURSORCLASS'] = "DictCursor"


mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        birthdate = request.form.get('birthdate')
        genre = request.form.get('genre')

        if genre == '':
            genre = None  # set genre to NULL

        cur = mysql.connection.cursor()

        cur.execute('''
        INSERT INTO artists(name, email, birthdate, genres_genre_id) VALUES(%s, %s, %s, %s)
        ''', (name, email, birthdate, genre,))

        mysql.connection.commit()
        cur.close()
        flash('Artist: ' + str(name) + ' - Successfully added!', "success")

        return redirect(url_for('artist_info'))
    
    else:
        # Handle the GET request to display the form
        cur = mysql.connection.cursor()
        cur.execute("SELECT genre_id, name FROM genres")  # Query to get genres
        genres = cur.fetchall()
        cur.close()
        print(genres)

        return render_template('submit_artist.html', genres=genres)


@app.route('/submit_track', methods=['POST'])
def submit_track():
    if request.method == 'POST':
        title = request.form.get('title')
        release_date = request.form.get('release_date')
        duration = request.form.get('duration')
        album = request.form.get('album')
        genre = request.form.get('genre')
        artists = request.form.getlist('artist')
        print(f"Artists selected: {artists}")  # Output to verify the structure

        cur = mysql.connection.cursor()

        if genre == '':
            genre = None  # set genre to NULL

        # insert into tracks table
        cur.execute('''
        INSERT INTO tracks(title, release_date, duration, genres_genre_id)
        VALUES(%s, %s, %s, %s)
        ''', (title, release_date, duration, genre,))

        # get the track ID of the inserted track
        track_id = cur.lastrowid
        
        # insert the relationship into the 'artists_tracks' intersection table
        if artists:
            for artist_id in artists:
                
                cur.execute('''
                INSERT INTO artists_tracks(artists_artist_id, tracks_track_id)
                VALUES(%s, %s)
                ''', (artist_id, track_id,))
            if album:
                for artist_id in artists:  # Associate each selected artist with the album
                    cur.execute('''
                    INSERT INTO artists_albums(artists_artist_id, albums_album_id)
                    VALUES(%s, %s)
                    ''', (artist_id, album))

        mysql.connection.commit()
        cur.close()
        flash('Track: ' + str(title) + ' - Successfully added!', "success")

        return redirect(url_for('track'))


@app.route('/submit_genre', methods=['POST'])
def submit_genre():
    if request.method == 'POST':
        name = request.form.get('name')

        cur = mysql.connection.cursor()

        cur.execute('''
        INSERT INTO genres(name) VALUES(%s)
        ''', (name,))

        mysql.connection.commit()
        cur.close()
        flash('Genre: ' + str(name) + ' - Successfully added!', "success")

        return redirect(url_for('genre'))


@app.route('/submit_album', methods=['POST'])
def submit_album():

    if request.method == 'POST':
        title = request.form.get('title')
        release_date = request.form.get('release_date')
        genre = request.form.get('genre')
        artists = request.form.getlist('artist')

        cur = mysql.connection.cursor()

        if genre == '':
            genre = None  # set genre to NULL

        cur.execute('''
        INSERT INTO albums(title, release_date, genres_genre_id) VALUES(%s, %s, %s)
        ''', (title, release_date, genre,))

        # Get the album ID of the inserted album
        album_id = cur.lastrowid

        # Insert the relationship into the 'artists_albums' intersection table
        if artists:
            for artist_id in artists:
                cur.execute('''
                INSERT INTO artists_albums(artists_artist_id, albums_album_id)
                VALUES(%s, %s)
                ''', (artist_id, album_id))

        mysql.connection.commit()
        cur.close()
        flash('Album: ' + str(title) + ' - Successfully added!', "success")

        return redirect(url_for('album'))
    

@app.route('/artist_info.html', methods=['GET'])
def artist_info():
    cur = mysql.connection.cursor()

    cur.execute("SELECT genre_id, name FROM genres")
    genres = cur.fetchall()

    cur.execute('''
        SELECT artists.artist_id, artists.name, artists.email, artists.birthdate, genres.name AS genre
        FROM artists
        LEFT JOIN genres ON artists.genres_genre_id = genres.genre_id
        ''')
    artists = cur.fetchall()

    cur.close()

    return render_template('artist_info.html', artists=artists, genres=genres)


@app.route('/track', methods=['GET'])
def track():
    cur = mysql.connection.cursor()

     # Query to get genres, artists and albums
    cur.execute("SELECT genre_id, name FROM genres")
    genres = cur.fetchall()

    cur.execute("SELECT artist_id, name FROM artists")
    artists = cur.fetchall()

    cur.execute("SELECT album_id, title FROM albums")
    albums = cur.fetchall()

    cur.execute('''
        SELECT 
            tracks.track_id,
            tracks.title,
            tracks.release_date,
            tracks.duration,
            genres.name AS genre_name
        FROM 
            tracks
        LEFT JOIN 
            genres ON tracks.genres_genre_id = genres.genre_id;
    ''')
    tracks = cur.fetchall()

    cur.close()

    return render_template('track.html', tracks=tracks, genres=genres, artists=artists, albums=albums)


@app.route('/genre', methods=['GET'])
def genre():
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM genres")
    genres = cur.fetchall()

    cur.close()

    return render_template('genre.html', genres=genres)


@app.route('/album', methods=['GET'])
def album():
    cur = mysql.connection.cursor()

    cur.execute("SELECT genre_id, name FROM genres")
    genres = cur.fetchall()

    cur.execute("SELECT artist_id, name FROM artists")
    artists = cur.fetchall()

    cur.execute('''
    SELECT albums.album_id, albums.title, albums.release_date, genres.name AS genre_name
    FROM albums 
    LEFT JOIN genres ON albums.genres_genre_id = genres.genre_id
    ''')
    albums = cur.fetchall()

    cur.close()

    return render_template('album.html', albums=albums, genres=genres, artists=artists)


@app.route('/artists/update/<int:artist_id>', methods=['GET', 'POST'])
def update_artist(artist_id):
    cur = mysql.connection.cursor()

    # Fetch the artist to be updated
    cur.execute('SELECT * FROM artists WHERE artist_id = %s', (artist_id,))
    artist = cur.fetchone()

    # Fetch all genres for the dropdown
    cur.execute("SELECT genre_id, name FROM genres")  # Query to get genres
    genres = cur.fetchall()

    # If the artist doesn't exist, return 404
    if artist is None:
        cur.close()
        return "Artist not found", 404
    
    # Handle form submission for updating artist
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        birthdate = request.form.get('birthdate')
        genre = request.form.get('genre')

        if genre == '':
            genre = None  # set genre to NULL

        cur.execute('''
        UPDATE artists
        SET name = %s, email =%s, birthdate = %s, genres_genre_id = %s
        WHERE artist_id = %s''', (name, email, birthdate, genre, artist_id,))

        mysql.connection.commit()
        cur.close()
        flash('artist_id: ' + str(artist_id) + ' - Updated Successfully!', "success")

        return redirect(url_for('artist_info'))

    cur.close()
    return render_template('update_artist.html', artist=artist, genres=genres)


@app.route('/tracks/update/<int:track_id>', methods=['GET', 'POST'])
def update_track(track_id):
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM tracks WHERE track_id = %s', (track_id,))
    track = cur.fetchone()

    # Query to get genres, artists, and albums
    cur.execute("SELECT genre_id, name FROM genres")
    genres = cur.fetchall()

    cur.execute("SELECT artist_id, name FROM artists")
    artists = cur.fetchall()

    cur.execute("SELECT album_id, title FROM albums")
    albums = cur.fetchall()

    if track is None:
        cur.close()
        return "Track not found", 404

    if request.method == "POST":
        title = request.form.get('title')
        release_date = request.form.get('release_date')
        duration = request.form.get('duration')
        album = request.form.get('album')
        genre = request.form.get('genre')
        artist = request.form.get('artist')

        if genre == '':
            genre = None  # set genre to NULL

        # update tracks table
        cur.execute('''
        UPDATE tracks
        SET title = %s, release_date =%s, duration = %s, genres_genre_id = %s
        WHERE track_id = %s''', (title, release_date, duration, genre, track_id,))

        # Update the relationship for artist and album if provided
        if artist:
            cur.execute('''
            UPDATE artists_tracks
            SET artists_artist_id = %s
            WHERE tracks_track_id = %s
            ''', (artist, track_id,))

        if album:
            cur.execute('''
            UPDATE artists_albums
            SET albums_album_id = %s
            WHERE artists_artist_id = %s
            ''', (album, artist,))

        mysql.connection.commit()
        cur.close()
        flash('track_id: ' + str(track_id) + ' - Updated Successfully!', "success")

        return redirect(url_for('track'))

    cur.close()
    return render_template('update_track.html', artists=artists, track=track, genres=genres, albums=albums)

@app.route('/genres/update/<int:genre_id>', methods=['GET', 'POST'])
def update_genre(genre_id):
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM genres WHERE genre_id = %s', (genre_id,))
    genre = cur.fetchone()

    if genre is None:
        cur.close()
        return "Genre not found", 404

    if request.method == "POST":
        name = request.form.get('name')

        cur.execute('''
        UPDATE genres
        SET name = %s
        WHERE genre_id = %s''', (name,genre_id,))

        mysql.connection.commit()
        cur.close()
        flash('genre_id: ' + str(genre_id) + ' - Updated Successfully!', "success")

        return redirect(url_for('genre'))

    cur.close()
    return render_template('update_genre.html', genre=genre)


@app.route('/albums/update/<int:album_id>', methods=['GET', 'POST'])
def update_album(album_id):
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM albums WHERE album_id = %s', (album_id,))
    album = cur.fetchone()

    cur.execute("SELECT genre_id, name FROM genres")
    genres = cur.fetchall()

    if album is None:
        cur.close()
        return "Album not found", 404

    if request.method == "POST":
        title = request.form.get('title')
        release_date = request.form.get('release_date')
        genre = request.form.get('genre')

        cur.execute('''
        UPDATE albums
        SET title = %s, release_date = %s, genres_genre_id = %s
        WHERE album_id = %s''', (title, release_date, genre, album_id,))

        mysql.connection.commit()
        cur.close()
        flash('album_id: ' + str(album_id) + ' - Updated Successfully!', "success")

        return redirect(url_for('album'))

    cur.close()
    return render_template('update_album.html', album=album, genres=genres)

@app.route('/artists_tracks/update/<int:artist_id>/<int:track_id>', methods=['GET', 'POST'])
def update_artists_tracks(artist_id, track_id):
    cur = mysql.connection.cursor()

    cur.execute('''
        SELECT artists.artist_id, artists.name AS artist_name, tracks.track_id, tracks.title AS track_title
        FROM artists
        JOIN artists_tracks ON artists.artist_id = artists_tracks.artists_artist_id
        JOIN tracks ON tracks.track_id = artists_tracks.tracks_track_id
        WHERE artists.artist_id = %s AND tracks.track_id = %s
    ''', (artist_id, track_id))

    association = cur.fetchone()

    if association is None:
        cur.close()
        return "Artist and Track association not found", 404

    # fetch artist_id to display in dropdown
    cur.execute('SELECT artist_id, name FROM artists')
    artists = cur.fetchall()

    # fetch track_id to display in dropdown
    cur.execute('SELECT track_id, title FROM tracks')
    tracks = cur.fetchall()

    if request.method == "POST":
        new_artist_id = request.form['artist_id']
        new_track_id = request.form['track_id']

        cur.execute('''
            UPDATE artists_tracks
            SET artists_artist_id = %s, tracks_track_id = %s
            WHERE artists_artist_id = %s AND tracks_track_id = %s
        ''', (new_artist_id, new_track_id, artist_id, track_id))

        mysql.connection.commit()
        cur.close()
        flash('track_id: ' + str(track_id) + ' - Updated Successfully!', "success")

        return redirect(url_for('artists_tracks'))

    cur.close()
    return render_template('update_artists_tracks.html', 
                           association=association, 
                           artists=artists, 
                           tracks=tracks)

@app.route('/artists_albums/update/<int:album_id>/<int:artist_id>', methods=['GET', 'POST'])
def update_artists_albums(album_id, artist_id):
    cur = mysql.connection.cursor()

    cur.execute('''
        SELECT albums.album_id, albums.title AS album_title, artists.artist_id, artists.name AS artist_name
        FROM albums
        JOIN artists_albums ON albums.album_id = artists_albums.albums_album_id
        JOIN artists ON artists_albums.artists_artist_id = artists.artist_id
        WHERE artists.artist_id = %s AND albums.album_id = %s
    ''', (artist_id, album_id,))
   

    album_data = cur.fetchone()

    if album_data is None:
        cur.close()
        return "Artist and album association not found", 404
    
    # fetch artist_id to display in dropdown
    cur.execute('SELECT artist_id, name FROM artists')
    artists = cur.fetchall()

    # fetch album_id to display in dropdown
    cur.execute('SELECT * FROM albums')
    albums = cur.fetchall()

    if request.method == "POST":
        new_artist_id = request.form.get('new_artist_id')
        new_album_id = request.form.get('new_album_id')

        cur.execute('''
            UPDATE artists_albums
            SET artists_artist_id = %s, albums_album_id = %s
            WHERE artists_artist_id = %s AND albums_album_id = %s
        ''', (new_artist_id, new_album_id, artist_id, album_id,))

        mysql.connection.commit()
        cur.close()
        flash('album_id: ' + str(album_id) + ' - Updated Successfully!', "success")

        return redirect(url_for('artists_albums'))

    cur.close()
    return render_template('update_artists_albums.html', 
                           album_data=album_data, 
                           artists=artists, 
                           albums=albums)


@app.route('/artists/delete/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM artists WHERE artist_id = %s', (artist_id,))

    mysql.connection.commit()
    cur.close()
    flash('artist_id: ' + str(artist_id) + ' - Deleted Successfully!', "success")

    return redirect(url_for('artist_info'))


@app.route('/tracks/delete/<int:track_id>', methods=['POST'])
def delete_track(track_id):
    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM tracks WHERE track_id = %s', (track_id,))

    mysql.connection.commit()
    cur.close()
    flash('track_id: ' + str(track_id) + ' - Deleted Successfully!', "success")

    return redirect(url_for('track'))


@app.route('/genres/delete/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM genres WHERE genre_id = %s', (genre_id,))

    mysql.connection.commit()
    cur.close()
    flash('genre_id: ' + str(genre_id) + ' - Deleted Successfully!', "success")

    return redirect(url_for('genre'))
    

@app.route('/albums/delete/<int:album_id>', methods=['POST'])
def delete_album(album_id):
    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM albums WHERE album_id = %s', (album_id,))

    mysql.connection.commit()
    cur.close()
    flash('album_id: ' + str(album_id) + ' - Deleted Successfully!', "success")

    return redirect(url_for('album'))

@app.route('/artists_genres', methods=['GET'])
def artists_genres():
    cur = mysql.connection.cursor()

    cur.execute('''
        SELECT artists.artist_id, artists.name AS artist_name, genres.genre_id, genres.name AS genre_name
        FROM artists
        JOIN artists_genres ON artists.artist_id = artists_genres.artists_artist_id
        JOIN genres ON artists_genres.genres_genre_id = genres.genre_id
    ''')

    artist_data = cur.fetchall()

    artists = {}
    for row in artist_data:
        artist_id = row['artist_id']
        if artist_id not in artists:
            artists[artist_id] = {
                'artist_id': artist_id,
                'artist_name': row['artist_name'],
                'genres': []
            }
        artists[artist_id]['genres'].append({'genre_id': row['genre_id'], 'genre_name': row['genre_name']})

    cur.close()

    return render_template('artists_genres.html', artists=artists.values())

@app.route('/artists_tracks/delete/<int:artist_id>/<int:track_id>', methods=['POST'])
def delete_artists_tracks(artist_id, track_id):
    cur = mysql.connection.cursor()

    cur.execute('''DELETE FROM artists_tracks
                WHERE artists_artist_id = %s AND tracks_track_id = %s''', 
                (artist_id, track_id,))
        
    mysql.connection.commit()

    cur.close()
    flash('track_id: ' + str(track_id) + ' - Deleted Successfully!', "success")

    return redirect(url_for('artists_tracks'))

@app.route('/artists_albums/delete/<int:album_id>/<int:artist_id>', methods=['POST'])
def delete_artists_albums(artist_id, album_id):
    cur = mysql.connection.cursor()

    cur.execute('''DELETE FROM artists_albums
                WHERE artists_artist_id = %s AND albums_album_id = %s''', 
                (artist_id, album_id,))
        
    mysql.connection.commit()

    cur.close()
    flash('Album_id: ' + str(album_id) + ' - Deleted Successfully!', "success")

    return redirect(url_for('artists_albums'))

@app.route('/artists_tracks', methods=['GET'])
def artists_tracks():
    cur = mysql.connection.cursor()


    cur.execute('''
        SELECT tracks.track_id, tracks.title, artists.artist_id, artists.name AS artist_name
        FROM tracks
        JOIN artists_tracks ON tracks.track_id = artists_tracks.tracks_track_id
        JOIN artists ON artists_tracks.artists_artist_id = artists.artist_id
    ''')

    track_data = cur.fetchall()

    tracks = {}
    for row in track_data:
        track_id = row['track_id']
        if track_id not in tracks:
            tracks[track_id] = {
                'track_id': track_id,
                'title': row['title'],
                'artists': []
            }
        tracks[track_id]['artists'].append({'artist_id': row['artist_id'], 'artist_name': row['artist_name']})

    cur.close()

    return render_template('artists_tracks.html', tracks=tracks.values())

@app.route('/artists_albums', methods=['GET'])
def artists_albums():
    cur = mysql.connection.cursor()

    cur.execute('''
        SELECT albums.album_id, albums.title AS album_title, artists.artist_id, artists.name AS artist_name
        FROM albums
        JOIN artists_albums ON albums.album_id = artists_albums.albums_album_id
        JOIN artists ON artists_albums.artists_artist_id = artists.artist_id
    ''')


    album_data = cur.fetchall()

    albums = {}
    for row in album_data:
        album_id = row['album_id']
        if album_id not in albums:
            albums[album_id] = {
                'album_id': album_id,
                'title': row['album_title'],
                'artists': []
            }
        albums[album_id]['artists'].append({'artist_id': row['artist_id'], 'artist_name': row['artist_name']})

    cur.close()

    return render_template('artists_albums.html', albums=albums.values())

@app.route('/tracks_genres', methods=['GET'])
def tracks_genres():
    cur = mysql.connection.cursor()

    cur.execute('''
        SELECT tracks.track_id, tracks.title AS track_title, genres.genre_id, genres.name AS genre_name
        FROM tracks
        JOIN tracks_genres ON tracks.track_id = tracks_genres.tracks_track_id
        JOIN genres ON tracks_genres.genres_genre_id = genres.genre_id
    ''')


    track_data = cur.fetchall()

    tracks = {}
    for row in track_data:
        track_id = row['track_id']
        if track_id not in tracks:
            tracks[track_id] = {
                'track_id': track_id,
                'title': row['track_title'],
                'genres': []
            }
        tracks[track_id]['genres'].append({'genre_id': row['genre_id'], 'genre_name': row['genre_name']})

    cur.close()

    return render_template('tracks_genres.html', tracks=tracks.values())

@app.route('/albums_genres', methods=['GET'])
def albums_genres():
    cur = mysql.connection.cursor()

    # Query to fetch albums and their associated genres
    cur.execute('''
        SELECT albums.album_id, albums.title AS album_title, genres.genre_id, genres.name AS genre_name
        FROM albums
        JOIN albums_genres ON albums.album_id = albums_genres.albums_album_id
        JOIN genres ON albums_genres.genres_genre_id = genres.genre_id
    ''')

    album_data = cur.fetchall()

    albums = {}
    for row in album_data:
        album_id = row['album_id']
        if album_id not in albums:
            albums[album_id] = {
                'album_id': album_id,
                'title': row['album_title'],
                'genres': []
            }
        albums[album_id]['genres'].append({'genre_id': row['genre_id'], 'genre_name': row['genre_name']})

    cur.close()

    return render_template('albums_genres.html', albums=albums.values())


if __name__ == "__main__":
    app.run(port=3746, debug=True)
