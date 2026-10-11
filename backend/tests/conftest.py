import os, tempfile
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client():
    handle,path=tempfile.mkstemp(suffix=".db"); os.close(handle)
    os.environ["DEVNOTES_DB"]=path
    from app.database import Base, engine
    from app.main import app
    Base.metadata.create_all(engine)
    with TestClient(app) as c: yield c
    engine.dispose(); os.unlink(path); os.environ.pop("DEVNOTES_DB",None)
