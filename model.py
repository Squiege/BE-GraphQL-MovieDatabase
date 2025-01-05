from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

db = SQLAlchemy(model_class=Base)


class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100))
    release_year: Mapped[int] = mapped_column(db.Integer)
    director: Mapped[str] = mapped_column(db.String(100))
    genre_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('genres.id'))

    genre = relationship('Genre', back_populates='movies')


class Genre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))

    movies = relationship('Movie', back_populates='genre')
