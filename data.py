from config import conexion
from flask import Flask, session
from datetime import datetime, date, time, timedelta
import psycopg2
import psycopg2.extras
from flask import flash
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class consulta_experiracion:
    @staticmethod
    def select_experiracion(id_objetivo):
        try:

            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                cliente_usuario_id,concat(o.objetivo_id, ' - ' ,o.nombre)
                                FROM cliente_usuario cu, cliente_mapa_cliente_objetivo co, objetivo o
                                WHERE cu.cliente_id = co.cliente_id
                                AND o.objetivo_id = co.objetivo_id
                                AND co.objetivo_id = %s
                                AND (o.fecha_expiracion >= NOW() OR o.fecha_expiracion IS NULL)
                                LIMIT 1""", (id_objetivo,))
            return cursor
        except:
            return False


class consulta_objetivo:
    @staticmethod
    def select_objetivo(id_objetivo):
        try:
            cursor = conexion.conect_post()
            cursor.execute(""" SELECT
                                   DISTINCT
                                   concat(n.nodo_id,' - ',n.nombre)
                                FROM
                                   nodo n,monitor m
                                WHERE
                                   m.monitor_id IN
                                     (
                                   	  SELECT
                                   	       DISTINCT unnest(oc.monitor_id) AS monitor
                                  	  FROM
                                 	        objetivo_config oc
                                  	  WHERE
                                 	         objetivo_id = %s
                                   	  ORDER BY monitor ASC
                                 	     ) AND m.nodo_id = n.nodo_id;""", (id_objetivo,))
            return cursor
        except:
            return False


class consulta_user_compania:
    @staticmethod
    def select_user_compania():
        try:
            usuario = session['cliente_usuario_id']
            cursor = conexion.conect_post()

            cursor.execute("""SELECT cu.nombre , c.nombre
                                FROM public.cliente_usuario cu inner join public.cliente c
                                ON cu.cliente_id = c.cliente_id
                                WHERE cu.cliente_usuario_id = %s""", (usuario,))
            return cursor
        except:
            return False


class consulta_user:
    @staticmethod
    def select_user():
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                	CONCAT (
                                		cliente_usuario_id,
                                		' - ',
                                		nombre
                                	)
                                FROM
                                	PUBLIC .cliente_usuario
                                WHERE
                                	cliente_id = 1
                                AND cliente_usuario_id NOT IN (
                                	SELECT
                                		cliente_usuario_id :: INTEGER
                                	FROM
                                		marcadodatos.perfil_usuario
                                );  """)
            return cursor
        except:
            return False


