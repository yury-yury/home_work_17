from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.app_context().push()
db = SQLAlchemy(app)


class Movie(db.Model):
    """
    The Movie class inherits from the Model class of the flask_sqlalchemy library defines the model
    of the 'movie' table of the database used.
    """
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    """
    The MovieSchema class inherits from the Schema class of the marshmallow library and defines the schema
    of the 'movie' table of the database used for serialization and deserialization of objects.
    """
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    year = fields.Int()
    trailer = fields.Str()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    """
    The Director class inherits from the Model class of the flask_sqlalchemy library defines the model
    of the 'director' table of the database used.
    """
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    """
    The Directory Schema class inherits from the Schema class of the marshmallow library and defines the schema
    of the 'director' table of the database used for serialization and deserialization of objects.
    """
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    """
    The Genre class inherits from the Model class of the flask_sqlalchemy library defines the model
    of the 'genre' table of the database used.
    """
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    """
    The GenreSchema class inherits from the Schema class of the marshmallow library and defines the schema
    of the 'genre' table of the database used for serialization and deserialization of objects.
    """
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genre')


@movie_ns.route('/')
class MoviesView(Resource):
    """
    The MoviesView class inherits from the Resource class of the flask_restx library and
    is a Base View class designed to process requests at the address "/movies/".
    """
    def get(self):
        """
        The function does not accept arguments and is designed to process GET requests to the address "/movies/",
        implements various types of movie search in the database: all movies, movies of a certain genre,
        movies of a certain director and movies of a certain director and genre.
        """
        if request.args.get("director_id") and request.args.get("genre_id"):
            movies = db.session.query(Movie).filter(Movie.director_id == int(request.args.get("director_id")),
                                                    Movie.genre_id == int(request.args.get("genre_id")))
            return movies_schema.dump(movies)

        elif request.args.get("director_id"):
            movies = db.session.query(Movie).filter(Movie.director_id == int(request.args.get("director_id")))
            return movies_schema.dump(movies)

        elif request.args.get("genre_id"):
            movies = db.session.query(Movie).filter(Movie.genre_id == int(request.args.get("genre_id")))
            return movies_schema.dump(movies)

        else:
            page = request.args.get("page", 1, type=int)
            all_movies = db.session.query(Movie).limit(2).offset((page - 1) * 2).all()
            return movies_schema.dump(all_movies)

    def post(self):
        """
        The function does not accept arguments and is designed to process a POST request at the address "/movies/",
        implements the creation of a new movie and writing it to the database,
        returns the created database object in the form of JSON.
        """
        movie = request.json

        movie_dict = movie_schema.load(movie)
        new_movie = Movie(**movie_dict)

        db.session.add(new_movie)
        db.session.commit()

        return movie_schema.dump(new_movie)


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    """
    he MovieView class inherits from the Resource class of the flask_rectx library and
    is a Base View class designed to process requests at the address "/movies/<int:mid>".
    """
    def get(self, mid: int):
        """
        The function takes as an argument the id of the movie as an integer and is designed to process
        a GET request at the address "/movies/<int:mid>", implements a search for the movie in the database,
        returns the found database object in the form of JSON.
        """
        movie = db.session.query(Movie).get(mid)
        return movie_schema.dump(movie)

    def put(self, mid: int):
        """
        The function takes as an argument the id of the movie as an integer and is designed to process
        a PUT request at the address "/movies/<int:mid>", implements the search and updating of movie data
        in the database, returns an updated database object in the form of JSON.
        """
        movie = db.session.query(Movie).get(mid)
        update_movie = request.json

        movie.id = update_movie["id"]
        movie.title = update_movie["title"]
        movie.description = update_movie["description"]
        movie.trailer = update_movie["trailer"]
        movie.year = update_movie["year"]
        movie.rating = update_movie["rating"]
        movie.genre_id = update_movie["genre_id"]
        movie.director_id = update_movie["director_id"]

        db.session.add(movie)
        db.session.commit()

        return movie_schema.dump(movie)

    def delete(self, mid: int):
        """
        The function takes as an argument the id of the movie as an integer and is designed to process
        a DELETE request at the address "/movies/<int:mid>", implements the search and deletion of the movie
        from the database, returns an empty string in the form of JSON.
        """
        movie = db.session.query(Movie).get(mid)

        db.session.delete(movie)
        db.session.commit()

        return ''


