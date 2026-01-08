from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    r = client.post('/users', json={'id':1,'name':'A','email':'a@test.com'})
    assert r.status_code == 200

def test_list_users():
    r = client.get('/users')
    assert r.status_code == 200