import psycopg2
from flask import Flask, session


class conexion:
    @staticmethod
    def conect_post():
        try:
            connection = psycopg2.connect(
                database="central2010", user="postgres", password="atentusdesa", host="172.16.5.117", port="5432")
            #connection = psycopg2.connect(database = "central2010", user = "reporte_web", password = ".112233.", host = "10.20.12.100", port = "5432")
            cursor = connection.cursor()
            return cursor
        except:
            return False