class consulta_user_perfiles:
    @staticmethod
    def select_user_perfil():
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT a2.nombre_perfil, a1.activo, a1.nombre_usuario,a1.id_perfil_usuario
                              FROM marcadodatos.perfil_usuario  a1 inner join marcadodatos.perfil a2
                              ON a1.perfil_id = a2.perfil_id""")
            return cursor
        except:
            return False


class actualiza_perfil:
    @staticmethod
    def update_perfil(nombre_perfil, activo, id_perfil_usuario):
        try:
            connection = psycopg2.connect(
                database="central2010", user="postgres", password="atentusdesa", host="172.16.5.124", port="5432")
                # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")
            cursor = connection.cursor()
            cursor.execute(""" UPDATE marcadodatos.perfil_usuario SET  perfil_id=%s, activo=%s WHERE id_perfil_usuario =%s """,
                           (nombre_perfil, activo, id_perfil_usuario))

            connection.commit()
            flash("DATOS ACTUALIZADOS EXITOSAMENTE", "success")
        except:
            flash("NO ES POSIBLE ACTUALIZAR !!", "danger")
            return cursor


class consulta_perfil:
    @staticmethod
    def select_perfil():
        try:
            usuario = session['cliente_usuario_id']
            cursor = conexion.conect_post()
            cursor.execute("""SELECT a1.nombre_perfil, b2.activo
                                  FROM marcadodatos.perfil a1 inner join marcadodatos.perfil_usuario b2
                                  ON a1.perfil_id = b2.perfil_id
                                  where b2.cliente_usuario_id = '%s'""", (usuario,))
            return cursor
        except:
            return False


class insertar_registro_perfil:
    @staticmethod
    def insert_perfil(list, perfil_usr_add, activo_usr_add):

        connection = psycopg2.connect(
            database="central2010", user="postgres", password="atentusdesa", host="172.16.5.124", port="5432")
            # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")
        cursor = connection.cursor()
        for data in list:
            cursor.execute(
                "SELECT MAX( id_perfil_usuario ) + 1 FROM marcadodatos.perfil_usuario")
            id_datos = cursor.fetchone()
            cursor.execute("""INSERT INTO marcadodatos.perfil_usuario(id_perfil_usuario, cliente_usuario_id, perfil_id, activo, nombre_usuario)
                                    VALUES (%s,%s,%s,%s,%s)""",
                           (id_datos, data["id_usuario_perfil"], perfil_usr_add, activo_usr_add, data["nombre_usuario_perfil"]))
            connection.commit()
        # flash("DATOS INGRESADOS CON EXITO", "success")
        return cursor


class consulta_cache:
    @staticmethod
    def select_cache(objetivo, fecha_inicial):
        try:
            cursor = conexion.conect_post()
            cursor.execute(""" SELECT
                            		fecha_creacion,
                            		fecha_expiracion,
                            		nombre,
                            		parametro
                            	FROM
                            		cache.cache_nivel1
                            	WHERE
                            		%s::text = ANY (parametro) AND
                                    fecha_creacion::date BETWEEN %s and '2050-01-01'""", (objetivo, fecha_inicial,))
            return cursor
        except:
            return False


class borrar_cache:
    @staticmethod
    def delete_cache(objetivo, fecha_inicial):
        try:
            connection = psycopg2.connect(
                database="central2010", user="postgres", password="atentusdesa", host="172.16.5.124", port="5432")
                # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")
            cursor = connection.cursor()
            cursor.execute(""" DELETE FROM
                                		cache.cache_nivel1
                               WHERE
                                %s::text = ANY (parametro) AND
                                fecha_creacion::date BETWEEN %s and '2050-01-01'""", (objetivo, fecha_inicial,))

            connection.commit()
        except:
            return False


class consulta_cliente:
    @staticmethod
    def select_cliente(objetivo):
        try:
            cursor = conexion.conect_post()
            cursor.execute(""" SELECT
                                    cliente_usuario_id,
                                    o.nombre,
                                    o.descripcion
                                    FROM cliente_usuario cu, cliente_mapa_cliente_objetivo co, objetivo o
                                    WHERE cu.cliente_id = co.cliente_id
                                    AND o.objetivo_id = co.objetivo_id
                                    AND co.objetivo_id = %s
                                    AND (o.fecha_expiracion >= NOW() OR o.fecha_expiracion IS NULL)
                                    AND (cu.fecha_expiracion >= NOW() OR cu.fecha_expiracion IS NULL)
                                    ORDER BY cu.cliente_id DESC
                                    LIMIT 1; """, (objetivo,))
            return cursor
        except:
            return False


class consulta_zona:
    @staticmethod
    def select_zona(cliente_id):
        try:
            cursor = conexion.conect_post()
            cursor.execute(""" SELECT DISTINCT
                                	a1.valor
                                FROM
                                	PUBLIC .zona_horaria a1
                                INNER JOIN PUBLIC .cliente_usuario a2 ON a2.zona_horaria_id = a1.zona_horaria_id
                                WHERE
                                	a2.cliente_usuario_id = %s """, (cliente_id,))
            return cursor
        except:
            return False


class inserta_marcadoDatos:
    @staticmethod
    def insert_marcadoDatos(objetivo, nodos, hlocal_inicio, hlocal_termino, motivo):
        try:
            connection = psycopg2.connect(
                database="central2010", user="postgres", password="atentusdesa", host="172.16.5.124", port="5432")
                # database = "central2010", user = "reporte_web", password = ".112233.", host = "10.20.12.100", port = "5432")
            cursor = connection.cursor()

            cursor.execute(
                "SELECT MAX( periodo_marcado_id ) + 1 FROM public.periodo_marcado")
            periodo_marcado_id = cursor.fetchone()

            desarrollador = session['cliente_usuario'][0][0]
            cursor.execute("""INSERT INTO public.periodo_marcado
                                (periodo_marcado_id,objetivo_id, nodos_id, fecha_inicio, fecha_termino,motivo, autorizacion)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                           (periodo_marcado_id, objetivo, nodos, hlocal_inicio, hlocal_termino, motivo, desarrollador))
            connection.commit()
            # flash("DATOS INGRESADOS CON EXITO", "success")
            return cursor
        except:
            return False


class inserta_bitacora:
    @staticmethod
    def insert_bitacora(fecha_entrega, nombre_proyecto, observaciones):
        try:
            connection = psycopg2.connect(
                database="central2010", user="postgres", password="atentusdesa", host="172.16.5.124", port="5432")
                # database = "central2010", user = "reporte_web", password = ".112233.", host = "10.20.12.100", port = "5432")
            cursor = connection.cursor()

            desarrollador = session['cliente_usuario'][0][0]
            cursor.execute(
                "SELECT MAX( bitacora_id ) + 1 FROM log.bitacora")
            bitacora_id = cursor.fetchone()

            cursor.execute(
                "SELECT version FROM log.bitacora ORDER BY bitacora_id DESC LIMIT 1")
            version = cursor.fetchone()

            cursor.execute(
                "SELECT MAX( periodo_marcado_id ) FROM public.periodo_marcado")
            secuencia = cursor.fetchone()

            cursor.execute("""INSERT into
                                log.bitacora (bitacora_id,version,fecha_entrega, fecha_instalacion, desarrollador,
                                            nombre_proyecto,tipo, instalado,observaciones,secuencia)
                                values( %s,%s,%s,now(),%s,%s,'M','t',%s,%s);""",
                           (bitacora_id, version, fecha_entrega, desarrollador, nombre_proyecto, observaciones,secuencia))
            connection.commit()

            return cursor
        except:
            return False


