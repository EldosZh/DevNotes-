def test_note_lifecycle_and_search(client):
    folder=client.post('/api/folders',json={'name':'Python'}).json()
    n=client.post('/api/notes',json={'title':'SQLAlchemy guide','content':'SQLite sessions','folder_id':folder['id'],'tags':['backend'],'pinned':True})
    assert n.status_code==201 and n.json()['tags'][0]['name']=='backend'
    assert client.get('/api/notes?q=SQLite').json()[0]['id']==n.json()['id']
    assert client.get('/api/notes',params={'folder_id':folder['id']}).status_code==200
    assert client.patch(f"/api/notes/{n.json()['id']}",json={'archived':True}).json()['archived'] is True
    assert client.get('/api/notes').json()==[]
    assert client.get('/api/notes',params={'archived':True}).json()
    assert client.delete(f"/api/notes/{n.json()['id']}").status_code==204
    assert client.get(f"/api/notes/{n.json()['id']}").status_code==404
def test_health_and_duplicate_folder(client):
    assert client.get('/api/health').json()=={'status':'ok'}
    assert client.post('/api/folders',json={'name':'Ideas'}).status_code==201
    assert client.post('/api/folders',json={'name':'Ideas'}).status_code==409
