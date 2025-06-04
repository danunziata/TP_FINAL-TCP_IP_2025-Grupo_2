import pandas as pd
import psycopg2
import os
import time

while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )

        query = "SELECT * FROM mediciones"
        df = pd.read_sql_query(query, conn)

        output_path = "/app/exportaciones/mediciones_exportadas.csv"
        df.to_csv(output_path, index=False)
        print(f"[INFO] CSV exportado en: {output_path}")

        conn.close()
        break  # Solo exporta una vez y termina

    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(5)
