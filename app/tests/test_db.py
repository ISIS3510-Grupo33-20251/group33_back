from database import SessionLocal
from sqlalchemy.sql import text

def test_connection():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        print("✅ Conexión a PostgreSQL exitosa!")
    except Exception as e:
        print(f"❌ Error en la conexión: {e}")
    finally:
        db.close()

test_connection()
