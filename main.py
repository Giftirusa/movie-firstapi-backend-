import uvicorn
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.orm import Session as SQLAlchemySession
from fastapi.middleware.cors import CORSMiddleware

class Movie(SQLModel, table=True):
    __tablename__ = 'movie'
    __table_args__ = {'extend_existing': True}
    id: int = Field(default=None, primary_key=True)
    title: str
    rating: float
    year: int
    image:str
    genre: str
    description: str
    

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


@app.get("/movies")
def get_movies():
    with Session(engine) as session:
        movies = session.exec(select(Movie)).all()
        return movies
    
@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    with Session(engine) as session:
        movie = session.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie

@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie):
    with Session(engine) as session:
        session.add(movie)
        session.commit()
        session.refresh(movie)
        return movie

@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie_data: Movie):
    with Session(engine) as session:
        db_movie = session.get(Movie, movie_id)
        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        movie_data_dict = movie_data.dict(exclude_unset=True)
        for key, value in movie_data_dict.items():
            setattr(db_movie, key, value)
        session.add(db_movie)
        session.commit()
        session.refresh(db_movie)
        return db_movie
    
@app.patch("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie_data: Movie):
    with Session(engine) as session:
        db_movie = session.query(Movie).filter(Movie.id == movie_id).first()
        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        # Update only the fields that are provided in the request
        update_data = movie_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_movie, key, value)

        session.add(db_movie)
        session.commit()
        session.refresh(db_movie)
        return db_movie
    

@app.delete("/movies/{movie_id}")
def remove_movie(movie_id: int):
    with Session(engine) as session:
        movie = session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        session.delete(movie)
        session.commit()
        return {"ok": True}

if __name__ == "__main__":
    create_db_and_tables()
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)