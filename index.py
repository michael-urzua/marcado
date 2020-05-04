# @TODO:Agregar SHEBANG!!
# /srv/proyecto/entorno_virtual/bin/python
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash
from datetime import datetime, date, time, timedelta
from pytz import timezone as pytztimezone
import pytz
import requests
from data import   consulta_user_compania, consulta_user, consulta_user_perfiles, consulta_perfil, insertar_registro_perfil, \
    actualizar_public_cliente, actualizar_rtrim, actualiza_perfil,consulta_objetivo,consulta_cache,borrar_cache,\
    consulta_cliente,consulta_zona,inserta_marcadoDatos,inserta_bitacora

from utils.get_token import get
from utils.globals import url2, url_chek
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.secret_key = 'many random bytes'


@app.route("/", methods=["GET", "POST"])
def index():

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()
    return redirect(url_for('index'))


@app.route('/acceso', methods=["GET", "POST"])
def acceso():

    usuario = request.form['email']
    clave = request.form['password']

    # VA A VALIDAR LA SESION GET_TOKEN.PY
    r = get.get_api(usuario, clave)

    if r == False:
        flash("Problemas en la conexion API ", "danger")
        return redirect(url_for('index'))

        # DESDE AQUI PARA ARRIBA ES LO TUYO ABAJO  SON COSAS DE VARIABLES NOMAS
        # DESPUES SIGUE Y VIEN session_token(var_session):

    status = r["status"]

    if status == 0:

        token = r["data"]["token"]
        cliente_usuario_id = r["data"]["cliente_usuario_id"]
        cliente_id = r["data"]["cliente_id"]

        # VARIABLES SESSION -.---------
        session['cliente_usuario_id'] = cliente_usuario_id
        session['cliente_id'] = cliente_id
        session['token'] = token

        cursor_perfil = consulta_perfil.select_perfil()
        perfil_name = cursor_perfil.fetchall()
        perfil_name_vacio=len(perfil_name)

        session["perfil_nombre"] = perfil_name
        if perfil_name_vacio == 0:
            flash("Usuario no registrado ", "danger")
            return redirect(url_for('index'))

        return redirect(url_for('inicio'))

    else:
        flash("Usuario y/o Clave son invalidos ", "danger")
        return redirect(url_for('index'))

def session_token(var_session):
    # AQUI VALIDA QUE EL TOKEN SIEMPRE SEA TRUE CADA VEZ Q EJECUTA UNA ACCION COMO EN LA RUTA INICIO
    validar_session = requests.get(
        url_chek + url2 + var_session['token'], allow_redirects=False, verify=False).content

    return validar_session


@app.route('/inicio')
def inicio():

    if len(session) == 0:
        return redirect(url_for('index'))

        # VALIDA TOKEN
    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    if session["perfil_nombre"][0][0] == 'administrador':
        return redirect(url_for('mantenedor'))

    now = datetime.now()
    yesterday = now.date() - timedelta(days=1)

    cursor3 = consulta_user_compania.select_user_compania()
    cliente_usuario = cursor3.fetchall()
    session['cliente_usuario'] = cliente_usuario
    nombre = session['cliente_usuario'][0][0]
    cliente = session['cliente_usuario'][0][1]

    newDict = dict(session)
    if newDict["perfil_nombre"]:

        if session["perfil_nombre"][0][1] == 'si':

            if session["perfil_nombre"][0][0] == 'lectura':

                return render_template("marcado.html", usuario=nombre,compania=cliente)

        elif session["perfil_nombre"][0][1] == 'no':
            flash("NO TIENE PERFIL ACTIVO", "danger")
            return redirect(url_for('index'))
    else:
        flash("NO SE ENCUENTRA REGISTRADO", "danger")
        return redirect(url_for('index'))


@app.route("/consultar", methods=["GET", "POST"])
def consultar_bco_chile():
    # from operator import itemgetter

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    id_objetivo = request.form['id_objetivo']
    session['id_objetivo'] = id_objetivo
    obje = session['id_objetivo']


    cursor = consulta_objetivo.select_objetivo(id_objetivo)
    objetivo = cursor.fetchall()
    q_obejtivo = len(objetivo)

    nombre = session['cliente_usuario'][0][0]
    cliente = session['cliente_usuario'][0][1]

    if q_obejtivo > 0:
        return render_template("marcado.html", usuario=nombre,compania=cliente,cantidad = q_obejtivo, obj = id_objetivo, isp = objetivo )
    else:
        flash("ISP SIN RESPUESTA", "danger")
        return render_template("marcado.html", usuario=nombre,compania=cliente,cantidad = q_obejtivo)

