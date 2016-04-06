from google.appengine.ext import ndb
from google.appengine.api import images
from core.controllers import BaseController
from core.helpers import ClientHelper
from core.helpers import RutaHelper
from core.helpers import UsuarioHelper
from core.helpers import CreditHelper
import time
import logging


class ClientController(BaseController):
    def get(self):
        self.is_logged()
        urlkey_ruta = self.ruta_by_role()
        urlkey_cliente = self.request.get("urlkey_cliente")
        clientes = []
        r_actual = False
        creditos = []
        if urlkey_ruta:
            clientes = ClientHelper.query_by_ruta(urlkey_ruta)
            r_actual = ndb.Key(urlsafe=urlkey_ruta).get()
        if urlkey_cliente:
            creditos = CreditHelper.query_by_client(urlkey_cliente)
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("client.html", clientes=clientes, rutas=rutas, r_actual=r_actual, creditos=creditos,
                    rutaSupervisor=rutaSupervisor)
        return


class NewClientController(BaseController):
    def get(self):
        self.is_logged()
        rutas = RutaHelper.query_all()
        rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
        self.render("new_client.html", rutas=rutas, cliente=None, rutaSupervisor=rutaSupervisor)

    def post(self):
        key = self.request.get("key")
        if key:
            cliente = ndb.Key(urlsafe=key).get()
            rutas = RutaHelper.query_all()
            rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
            self.render("new_client.html", rutas=rutas, cliente=cliente, rutaSupervisor=rutaSupervisor)
            return
        else:
            documento = int(self.request.get("documento")) if self.request.get("documento") else None
            nombres = self.request.get("nombres")
            apellidos = self.request.get("apellidos")
            dir_casa = self.request.get("dir_casa")
            tel_casa = int(self.request.get("tel_casa")) if self.request.get("tel_casa") else None
            celular = int(self.request.get("celular")) if self.request.get("celular") else None
            nombre_est = self.request.get("nombre_est")
            dir_est = self.request.get("dir_est")
            imagen_documento = self.request.get("imagen_documento")
            if imagen_documento:
                imagen_documento = images.resize(imagen_documento, 150, 112)
            else:
                imagen_documento = None
            imagen_negocio = self.request.get("imagen_negocio")
            if imagen_negocio:
                imagen_negocio = images.resize(imagen_negocio, 150, 112)
            else:
                imagen_negocio = None
            if self.user.role == "admin" or self.user.role == "supervisor":
                ruta = self.request.get("urlkey_ruta")
            else:
                if self.user.ruta:
                    ruta = self.user.ruta.urlsafe()
                else:
                    ruta = UsuarioHelper.query_all_rutas(self.user.key)[0].ruta.urlsafe()
            key = self.request.get("client_urlkey")
            if key:
                cliente = ndb.Key(urlsafe=key)
                alert = ClientHelper.actualizar_registro(cliente, documento, 
                                                         ruta, nombres,
                                                         apellidos, dir_casa,
                                                         tel_casa, celular,
                                                         nombre_est, dir_est, 
                                                         imagen_documento, imagen_negocio)
            else:
                alert = ClientHelper.nuevo_registro(documento, 
                                                    ruta, nombres,
                                                    apellidos, dir_casa,
                                                    tel_casa, celular,
                                                    nombre_est, dir_est, 
                                                    imagen_documento, imagen_negocio)
            if alert[0] == "alert-danger":
                rutas = RutaHelper.query_all()
                rutaSupervisor = UsuarioHelper.query_all_rutas(self.user.key)
                self.render("new_client.html", rutas=rutas, cliente=None, 
                    rutaSupervisor=rutaSupervisor, alert=alert)
            else:
                time.sleep(1)
                self.redirect("/cliente?urlkey_ruta=" + ruta)

class ImagenDocumento(BaseController):
    def get(self):
        key = self.request.get("imgDocumento")
        cliente = ndb.Key(urlsafe=key).get()
        if cliente.imagen_documento:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(cliente.imagen_documento)
        else:
            self.response.out.write('No image')

class ImagenNegocio(BaseController):
    def get(self):
        key = self.request.get("imgNegocio")
        cliente = ndb.Key(urlsafe=key).get()
        if cliente.imagen_negocio:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(cliente.imagen_negocio)
        else:
            self.response.out.write('No image')