#
#
class consulta_grafico:
    @staticmethod
    def select_grafico(fecha_inicial,fecha_final):
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                	CONCAT (a1.objetivo_id,' - ',a2.nombre),
                                	COUNT (a1.objetivo_id) AS total
                                FROM
                                	PUBLIC .periodo_marcado a1
                                INNER JOIN PUBLIC .objetivo a2 ON a1.objetivo_id = a2.objetivo_id
                                WHERE
                                	a1.fecha_inicio :: date BETWEEN %s and %s
                                GROUP BY
                                	a1.objetivo_id,
                                	a2.nombre
                                HAVING count(*)>=10
                                ORDER BY
                                	total DESC""",(fecha_inicial,fecha_final,))
            return cursor

        except:
            return False

class consulta_grafico_motivo:
    @staticmethod
    def select_grafico_motivo(fecha_inicial,fecha_final):
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                	CONCAT (objetivo_id,' - ',' Motivo ( ',motivo,'  ) '),
                                	COUNT (objetivo_id) AS total
                                FROM
                                	PUBLIC .periodo_marcado
                                WHERE
                                	fecha_inicio :: date BETWEEN %s and %s
                                GROUP BY
                                	objetivo_id,
                                	motivo
                                HAVING count(*)>=5
                                ORDER BY
                                	total DESC""",(fecha_inicial,fecha_final,))
            return cursor

        except:
            return False


class consulta_grafico_fechainicial:
    @staticmethod
    def select_grafico_fechainicial():
        try:
            cursor = conexion.conect_post()
            cursor.execute(""" SELECT
                                	concat (date_part('year', now()),'-','0',date_part('month', now()),'-','01')
                                UNION
                                	SELECT
                                		concat (date_part('year', now()),'-','0',date_part('month', now()),'-',
                                			EXTRACT (DAY
                                				FROM(
                                					SELECT
                                						date_trunc('month', CURRENT_DATE) + '1month' :: INTERVAL - '1sec' :: INTERVAL
                                					)
                                			)
                                		) """)
            return cursor

        except:
            return False

class consulta_grafico_nodos:
    @staticmethod
    def select_grafico_nodos(fecha_inicial,fecha_final):
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                	CONCAT (objetivo_id,' - ',nodos_id),
                                	COUNT (objetivo_id) AS total
                                FROM
                                	PUBLIC .periodo_marcado
                                WHERE
                                	fecha_inicio :: date BETWEEN %s and %s
                                GROUP BY
                                	objetivo_id,
                                	nodos_id
                                HAVING
                                	COUNT (*) >= 10
                                ORDER BY
                                	total DESC""",(fecha_inicial,fecha_final,))
            return cursor

        except:
            return False

class consulta_nodos():
    @staticmethod
    def select_nodos():
        try:
            cursor = conexion.conect_post()
            cursor.execute(""" SELECT
                                	CONCAT (a1.nodo_id, '-',a1.nombre,'-',a2.nombre)
                                FROM
                                	nodo a1
                                INNER JOIN pais a2 on a1.pais_id =  a2.pais_id
                                ORDER BY a1.nodo_id ASC""")
            return cursor

        except:
            return False


class consulta_grafico_marcado:
    @staticmethod
    def select_grafico_marcado(fecha_inicial,fecha_final):
        try:
            cursor = conexion.conect_post()

            cursor.execute("""SELECT count(id_tipo_marcado) FROM public.periodo_marcado
                                WHERE fecha_inicio :: date BETWEEN %s and %s""",(fecha_inicial,fecha_final))
            total = cursor.fetchone()
            for elem in total:
                totales =str(elem).split("L")[0]

            cursor.execute("""SELECT
                                	CONCAT(
                                        	CASE
                                        WHEN id_tipo_marcado = 7 THEN
                                        	'MARCADO (7)'
                                        ELSE
                                        	'MANTENCION (9)'
                                        END,' /','Q(',COUNT (id_tipo_marcado),')'),
                                        round(COUNT (id_tipo_marcado)*100 /%s ::numeric, 2)
                                FROM
                                	PUBLIC .periodo_marcado
                                WHERE
                                	id_tipo_marcado IN (7, 9)
                                AND fecha_inicio :: date BETWEEN %s and %s
                                GROUP BY
                                	id_tipo_marcado""",(totales,fecha_inicial,fecha_final,))
            return cursor

        except:
            return False
