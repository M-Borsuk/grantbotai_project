from app.db import Mongo


class DummyCollection:
    def find(self, query):
        return [{"id": "testdoc", "company_id": "123", "text": "X"}]

    def insert_one(self, doc):
        self.doc = doc
        return True


def test_mongo_collections(monkeypatch):
    mongo = Mongo()
    monkeypatch.setattr(type(mongo), "documents", property(lambda self: DummyCollection()))

    docs = mongo.documents.find({})
    assert isinstance(docs, list)
    assert "id" in docs[0]

    monkeypatch.setattr(type(mongo), "history", property(lambda self: DummyCollection()))
    res = mongo.history.insert_one({"foo": "bar"})
    assert res
