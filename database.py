import sqlite3
import os
import datetime

DB_PATH = 'appointments.db'

def get_db_connection():
    """Retorna una conexión a la base de datos configurada para retornar diccionarios."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos, creando la tabla si no existe e insertando datos de prueba iniciales."""
    # Comprobar si la DB es nueva para decidir si poblar con datos de prueba
    is_new = not os.path.exists(DB_PATH)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de turnos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            client_phone TEXT NOT NULL,
            client_email TEXT,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            service TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Si la base de datos es nueva, poblarla con algunos datos iniciales de prueba
    if is_new:
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - datetime.timedelta(days=1)
        
        mock_data = [
            ("Carlos Gómez", "11 5555 1234", "carlos@gmail.com", tomorrow.strftime("%Y-%m-%d"), "10:30", "Consulta Médica", "Confirmed", "Paciente requiere chequeo general preventivo."),
            ("María Rodríguez", "11 4444 5678", "maria.r@gmail.com", today.strftime("%Y-%m-%d"), "15:00", "Peluquería / Estética", "Pending", "Corte y tintura. Confirmar color antes de la cita."),
            ("Esteban Quito", "11 2222 3333", "equito@gmail.com", yesterday.strftime("%Y-%m-%d"), "11:00", "Servicio Técnico", "Completed", "Limpieza interna de notebook y cambio de pasta térmica.")
        ]
        
        cursor.executemany('''
            INSERT INTO appointments (client_name, client_phone, client_email, appointment_date, appointment_time, service, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', mock_data)
        
        conn.commit()
        print("Base de datos inicializada y poblada con datos de prueba.")
    else:
        print("Base de datos ya existente. Cargada con éxito.")
        
    conn.close()

def get_all_appointments(date_filter=None, status_filter=None, search_query=None):
    """Obtiene todos los turnos aplicando filtros de fecha, estado y búsqueda de texto."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM appointments WHERE 1=1"
    params = []
    
    if date_filter:
        query += " AND appointment_date = ?"
        params.append(date_filter)
        
    if status_filter and status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)
        
    if search_query:
        query += " AND (client_name LIKE ? OR client_phone LIKE ?)"
        # Búsqueda parcial (like)
        like_query = f"%{search_query}%"
        params.append(like_query)
        params.append(like_query)
        
    # Ordenar por fecha y hora (orden cronológico)
    query += " ORDER BY appointment_date ASC, appointment_time ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Convertir a lista de diccionarios
    return [dict(row) for row in rows]

def get_appointment_by_id(appointment_id):
    """Obtiene un único turno por su ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_appointment(client_name, client_phone, client_email, appointment_date, appointment_time, service, status='Pending', notes=''):
    """Inserta un nuevo turno en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (client_name, client_phone, client_email, appointment_date, appointment_time, service, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client_name, client_phone, client_email, appointment_date, appointment_time, service, status, notes))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_appointment(appointment_id, client_name, client_phone, client_email, appointment_date, appointment_time, service, status, notes):
    """Actualiza los datos de un turno existente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE appointments
        SET client_name = ?, client_phone = ?, client_email = ?, appointment_date = ?, appointment_time = ?, service = ?, status = ?, notes = ?
        WHERE id = ?
    ''', (client_name, client_phone, client_email, appointment_date, appointment_time, service, status, notes, appointment_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def delete_appointment(appointment_id):
    """Elimina físicamente un turno por su ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
