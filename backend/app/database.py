from sqlmodel import create_engine, Session

SQLITE_URL = "sqlite:///./dev.db"
engine = create_engine(SQLITE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