@director_ns.route('/')
class DirectorsView(Resource):
    """
    The Directory view class inherits from the Resource class of the flask_restx library and
    is a Base View class designed to process requests at the address "/directors/".
    """
    def get(self):
        """
        The function does not accept arguments and is designed to process GET requests at the address "/directors/",
        implements a search for all directors in the database, returns the found data in the form of JSON.
        """
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors)

    def post(self):
        """
        The function does not accept arguments and is designed to process a POST request to the address "/directors/",
        implements the creation of a new director and writing it to the database,
        returns the created database object in the form of JSON.
        """
        director = request.json

        director_dict = director_schema.load(director)
        new_director = Director(**director_dict)

        db.session.add(new_director)
        db.session.commit()

        return movie_schema.dump(new_director)


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    """
    The Directory View class inherits from the Resource class of the flask_restx library and
    is a Base View class designed to process requests at the address "/directors/<int:did>".
    """
    def get(self, did: int):
        """
        The function takes as an argument the ID of the director in the form of an integer and is intended
        for processing a GET request to the address "/directors/<in:did>", implements a search for
        a director in the database,returns the found database object in the form of JSON.
        """
        director = db.session.query(Director).get(did)
        return director_schema.dump(director)

    def put(self, did: int):
        """
        The function takes as an argument the ID of the director in the form of an integer and is intended
        for processing the PUT request to the address "/directors/<int:did>", implements the search and updating
        of data about the director returns an updated database object in the form of JSON in the database.
        """
        director = db.session.query(Director).get(did)
        director_update = request.json

        director.id = director_update["id"]
        director.name = director_update["name"]

        db.session.add(director)
        db.session.commit()

    def delete(self, did: int):
        """
        The function takes as an argument the id of the director as an integer and is designed to process
        a DELETE request at the address "/directors/<int:did>", implements the search and deletion
        of the director from the database, returns an empty string in the form of JSON.
        """
        director = db.session.query(Director).get(did)

        db.session.delete(director)
        db.session.commit()

        return ''


@genre_ns.route('/')
class GenresView(Resource):
    """
    The GenresView class inherits from the Resource class of the flask_restx library and
    is a Base View class designed to process requests at the address "/genres/".
    """
    def get(self):
        """
        The function does not accept arguments and is designed to process GET requests at the address "/genres/",
        implements a search for all genres in the database, returns the found data in the form of JSON.
        """
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres)

    def post(self):
        """
        The function does not accept arguments and is designed to process a POST request at the address "/genres/",
        implements the creation of a new genre and writing it to the database,
        returns the created database object in the form of JSON.
        """
        genre = request.json

        genre_dict = genre_schema.load(genre)
        new_genre = Director(**genre_dict)

        db.session.add(new_genre)
        db.session.commit()

        return genre_schema.dump(new_genre)


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    """
    The GenreView class inherits from the Resource class of the flask_restx library and
    is a Base View class designed to process requests at "/genres/<int:gid>".
    """
    def get(self, gid: int):
        """
        The function takes as an argument the genre identifier in the form of an integer and is intended
        for processing a GET request at the address "/genres/<in:gid>", implements a genre search
        in the database, returns the found database object in the form of JSON.
        """
        genre = db.session.query(Genre).get(gid)
        movies = db.session.query(Movie).filter(Movie.genre_id == gid).all()
        movies_list = []
        for item in movies:
            movies_list.append(item.title)
        res = {"id": genre.id, "name": genre.name, "movies": movies_list}
        return jsonify(res)

    def put(self, gid: int):
        """
        The function takes as an argument the genre identifier in the form of an integer and is intended
        for processing request PUT at "/genres/<int:gid>", implements the search and updating of genre data
        in the database, returns the updated database object in the form of JSON.
        """
        genre = db.session.query(Director).get(gid)
        genre_update = request.json

        genre.id = genre_update["id"]
        genre.name = genre_update["name"]

        db.session.add(genre)
        db.session.commit()

        return genre_schema.dump(genre)

    def delete(self, gid):
        """
        The function takes as an argument the genre id as an integer and is designed to process
        a DELETE request at the address "/genres/<int:gid>", implements the search and deletion
        of the genre from the database, returns an empty string in the form of JSON.
        """
        genre = db.session.query(Director).get(gid)

        db.session.delete(genre)
        db.session.commit()
        return ''


if __name__ == '__main__':
    app.run(debug=True)
