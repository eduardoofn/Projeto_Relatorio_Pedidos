import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Estabelece uma conexão com o banco de dados SQL Server.
    """
    try:
        connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};" 
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')}"
        )
        return connection
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

def execute_query(query, params=None, fetch=False):
    """
    Executa uma query SQL no banco de dados.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            conn.close()
            return True
    return False
