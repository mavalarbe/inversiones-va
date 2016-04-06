from google.appengine.ext import ndb

from core.models import BaseModel


class Transaccion(BaseModel):

    ruta = ndb.KeyProperty(required=True)
    tipo = ndb.StringProperty(required=True)
    tipo_gasto = ndb.StringProperty()
    observacion = ndb.StringProperty(required=True)
    usuario = ndb.StringProperty()

    valor = ndb.IntegerProperty(required=True)
