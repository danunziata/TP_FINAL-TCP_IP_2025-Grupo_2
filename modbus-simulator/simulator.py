import psycopg2
from datetime import datetime
import random
import time
import sys

# Configuración de la base de datos
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "medicionesdb"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Intervalo de simulación en segundos
INTERVALO_SEGUNDOS = 5

def conectar_db():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("[INFO] Conexión establecida con la base de datos.")
            return conn
        except Exception as e:
            print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
            print("Reintentando en 5 segundos...")
            time.sleep(5)

def insertar_datos(cur, conn):
    query = """
        INSERT INTO mediciones (fecha_hora, ia, ib, ic, va, vb, vc, p_act, p_react, fp, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        datetime.now(),
        random.uniform(0, 50),
        random.uniform(0, 50),
        random.uniform(0, 50),
        random.uniform(200, 240),
        random.uniform(200, 240),
        random.uniform(200, 240),
        random.uniform(0, 5000),
        random.uniform(0, 2000),
        random.uniform(0.7, 1),
        random.randint(0, 1)
    )
    cur.execute(query, values)
    conn.commit()

def main():
    conn = conectar_db()
    cur = conn.cursor()

    try:
        while True:
            insertar_datos(cur, conn)
            print(f"[INFO] Dato simulado insertado: {datetime.now()}")
            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\n[INFO] Simulación detenida manualmente.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cur.close()
        conn.close()
        print("[INFO] Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    main()
