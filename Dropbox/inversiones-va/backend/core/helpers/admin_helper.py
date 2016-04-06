# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from core.helpers import BaseHelper
from core.models import Ruta
from core.models import Ciudad
from core.models import Caja
from core.models import User
from core.models import Abono
from core.models import Cliente
from core.models import Credito
from core.models import Transaccion
from core.models import UserRuta


class AdminHelper(BaseHelper):
    @classmethod
    def has_children(cls, key):
        key = ndb.Key(urlsafe=key)
        kind = key.kind()
        children = 0
        if kind == 'Ciudad':
            children += Ruta.query(Ruta.ciudad == key).count()
        elif kind == 'Ruta':
            children += Abono.query(Abono.ruta == key).count()
            children += Cliente.query(Cliente.ruta == key).count()
            children += Credito.query(Credito.ruta == key).count()
            children += Transaccion.query(Transaccion.ruta == key).count()
            children += User.query(User.ruta == key).count()
        elif kind == 'Cliente':
            pass
        elif kind == 'Credito':
            pass
        return True if children > 0 else False

    @classmethod
    def get_alert(cls, code=None):
        if code:
            alert = {
                1: ['alert-danger', (u'mensaje')],
                #2: ['alert-success', mensaje],
                #3: ['alert-info', mensaje],
                #4: ['alert-warning', mensaje]
                }
            return alert[int(code)] if int(code) in alert else None
        return None

class RutaHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            rutas = Ruta.query().fetch()
        else:
            rutas = Ruta.query(Ruta.activo == True).fetch()
        return rutas

    @classmethod
    def existe(cls, urlkey):
        if urlkey:
            ruta_entity = ndb.Key(urlsafe=urlkey).get()
            if ruta_entity:
                return ruta_entity
            else:
                return False
        else:
            return False

    @classmethod
    def existe_nombre(cls, nombre):
        if nombre:
            if Ruta.query(Ruta.nombre == nombre).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def validar_nueva(cls, urlkey_ciudad, nombre):
        ruta_ciudad = CiudadHelper.existe(urlkey_ciudad)
        existe_nombre = cls.existe_nombre(nombre)
        if ruta_ciudad and not existe_nombre:
            return [ruta_ciudad, nombre]
        else:
            return False

    @classmethod
    def nuevo_registro(cls, urlkey_ciudad, nombre):
        ruta_params = cls.validar_nueva(urlkey_ciudad, nombre)
        if ruta_params:
            nueva_ruta = Ruta(ciudad=ruta_params[0].key,
                              nombre=ruta_params[1],
                              saldo=0,
                              activo=True)
            nueva_ruta.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo realizar el registro"]

    @classmethod
    def generar_entrada(cls, ruta, valor):
        ruta.saldo += valor
        ruta.put()
        return

    @classmethod
    def generar_salida(cls, ruta, valor):
        ruta.saldo -= valor
        ruta.put()
        return

    @classmethod
    def get_saldo(cls, ruta):
        saldo = ruta.saldo
        return saldo

class CiudadHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            ciudades = Ciudad.query().fetch()
        else:
            ciudades = Ciudad.query(Ciudad.activo == True).fetch()
        return ciudades

    @classmethod
    def nuevo_registro(cls, nombre):
        if not cls.existe_nombre(nombre):
            nueva_ciudad = Ciudad(nombre=nombre)
            nueva_ciudad.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "La ciudad ya existe"]

    @classmethod
    def existe(cls, urlkey):
        if urlkey:
            ciudad_entity = ndb.Key(urlsafe=urlkey).get()
            if ciudad_entity:
                return ciudad_entity
            else:
                return False
        else:
            return False

    @classmethod
    def existe_nombre(cls, nombre):
        if nombre:
            if Ciudad.query(Ciudad.nombre == nombre).fetch():
                return True
            else:
                return False
        else:
            return False


class CajaHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            cajas = Caja.query().fetch()
        else:
            cajas = Caja.query(Caja.activo == True).fetch()
        return cajas

    @classmethod
    def nuevo_registro(cls, nombre):
        if not cls.existe_nombre(nombre):
            nueva_caja = Caja(nombre=nombre)
            nueva_caja.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "La Caja ya existe"]

    @classmethod
    def existe(cls, urlkey):
        if urlkey:
            caja_entity = ndb.Key(urlsafe=urlkey).get()
            if caja_entity:
                return caja_entity
            else:
                return False
        else:
            return False

    @classmethod
    def existe_nombre(cls, nombre):
        if nombre:
            if Caja.query(Caja.nombre == nombre).fetch():
                return True
            else:
                return False
        else:
            return False


class UsuarioHelper(BaseHelper):

    @classmethod
    def query_all(cls, admin=False):
        if admin:
            usuarios = User.query().fetch()
        else:
            usuarios = User.query(User.activo == True).fetch()
        return usuarios

    @classmethod
    def query_all_rutas(cls, usuario_key):
        if usuario_key:
            return UserRuta.query(UserRuta.usuario == usuario_key).fetch()
        else:
            return UserRuta.query().fetch()

    @classmethod
    def nuevo_registro(cls, documento, nombres, apellidos,
                       usuario, clave, role, rutas):
        existe_documento = cls.existe_documento(documento)
        existe_usuario = cls.existe_usuario(usuario)

        if not existe_documento and not existe_usuario and usuario and clave:
            u = User.register_ruta(documento, nombres, apellidos,
                                  usuario, clave, role)
            u.put()
            if rutas:
                for rut in rutas:
                    ruta_key = ndb.Key(urlsafe=rut)
                    rta = ruta_key.get()
                    nueva_ruta = UserRuta(ruta=rta.key, usuario=u.key)
                    nueva_ruta.put()
            return ["alert-success", "El registro ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar el registro"]

    @classmethod
    def existe_documento(cls, documento):
        if documento:
            if User.query(User.documento == documento).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def existe_usuario(cls, usuario):
        if usuario:
            if User.query(User.usuario == usuario).fetch():
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def existe_userRuta(cls, urlkey):
        if urlkey:
            userRuta_entity = ndb.Key(urlsafe=urlkey).get()
            if userRuta_entity:
                return userRuta_entity
            else:
                return None
        else:
            return None

    @classmethod
    def actualizar_registro(cls, documento, nombres, apellidos,
                            usuario, clave, role, rutas):
        existe_documento = cls.existe_documento(documento)
        if existe_documento and usuario:
            u = User.query(User.documento == documento).get()
            u.nombres = nombres
            u.apellidos = apellidos
            if clave:
                u.clave_hash = User.make_pw_hash(usuario, clave)
            elif u.usuario != usuario and not cls.existe_usuario(usuario) and clave:
                u.clave_hash = User.make_pw_hash(usuario, clave)
                u.usuario = usuario
            u.role = role
            u.put()
            rutasEliminar = cls.query_all_rutas(u.key)
            if rutasEliminar:
                for r in rutasEliminar:
                    if r.usuario.get().usuario == u.usuario:
                        r.key.delete()
            if rutas:
                for rut in rutas:
                    ruta_key = ndb.Key(urlsafe=rut)
                    rta = ruta_key.get()
                    nueva_ruta = UserRuta(ruta=rta.key, usuario=u.key)
                    nueva_ruta.put()
            return ["alert-success", "La actualización ha sido exitoso"]
        else:
            return ["alert-danger", "No se pudo completar la actualización"]
