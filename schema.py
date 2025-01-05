import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from model import Movie as MovieModel, Genre as GenreModel, db
from sqlalchemy.orm import Session

# Movie and Genre Classes
class Movie(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel

class Genre(SQLAlchemyObjectType):
    class Meta:
        model = GenreModel

# Query Classes
class Query(graphene.ObjectType):
    movies = graphene.List(Movie)
    genres = graphene.List(Genre)
    movies_by_genre = graphene.List(Movie, genre_id=graphene.Int(required=True))
    genres_by_movie = graphene.List(Genre, movie_id=graphene.Int(required=True))

    # Resolver for movies
    def resolve_movies(self, info):
        return db.session.execute(db.select(MovieModel)).scalars().all()

    # Resolver for genres
    def resolve_genres(self, info):
        return db.session.execute(db.select(GenreModel)).scalars().all()

    # Resolver for movies by genre
    def resolve_movies_by_genre(self, info, genre_id):
        return db.session.execute(db.select(MovieModel).where(MovieModel.genre_id == genre_id)).scalars().all()

    # Resolver for genres by movie
    def resolve_genres_by_movie(self, info, movie_id):
        return db.session.execute(db.select(GenreModel).join(MovieModel).where(MovieModel.id == movie_id)).scalars().all()



# Movie Mutation Classes
class CreateMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        release_year = graphene.Int(required=True)
        director = graphene.String(required=True)
        genre_id = graphene.Int(required=True)

    movie = graphene.Field(Movie)

    def mutate(self, info, title, release_year, director, genre_id):
        genre = db.session.execute(db.select(GenreModel).where(GenreModel.id == genre_id)).scalar_one_or_none()
        if not genre:
            raise Exception(f"Genre with id {genre_id} does not exist.")

        try:
            new_movie = MovieModel(
                title=title,
                release_year=release_year,
                director=director,
                genre_id=genre_id,
            )
            db.session.add(new_movie)
            db.session.commit()

            return CreateMovie(movie=new_movie)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error creating movie: {e}")

class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        
    movie = graphene.Field(Movie)

    def mutate(self, info, id):
        with Session(db.engine) as session:
            with session.begin():
                movie = session.get(MovieModel, id)
                if not movie:
                    raise Exception(f"Movie with id {id} not found.")
                session.delete(movie)

            return DeleteMovie(movie=movie)
        
class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String(required=True)
        release_year = graphene.Int(required=True)
        director = graphene.String(required=True)
        genre_id = graphene.Int(required=True)

    movie = graphene.Field(Movie)

    def mutate(self, info, id, title, release_year, director, genre_id):
        with Session(db.engine) as session:
            with session.begin():
                movie = session.get(MovieModel, id)
                if not movie:
                    raise Exception(f"Movie with id {id} not found.")
                movie.title = title
                movie.release_year = release_year
                movie.director = director
                movie.genre_id = genre_id

            return UpdateMovie(movie=movie)

# Genre Mutation Classes
class CreateGenre(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    genre = graphene.Field(Genre)

    def mutate(self, info, name):
        try:
            with Session(db.engine) as session:
                with session.begin():
                    genre = GenreModel(name=name)
                    session.add(genre)

                return CreateGenre(genre=genre)
        except Exception as e:
            raise Exception(f"Error adding genre: {e}")
        
class DeleteGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        
    genre = graphene.Field(Genre)

    def mutate(self, info, id):
        with Session(db.engine) as session:
            with session.begin():
                genre = session.get(GenreModel, id)
                if not genre:
                    raise Exception(f"Genre with id {id} not found.")
                session.delete(genre)

            return DeleteGenre(genre=genre)
        
class UpdateGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    genre = graphene.Field(Genre)

    def mutate(self, info, id, name):
        with Session(db.engine) as session:
            with session.begin():
                genre = session.get(GenreModel, id)
                if not genre:
                    raise Exception(f"Genre with id {id} not found.")
                genre.name = name

            return UpdateGenre(genre=genre)
        
# Mutation Class
class Mutation(graphene.ObjectType):
    create_genre = CreateGenre.Field()
    delete_genre = DeleteGenre.Field()
    update_genre = UpdateGenre.Field()
    create_movie = CreateMovie.Field()
    delete_movie = DeleteMovie.Field()
    update_movie = UpdateMovie.Field()
