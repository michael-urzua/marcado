# @TODO:Agregar SHEBANG!!
# -*- coding: utf-8 -*-
# /srv/proyecto/entorno_virtual/bin/python
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash
from datetime import datetime, date, time, timedelta
from pytz import timezone as pytztimezone
import pytz
import requests
import pygal
from pygal.style import DefaultStyle

from data import   consulta_user_compania, consulta_user, consulta_user_perfiles, consulta_perfil, insertar_registro_perfil, \
     actualiza_perfil,consulta_objetivo,consulta_cache,borrar_cache,consulta_experiracion,consulta_cliente,consulta_zona,\
     inserta_marcadoDatos,inserta_bitacora,consulta_grafico,consulta_grafico_motivo,consulta_grafico_fechainicial,consulta_grafico_nodos,\
     consulta_nodos,consulta_grafico_marcado

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


@app.route('/inicio', methods=["GET", "POST"])
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

            if session["perfil_nombre"][0][0] == 'escritura':

                return render_template("marcado.html", usuario=nombre,compania=cliente)

        elif session["perfil_nombre"][0][1] == 'no':
            flash("NO TIENE PERFIL ACTIVO", "danger")
            return redirect(url_for('index'))
    else:
        flash("NO SE ENCUENTRA REGISTRADO", "danger")
        return redirect(url_for('index'))


@app.route("/consultar", methods=["GET", "POST"])
def consultar_bco_chile():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    id_objetivo = request.form['id_objetivo']
    session['id_objetivo'] = id_objetivo
    obje = session['id_objetivo']

    nombre = session['cliente_usuario'][0][0]
    cliente = session['cliente_usuario'][0][1]

    cursor = consulta_experiracion.select_experiracion(id_objetivo)
    objetivo = cursor.fetchall()
    nom_objetivo = objetivo[0][1]
    q_existe = len(objetivo)
    if q_existe > 0:

        cursor1 = consulta_objetivo.select_objetivo(id_objetivo)
        objetivo1 = cursor1.fetchall()
        q_obejtivo = len(objetivo1)

        if q_obejtivo > 0:
            return render_template("marcado.html", usuario=nombre,compania=cliente,cantidad = q_obejtivo,
                                    obj = id_objetivo, isp = objetivo1, nom_objetivo = nom_objetivo)
        else:
            flash("OBJETIVO SIN NODO", "danger")
            return render_template("marcado.html", usuario=nombre,compania=cliente,cantidad = q_obejtivo)
    else:
        flash("OBJETIVO EXPIRADO", "danger")
        return render_template("marcado.html", usuario=nombre,compania=cliente)

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
        flash("DATOS INGRESADOS CON EXITO", "success")
        return redirect(url_for('mantenedor'))
    else:

        flash("ERROR AL INGRESAR DATOS", "danger")
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
    nodo_final = ""
    for elem in nodo:
        nodo_final2 =(str(elem).split("-")[0])
        nodo_final = nodo_final + "," +nodo_final2
        nodos = "{"+ nodo_final[1:120] + "}"

    fecha_inicio = request.form['fecha_inicio']
    fecha_termino = request.form['fecha_termino']

    fecha_inicial = fecha_inicio.split(" ")[0]


    if fecha_inicio == fecha_termino:
        flash("HA INGRESADO HORARIOS IGUALES, CAMBIAR RANGO", "danger")
        return redirect(url_for('inicio'))


    if fecha_inicio > fecha_termino:
        flash("HA INGRESADO UNA FECHA DE TERMINO MENOR A LA FECHA DE INICIO, CAMBIAR RANGO", "danger")
        return redirect(url_for('inicio'))

    motivo = request.form['motivo']
    fecha_entrega = request.form['fecha_entrega']
    nombre_proyecto = request.form['nombre_proyecto']
    observaciones = request.form['observaciones']

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
        objetivo,nodos,hlocal_inicio,hlocal_termino,motivo)

    if cursor2 != False:
        # CONSULTAR CACHE
        cursor3 = consulta_cache.select_cache(objetivo,fecha_inicial)
        cache = cursor3.fetchall()
        q_cache = len(cache)

        cursor = inserta_bitacora.insert_bitacora(fecha_entrega,nombre_proyecto,observaciones)
        if cursor == False:
            flash("ERROR INSERT BITACORA", "danger")
        # BORRAR cache.cache_nivel1
        if q_cache > 0:
            cursor3 = borrar_cache.delete_cache(objetivo,fecha_inicial)
            flash("MARCADO DE DATOS REALIZADOS Y SE ELIMINA CACHE ", "success")
        else:
            flash("MARCADO DE DATOS REALIZADOS ", "success")
            flash("NO ENCONTRO DATOS DE CACHE PARA BORRAR ", "danger")

    else:
        flash(" OCURRIÓ UN ERROR AL INGRESAR EL MARCADO, FAVOR REVISAR QUE \
        PERIODO INGRESADO NO SE SUPERPONGA CON OTRO ", "danger")

    return redirect(url_for('inicio'))

#
#
#
#

