from google.appengine.ext import ndb

from core.controllers import BaseController
from core.helpers import RutaHelper
from core.helpers import CiudadHelper
from core.helpers import CajaHelper
from core.helpers import UsuarioHelper
from core.helpers import AdminHelper
from core.helpers import BaseHelper
from core.models import TimezoneOffset
import time
import logging


class AdminController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        rutas = RutaHelper.query_all(True)
        rutasEdit = RutaHelper.query_all(False)
        ciudades = CiudadHelper.query_all(True)
        cajas = CajaHelper.query_all(True)
        usuarios = UsuarioHelper.query_all(True)
        rutasUser = UsuarioHelper.query_all_rutas(None)
        TZO = TimezoneOffset.query().get()
        actual_time = BaseHelper.hora_actual_mexico()
        self.render("admin.html", rutas_admin=rutas, ciudades=ciudades,
                    cajas=cajas, usuarios=usuarios, usuario=None,
                    TZO=TZO, actual_time=actual_time, rutasUser=rutasUser, rutasEdit=rutasEdit)

    def post(self):
        self.is_logged()
        self.is_admin()
        key = self.request.get('key')
        if key:
            usuario = ndb.Key(urlsafe=key).get()
        rutas = RutaHelper.query_all(True)
        rutasEdit = RutaHelper.query_all(False)
        rutasUser = UsuarioHelper.query_all_rutas(None)
        ciudades = CiudadHelper.query_all(True)
        cajas = CajaHelper.query_all(True)
        usuarios = UsuarioHelper.query_all(True)
        TZO = TimezoneOffset.query().get()
        actual_time = BaseHelper.hora_actual_mexico()
        self.render("admin.html", rutas=rutas, ciudades=ciudades,
                    cajas=cajas, usuarios=usuarios, usuario=usuario,
                    TZO=TZO, actual_time=actual_time, rutasUser=rutasUser, rutasEdit=rutasEdit)


class CiudadController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        ciudades = CiudadHelper.query_all()
        self.render("ciudad.html", ciudades=ciudades)

    def post(self):
        self.is_logged()
        self.is_admin()
        nombre = self.request.get("nombre")
        alert = CiudadHelper.nuevo_registro(nombre)
        time.sleep(1)
        self.redirect("/admin")


class CajaController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        cajas = CajaHelper.query_all()
        self.render("caja.html", cajas=cajas)

    def post(self):
        self.is_logged()
        self.is_admin()
        nombre = self.request.get("nombre")
        alert = CajaHelper.nuevo_registro(nombre)
        time.sleep(1)
        self.redirect("/admin")


class RutaController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        rutas = RutaHelper.query_all()
        self.render("admin.html", rutas=rutas)

    def post(self):
        self.is_logged()
        self.is_admin()
        urlkey_ciudad = self.request.get("urlkey_ciudad")
        nombre = self.request.get("nombre")
        alert = RutaHelper.nuevo_registro(urlkey_ciudad, nombre)
        time.sleep(1)
        self.redirect("/admin")


class UsuarioController(BaseController):
    def get(self):
        self.is_logged()
        self.is_admin()
        usuarios = UsuarioHelper.query_all()
        self.render("usuario.html", usuarios=usuarios)

    def post(self):
        self.is_logged()
        self.is_admin()
        documento = int(self.request.get("documento")) if self.request.get("documento") else None
        nombres = self.request.get("nombres")
        apellidos = self.request.get("apellidos")
        usuario = self.request.get("usuario")
        clave = self.request.get("clave")
        role = self.request.get("role")
        rutas = self.request.get_all("chkRutas")
        seguir = True
        if rutas and len(rutas) > 0:
            if role != "supervisor" and role != "admin":
                if len(rutas) > 1:
                    seguir = False
                    alert = ["alert-success", "El rol seleccionado no puede tener mas de una ruta"]
        else:
            seguir = False
            alert = ["alert-success", "Debe seleccionar por lo menos una ruta"]
        if seguir:
            if UsuarioHelper.existe_documento(documento) and self.request.get("exist"):
                alert = UsuarioHelper.actualizar_registro(documento, nombres, apellidos, usuario,
                                                        clave, role, rutas)
            else:
                alert = UsuarioHelper.nuevo_registro(documento, nombres, apellidos, usuario,
                                                     clave, role, rutas)
        else:
            key = self.request.get('key')
            if key:
                usuario = ndb.Key(urlsafe=key).get()
            rutas = RutaHelper.query_all(True)
            rutasEdit = RutaHelper.query_all(False)
            ciudades = CiudadHelper.query_all(True)
            cajas = CajaHelper.query_all(True)
            usuarios = UsuarioHelper.query_all(True)
            rutasUser = UsuarioHelper.query_all_rutas(None)
            TZO = TimezoneOffset.query().get()
            actual_time = BaseHelper.hora_actual_mexico()
            self.render("admin.html", rutas_admin=rutas, ciudades=ciudades,
                        cajas=cajas, usuarios=usuarios, usuario=usuario, alert=alert,
                        TZO=TZO, actual_time=actual_time, rutasUser=rutasUser, rutasEdit=rutasEdit)
            return
        time.sleep(1)
        self.redirect("/admin")


class EnableController(BaseController):
    def post(self):
        self.is_logged()
        self.is_admin()
        key = self.request.get("key")
        url = self.request.get("url")
        if key:
            entity = ndb.Key(urlsafe=key).get()
            entity.activo = True
            if entity.key.kind() == "Cliente":
                for cr in entity.creditos:
                    c = cr.get()
                    c.activo = True
                    c.put()
            entity.put()
            time.sleep(1)
        if url:
            self.redirect(url)
            return
        self.redirect("/admin")


class DisableController(BaseController):
    def post(self):
        self.is_logged()
        self.is_admin()
        key = self.request.get("key")
        url = self.request.get("url")
        if key:
            entity = ndb.Key(urlsafe=key).get()
            entity.activo = False
            if entity.key.kind() == "Cliente":
                for cr in entity.creditos:
                    c = cr.get()
                    c.activo = False
                    c.put()
            entity.put()
            time.sleep(1)
        if url:
            self.redirect(url)
            return
        self.redirect("/admin")


class DeleteController(BaseController):
    def post(self):
        self.is_logged()
        self.is_admin()
        key = self.request.get("key")
        if key:
            if not AdminHelper().has_children(key):
                entity = ndb.Key(urlsafe=key).get()
                entity.key.delete()
                time.sleep(1)
                self.redirect("/admin")
            else:
                self.redirect("/admin?r=1")

class UpdateTimeZone(BaseController):
    def post(self):
        self.is_logged()
        self.is_admin()
        tzo = self.request.get("tzo")
        if tzo:
            TimezoneOffset.create(tzo)
        time.sleep(0.2)
        self.redirect("/admin")
