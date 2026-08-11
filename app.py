from flask import Flask, render_template, jsonify, request
import datetime
import re
import database

app = Flask(__name__)

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
    
    try:
        appointments = database.get_all_appointments(
            date_filter=date_filter,
            status_filter=status_filter,
            search_query=search_query
        )
        return jsonify(appointments)
    except Exception as e:
        return jsonify({"error": f"Error al consultar la base de datos: {str(e)}"}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    try:
        appointment = database.get_appointment_by_id(appointment_id)
        if not appointment:
            return jsonify({"error": "Turno no encontrado."}), 404
        return jsonify(appointment)
    except Exception as e:
        return jsonify({"error": f"Error al consultar el turno: {str(e)}"}), 500

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json() or {}
    
    # Validar
    errors = validate_appointment_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
        
    try:
        new_id = database.create_appointment(
            client_name=data["client_name"].strip(),
            client_phone=data["client_phone"].strip(),
            client_email=data.get("client_email", "").strip(),
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"],
            service=data["service"],
            status=data.get("status", "Pending"),
            notes=data.get("notes", "").strip()
        )
        
        # Devolver el objeto creado
        created_appointment = database.get_appointment_by_id(new_id)
        return jsonify(created_appointment), 201
    except Exception as e:
        return jsonify({"error": f"Error al guardar en la base de datos: {str(e)}"}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    # Verificar existencia
    appointment = database.get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({"error": "Turno no encontrado."}), 404
        
    data = request.get_json() or {}
    
    # Validar datos
    errors = validate_appointment_data(data, is_update=True)
    if errors:
        return jsonify({"errors": errors}), 400
        
    try:
        success = database.update_appointment(
            appointment_id=appointment_id,
            client_name=data["client_name"].strip(),
            client_phone=data["client_phone"].strip(),
            client_email=data.get("client_email", "").strip(),
            appointment_date=data["appointment_date"],
            appointment_time=data["appointment_time"],
            service=data["service"],
            status=data.get("status", appointment["status"]),
            notes=data.get("notes", "").strip()
        )
        
        if not success:
            return jsonify({"error": "No se pudo actualizar el turno."}), 500
            
        updated_appointment = database.get_appointment_by_id(appointment_id)
        return jsonify(updated_appointment)
    except Exception as e:
        return jsonify({"error": f"Error al actualizar la base de datos: {str(e)}"}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    # Verificar existencia
    appointment = database.get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({"error": "Turno no encontrado."}), 404
        
    try:
        success = database.delete_appointment(appointment_id)
        if not success:
            return jsonify({"error": "No se pudo eliminar el turno."}), 500
        return jsonify({"success": True, "message": "Turno eliminado con éxito."})
    except Exception as e:
        return jsonify({"error": f"Error al eliminar en la base de datos: {str(e)}"}), 500

# Inicializar Base de Datos al arrancar
database.init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