@app.route("/inicio_graficos", methods=["GET", "POST"])
def inicio_graficos():

    if len(session) == 0:
        return redirect(url_for('index'))

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    cursor = consulta_user_compania.select_user_compania()
    cliente_usuario = cursor.fetchall()
    nombre = cliente_usuario[0][0]
    cliente = cliente_usuario[0][1]

    cursor = consulta_grafico_fechainicial.select_grafico_fechainicial()
    grafico_fechainicial = cursor.fetchall()

    fecha_inicial = grafico_fechainicial[0]
    fecha_final = grafico_fechainicial[1]
    # mes = str(grafico_fechainicial[2])

    cursor1 = consulta_grafico.select_grafico(fecha_inicial,fecha_final)
    cliente_grafico = cursor1.fetchall()

    chart = pygal.Bar(print_values=True, style=DefaultStyle(
                  value_font_family='googlefont:Raleway',
                  value_font_size=25,
                  value_colors=('white',)))

    chart.title = 'OBJETIVOS CON MAS MARCADOS'

    for value in cliente_grafico:
        chart.add(value[0],[value[1]])

    chart_data = chart.render_data_uri()

    # --------------------------

    cursor2 = consulta_grafico_motivo.select_grafico_motivo(fecha_inicial,fecha_final)
    cliente_grafico_motivo = cursor2.fetchall()

    chart = pygal.Bar(print_values=True, print_zeroes=False)
    chart.title = 'MOTIVOS MAS RECURRENTES POR OBJETIVOS'
    for value_motivo in cliente_grafico_motivo:
        chart.add(value_motivo[0],[value_motivo[1]])

    chart_data_motivo = chart.render_data_uri()

    # ------------

    cursor3 = consulta_grafico_nodos.select_grafico_nodos(fecha_inicial,fecha_final)
    cliente_grafico_nodos = cursor3.fetchall()

    chart = pygal.Bar(print_values=True, print_zeroes=False)
    chart.title = 'NODOS MAS RECURRENTES POR OBJETIVOS'
    for value_motivo in cliente_grafico_nodos:
        chart.add(value_motivo[0],[value_motivo[1]])

    chart_data_nodos = chart.render_data_uri()

    # ------------
    cursor4 = consulta_nodos.select_nodos()
    nodos = cursor4.fetchall()

    # ------------
    cursor5 = consulta_grafico_marcado.select_grafico_marcado(fecha_inicial,fecha_final)
    marcado = cursor5.fetchall()

    pie_chart = pygal.Pie(inner_radius=.4 )
    pie_chart.title = 'TIPO DE MARCADO (EN %)'

    for value_marcado in marcado:
        pie_chart.add(str(value_marcado[0]),value_marcado[1])

    chart_data_marcado = pie_chart.render_data_uri()

    return render_template("graficos.html", usuario=nombre, compania=cliente, chart_data = chart_data,
                            chart_data_motivo = chart_data_motivo, chart_data_nodos = chart_data_nodos,nodos=nodos,
                            chart_data_marcado=chart_data_marcado)



@app.route("/consultar_grafico", methods=["GET", "POST"])
def consultar_grafico():

    if len(session) == 0:
        return redirect(url_for('index'))

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    cursor = consulta_user_compania.select_user_compania()
    cliente_usuario = cursor.fetchall()
    nombre = cliente_usuario[0][0]
    cliente = cliente_usuario[0][1]

    mes_grafico = request.form['mes_grafico']
    if mes_grafico == '0':
        flash("SELECCIONE UNA FECHA ", "danger")
        return redirect(url_for('inicio_graficos'))

    fecha_inicial = mes_grafico.split("/")[0]
    fecha_final = mes_grafico.split("/")[1]
    mes = mes_grafico.split("/")[2]

    cursor1 = consulta_grafico.select_grafico(fecha_inicial,fecha_final)
    cliente_grafico = cursor1.fetchall()

    chart = pygal.Bar(print_values=True, style=DefaultStyle(
                  value_font_family='googlefont:Raleway',
                  value_font_size=25,
                  value_colors=('white',)))

    chart.title = 'OBJETIVOS CON MAS MARCADOS EN'+' '+mes

    for value in cliente_grafico:
        chart.add(value[0],[value[1]])

    chart_data = chart.render_data_uri()

    cursor2 = consulta_grafico_motivo.select_grafico_motivo(fecha_inicial,fecha_final)
    cliente_grafico_motivo = cursor2.fetchall()

    chart = pygal.Bar(print_values=True, print_zeroes=False)
    chart.title = 'MOTIVOS MAS RECURRENTES POR OBJETIVOS EN'+' '+mes
    for value_motivo in cliente_grafico_motivo:
        chart.add(value_motivo[0],[value_motivo[1]])

    chart_data_motivo = chart.render_data_uri()

    # ------------

    cursor3 = consulta_grafico_nodos.select_grafico_nodos(fecha_inicial,fecha_final)
    cliente_grafico_nodos = cursor3.fetchall()

    chart = pygal.Bar(print_values=True, print_zeroes=False)
    chart.title = 'NODOS MAS RECURRENTES POR OBJETIVOS EN'+' '+mes
    for value_motivo in cliente_grafico_nodos:
        chart.add(value_motivo[0],[value_motivo[1]])

    chart_data_nodos = chart.render_data_uri()

    # ------------
    cursor4 = consulta_nodos.select_nodos()
    nodos = cursor4.fetchall()

    # ------------
    cursor5 = consulta_grafico_marcado.select_grafico_marcado(fecha_inicial,fecha_final)
    marcado = cursor5.fetchall()

    pie_chart = pygal.Pie(inner_radius=.4 )
    pie_chart.title = 'TIPO DE MARCADOS EN'+' '+mes+ ' (EN %)'
    for value_marcado in marcado:
        pie_chart.add(str(value_marcado[0]),value_marcado[1])

    chart_data_marcado = pie_chart.render_data_uri()

    return render_template("graficos.html", usuario=nombre, compania=cliente, chart_data = chart_data,
                            chart_data_motivo = chart_data_motivo, chart_data_nodos = chart_data_nodos,nodos=nodos,
                            chart_data_marcado=chart_data_marcado)


if(__name__ == "__main__"):
    #app.run(debug = True)
    # app.run("0.0.0.0", 5000)
    app.run("0.0.0.0", 5002)
