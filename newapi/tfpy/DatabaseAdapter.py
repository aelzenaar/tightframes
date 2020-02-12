from pymongo import MongoClient
from copy import deepcopy

class DatabaseAdapter(object):
  """Encapsulate the database API.

    This class is a context manager that interfaces with a database layer, enabling
    storage and retrieval of spherical designs.

  """
  def __init__(self, dbname = 'tfpy', collection = 'designs'):
    self._client = None
    self._db = None
    self._designs = None

    self._dbname = dbname
    self._collection = collection
    pass

  def __enter__(self):
    self._client = MongoClient()
    self._db = self._client[self._dbname]
    self._designs = self._db[self._collection]
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    pass

  def search(self, **kwargs):
    prototype_designs = set({})

    def set_theoretic_product(st, key, values):
      scratch = set()
      for v in values:
        for s in st:
          t = copy.deepcopy(s)
          t[key] = v
          scratch.add(t)
      return scratch

    for key in ['d','n','t']:
      if key in kwargs:
        prototype_designs = set_theoretic_product(prototype_designs, key, kwargs[key])
    for key in ['field', 'design_type']:
      if key in kwargs:
        prototype_designs = set_theoretic_product(prototype_designs, key, [v.value for v in kwargs[key]])

    return self._designs.find(prototype_designs)

  def insert(self, design):
    return self._designs.insert_one(design.to_dict()).inserted_id

  def update(self, dbid, design):
    return self._designs.replace_one({"_id": dbid},design.to_dict())

  def delete(self, dbid):
    return self._designs.delete_one({"_id": dbid})
