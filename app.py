from flask import Flask, render_template, jsonify, request
import datetime
import re

app = Flask(__name__)

# Datos simulados en memoria para la Fase 2
APPOINTMENTS = [
    {
        "id": 1,
        "client_name": "Carlos Gómez",
        "client_phone": "11 5555 1234",
        "client_email": "carlos@gmail.com",
        "appointment_date": (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        "appointment_time": "10:30",
        "service": "Consulta Médica",
        "status": "Confirmed",
        "notes": "Paciente requiere chequeo general preventivo."
    },
    {
        "id": 2,
        "client_name": "María Rodríguez",
        "client_phone": "11 4444 5678",
        "client_email": "maria.r@gmail.com",
        "appointment_date": datetime.date.today().strftime("%Y-%m-%d"),
        "appointment_time": "15:00",
        "service": "Peluquería / Estética",
        "status": "Pending",
        "notes": "Corte y tintura. Confirmar color antes de la cita."
    },
    {
        "id": 3,
        "client_name": "Esteban Quito",
        "client_phone": "11 2222 3333",
        "client_email": "equito@gmail.com",
        "appointment_date": (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        "appointment_time": "11:00",
        "service": "Servicio Técnico",
        "status": "Completed",
        "notes": "Limpieza interna de notebook y cambio de pasta térmica."
    }
]
NEXT_ID = 4

# Servicios válidos para validación
VALID_SERVICES = [
    "Asesoría General",
    "Consulta Médica",
    "Servicio Técnico",
    "Trámite Administrativo",
    "Peluquería / Estética",
    "Otro"
]

# Estados válidos
VALID_STATUSES = ["Pending", "Confirmed", "Completed", "Cancelled"]

def validate_appointment_data(data, is_update=False):
    errors = {}
    
    # Validar Nombre
    if "client_name" not in data or not data["client_name"].strip():
        errors["client_name"] = "El nombre del cliente es obligatorio."
    elif len(data["client_name"]) < 3:
        errors["client_name"] = "El nombre debe tener al menos 3 caracteres."
        
    # Validar Teléfono
    if "client_phone" not in data or not data["client_phone"].strip():
        errors["client_phone"] = "El teléfono es obligatorio."
        
    # Validar Email (opcional, pero si existe debe ser válido)
    if "client_email" in data and data["client_email"].strip():
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, data["client_email"]):
            errors["client_email"] = "El formato de correo es inválido."
            
    # Validar Fecha
    if "appointment_date" not in data or not data["appointment_date"].strip():
        errors["appointment_date"] = "La fecha es obligatoria."
    else:
        try:
            datetime.datetime.strptime(data["appointment_date"], "%Y-%m-%d")
        except ValueError:
            errors["appointment_date"] = "La fecha debe tener el formato AAAA-MM-DD."
            
    # Validar Hora
    if "appointment_time" not in data or not data["appointment_time"].strip():
        errors["appointment_time"] = "La hora es obligatoria."
    else:
        try:
            datetime.datetime.strptime(data["appointment_time"], "%H:%M")
        except ValueError:
            errors["appointment_time"] = "La hora debe tener el formato HH:MM."
            
    # Validar Servicio
    if "service" not in data or data["service"] not in VALID_SERVICES:
        errors["service"] = "Debe seleccionar un servicio válido."
        
    # Validar Estado (si se actualiza o si se provee explícitamente)
    if "status" in data and data["status"] not in VALID_STATUSES:
        errors["status"] = "El estado seleccionado no es válido."
        
    return errors

@app.route('/')
def index():
    # Sirve el archivo index.html ubicado en templates/
    return render_template('index.html')

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')
    search_query = request.args.get('search')
    
    filtered_list = APPOINTMENTS.copy()
    
    # Aplicar filtros
    if date_filter:
        filtered_list = [a for a in filtered_list if a["appointment_date"] == date_filter]
        
    if status_filter and status_filter != 'all':
        filtered_list = [a for a in filtered_list if a["status"] == status_filter]
        
    if search_query:
        search_query = search_query.lower()
        filtered_list = [
            a for a in filtered_list 
            if search_query in a["client_name"].lower() or search_query in a["client_phone"]
        ]
        
    # Ordenar por fecha y hora (de más reciente a más antigua)
    filtered_list.sort(key=lambda x: (x["appointment_date"], x["appointment_time"]))
    
    return jsonify(filtered_list)

@app.route('/api/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = next((a for a in APPOINTMENTS if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Turno no encontrado."}), 404
    return jsonify(appointment)

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    global NEXT_ID
    data = request.get_json() or {}
    
    # Validar
    errors = validate_appointment_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
        
    # Crear registro
    new_appointment = {
        "id": NEXT_ID,
        "client_name": data["client_name"].strip(),
        "client_phone": data["client_phone"].strip(),
        "client_email": data.get("client_email", "").strip(),
        "appointment_date": data["appointment_date"],
        "appointment_time": data["appointment_time"],
        "service": data["service"],
        "status": data.get("status", "Pending"),
        "notes": data.get("notes", "").strip()
    }
    
    APPOINTMENTS.append(new_appointment)
    NEXT_ID += 1
    
    return jsonify(new_appointment), 201

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    appointment = next((a for a in APPOINTMENTS if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Turno no encontrado."}), 404
        
    data = request.get_json() or {}
    
    # Validar datos
    errors = validate_appointment_data(data, is_update=True)
    if errors:
        return jsonify({"errors": errors}), 400
        
    # Actualizar campos
    appointment["client_name"] = data["client_name"].strip()
    appointment["client_phone"] = data["client_phone"].strip()
    appointment["client_email"] = data.get("client_email", "").strip()
    appointment["appointment_date"] = data["appointment_date"]
    appointment["appointment_time"] = data["appointment_time"]
    appointment["service"] = data["service"]
    appointment["status"] = data.get("status", appointment["status"])
    appointment["notes"] = data.get("notes", "").strip()
    
    return jsonify(appointment)

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    global APPOINTMENTS
    appointment = next((a for a in APPOINTMENTS if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Turno no encontrado."}), 404
        
    APPOINTMENTS = [a for a in APPOINTMENTS if a["id"] != appointment_id]
    return jsonify({"success": True, "message": "Turno eliminado con éxito."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