@app.route("/mantenedor", methods=["GET", "POST"])
def mantenedor():

    if session["perfil_nombre"][0][0] == 'administrador' :

        if len(session) == 0:
            return redirect(url_for('index'))

        variable = session_token(session)
        if variable == 'False':
            return render_template("login.html")

        cursor3 = consulta_user_compania.select_user_compania()
        cliente_usuario = cursor3.fetchall()
        nombre = cliente_usuario[0][0]
        cliente = cliente_usuario[0][1]

        # LISTA DE USUARIOS ATENTUS
        cursor_user = consulta_user.select_user()
        user_add = cursor_user.fetchall()

        # LISTA USUARIOS YA REGISTRADOS
        cursor_user_perfil = consulta_user_perfiles.select_user_perfil()
        user_show = cursor_user_perfil.fetchall()

        return render_template("mantenedor.html", usuario=nombre, compania=cliente, usuario_add=user_add, mostrar_user=user_show)
    else:
        return redirect(url_for('index'))



@app.route("/actualizar_perfil", methods=['POST'])
def actualizar_perfil():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    nombre_perfil = request.form['nombre_perfil']
    activo = request.form['activo']
    # id_banco = request.form['id_banco']
    id_perfil_usuario = request.form['id_perfil_usuario']

    cursor = actualiza_perfil.update_perfil(
        nombre_perfil, activo, id_perfil_usuario)

    return redirect(url_for('mantenedor'))


@app.route("/insertar_perfil", methods=['POST'])
def insertar_perfil():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    usr_perfil = request.form.getlist('usr_perfil')
    listUsr = []
    for elem in usr_perfil:
        dictUsr = {}
        dictUsr["id_usuario_perfil"] = (str(elem).split("-")[0])
        dictUsr["nombre_usuario_perfil"] = (str(elem).split("-")[1])
        listUsr.append(dictUsr)

    perfil_usr_add = request.form['perfil_usr_add']
    activo_usr_add = request.form['activo_usr_add']

    cursor = insertar_registro_perfil.insert_perfil(
        listUsr, perfil_usr_add, activo_usr_add)
    if cursor != False:
        cursor2 = actualizar_public_cliente.update_public_cliente(listUsr)
        cursor3 = actualizar_rtrim.update_rtrim()

    return redirect(url_for('mantenedor'))


def toUTC(tz, datetime):
    return tz.normalize(tz.localize(datetime)).astimezone(pytz.utc)

@app.route("/insertar_marcado", methods=['POST'])
def insertar_marcado():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    objetivo = request.form['objetivo']
    nodo = request.form.getlist('nodo')

    listUsr = []
    for elem in nodo:
        dictUsr = {}
        dictUsr["nodo"] ="{"+(str(elem).split("-")[0])+"}"
        listUsr.append(dictUsr)

    print"listUsr",listUsr

    fecha_inicio = request.form['fecha_inicio']
    fecha_termino = request.form['fecha_termino']
    motivo = request.form['motivo']
    autorizacion = request.form['autorizacion']

    fecha_inicial = fecha_inicio.split(" ")[0]

    cursor1 = consulta_cliente.select_cliente(objetivo)
    cliente = cursor1.fetchone()
    session['cliente'] = cliente
    cliente_id = session['cliente'][0]

    cursor2 = consulta_zona.select_zona(cliente_id)
    zona = cursor2.fetchone()
    session['zona'] = zona
    zona = session['zona'][0]

    hlocal_inicio = toUTC(pytztimezone(zona), datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S' ))
    hlocal_termino = toUTC(pytztimezone(zona), datetime.strptime(fecha_termino, '%Y-%m-%d %H:%M:%S' ))


    # INSERTAR MARCADO DE DATOS
    cursor2 = inserta_marcadoDatos.insert_marcadoDatos(
        objetivo,listUsr,hlocal_inicio,hlocal_termino,motivo,autorizacion)

    if cursor2 != False:
        # CONSULTAR CACHE
        cursor3 = consulta_cache.select_cache(objetivo,fecha_inicial)
        cache = cursor3.fetchall()
        q_cache = len(cache)

        print"q_cacheeeee",q_cache
        # # # BORRAR cache.cache_nivel1
        if q_cache > 0:
            cursor3 = borrar_cache.delete_cache(objetivo,fecha_inicial)
            flash("MARCADO DE DATOS REALIZADOS Y SE ELIMINA CACHE ", "success")
        else:
            flash("MARCADO DE DATOS REALIZADOS ", "success")
            flash("NO ENCONTRO DATOS DE CACHE PARA BORRAR ", "danger")

    else:
        flash("NO SE REALIZA MARCADO DE DATOS ", "danger")

    return redirect(url_for('inicio'))

@app.route("/insertar_bitacora", methods=['POST'])
def insertar_bitacora():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    fecha_entrega = request.form['fecha_entrega']
    desarrollador = request.form['desarrollador']
    nombre_proyecto = request.form['nombre_proyecto']
    documentos_referencia = request.form['documentos_referencia']
    tipo = request.form['tipo']

    cursor = inserta_bitacora.insert_bitacora(fecha_entrega,desarrollador,
      nombre_proyecto, documentos_referencia,  tipo)

    return redirect(url_for('inicio'))



if(__name__ == "__main__"):
    #app.run(debug = True)
    app.run("0.0.0.0", 5000)
