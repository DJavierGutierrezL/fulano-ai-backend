import psycopg2

try:
    conn = psycopg2.connect(
        "postgresql://fulano_ai_db_user:6Tpf1bWYJ0aaeYxgjZxRhWxmAz4HnqwL@dpg-d2nmvqbipnbc738d5l20-a.ohio-postgres.render.com/fulano_ai_db"
    )
    cur = conn.cursor()

    sql = """
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    ALTER TABLE conversations
    ADD COLUMN IF NOT EXISTS conversation_id UUID UNIQUE DEFAULT gen_random_uuid();

    ALTER TABLE conversations
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE CASCADE,
        role VARCHAR(50),
        content TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """

    cur.execute(sql)
    conn.commit()
    print("¡Tablas actualizadas correctamente!")

except Exception as e:
    print("❌ Ocurrió un error:", e)

finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
