import pyodbc
from app.core.config import settings

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados MS SQL Server.
    Lida com exceções de conexão.
    """
    try:
        conn = pyodbc.connect(settings.DATABASE_URL)
        print("INFO:     Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"ERRO:     Falha na conexão com o banco de dados. SQLSTATE: {sqlstate}")
        print(ex)
        return None