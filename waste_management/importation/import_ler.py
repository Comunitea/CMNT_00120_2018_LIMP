##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""Script para la importación del fichero xls de la LER"""

import sys
import xmlrpclib
import socket
import traceback
import xlrd


def ustr(text):
    """convierte las cadenas de sql server en iso-8859-1 a utf-8 que es la cofificación de postgresql"""
    return unicode(text, "iso-8859-15").encode("utf-8")


class CCImport:
    """
    Importa a OpenERP datos desde un excel.
    """

    def __init__(self, dbname, user, passwd, filename):
        """
        Inicializar las opciones por defecto y conectar con OpenERP
        """

        # -------------------------------------------------------------------------
        # --- WRAPPER XMLRPC OPENERP ----------------------------------------------
        # -------------------------------------------------------------------------

        self.url_template = "http://%s:%s/xmlrpc/%s"
        self.server = "localhost"
        self.port = 8069
        self.dbname = dbname
        self.user_name = user
        self.user_passwd = passwd
        self.user_id = 0
        self.filename = filename

        #
        # Conectamos con OpenERP
        #
        login_facade = xmlrpclib.ServerProxy(
            self.url_template % (self.server, self.port, "common")
        )
        self.user_id = login_facade.login(
            self.dbname, self.user_name, self.user_passwd
        )
        self.object_facade = xmlrpclib.ServerProxy(
            self.url_template % (self.server, self.port, "object")
        )

        #
        # Fichero Log de Excepciones
        #
        self.file = open("importation_log.txt", "w")

    def exception_handler(self, exception):
        """Manejador de Excepciones"""
        print "HANDLER: ", (exception)
        self.file.write("WARNING: %s\n\n\n" % repr(exception))
        return True

    def create(self, model, data, context={}):
        """
        Wrapper del método create.
        """
        try:
            res = self.object_facade.execute(
                self.dbname,
                self.user_id,
                self.user_passwd,
                model,
                "create",
                data,
                context,
            )

            if isinstance(res, list):
                res = res[0]

            return res
        except socket.error, err:
            raise Exception(u"Conexión rechazada: %s!" % err)
        except xmlrpclib.Fault, err:
            raise Exception(
                u"Error %s en create: %s" % (err.faultCode, err.faultString)
            )

    def search(self, model, query, context={}):
        """
        Wrapper del método search.
        """
        try:
            ids = self.object_facade.execute(
                self.dbname,
                self.user_id,
                self.user_passwd,
                model,
                "search",
                query,
                context,
            )
            return ids
        except socket.error, err:
            raise Exception(u"Conexión rechazada: %s!" % err)
        except xmlrpclib.Fault, err:
            raise Exception(
                u"Error %s en search: %s" % (err.faultCode, err.faultString)
            )

    def write(self, model, ids, field_values, context={}):
        """
        Wrapper del método write.
        """
        try:
            res = self.object_facade.execute(
                self.dbname,
                self.user_id,
                self.user_passwd,
                model,
                "write",
                ids,
                field_values,
                context,
            )
            return res
        except socket.error, err:
            raise Exception(u"Conexión rechazada: %s!" % err)
        except xmlrpclib.Fault, err:
            raise Exception(
                u"Error %s en write: %s" % (err.faultCode, err.faultString)
            )

    def process_data(self):
        """
        Importa la bbdd
        """
        print "Intentamos establecer conexion"
        try:
            wb = xlrd.open_workbook(self.filename, encoding_override="utf-8")

            sh = wb.sheet_by_index(0)

            for rownum in range(1, sh.nrows):
                rows = sh.row_values(rownum)
                print rows
                vals = {
                    "name": rows[1],
                    "code": rows[0].replace("*", ""),
                    "dangerous": "*" in rows[0] and True or False,
                }

                ids = self.search(
                    "waste.ler.code",
                    [
                        ("code", "=", vals["code"]),
                        ("name", "=", vals["name"]),
                        ("dangerous", "=", vals["dangerous"]),
                    ],
                )
                if ids:
                    self.write("waste.ler.code", ids[0], vals)
                    ids = ids[0]
                else:
                    ids = self.create("waste.ler.code", vals)

        except Exception, ex:
            print "Error al conectarse a las bbdd: ", (ex)
            sys.exit()

        # cerramos el fichero
        self.file.close()

        return True


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print u"Uso: %s <dbname> <user> <password> <file.xls>" % sys.argv[0]
    else:
        ENGINE = CCImport(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

        ENGINE.process_data()
