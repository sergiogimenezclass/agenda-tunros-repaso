import unittest
import json
import os
import app
import database

class TestAppointmentsAPI(unittest.TestCase):
    def setUp(self):
        # Usar una base de datos de pruebas temporal para no interferir con la de desarrollo
        database.DB_PATH = 'test_appointments.db'
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        
        # Inicializar la base de datos de pruebas
        database.init_db()
        
        # Configurar la aplicación Flask en modo pruebas
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    def tearDown(self):
        # Limpiar la base de datos de pruebas al finalizar
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_get_appointments(self):
        """Verifica que el listado inicial retorna los 3 registros semilla."""
        response = self.client.get('/api/appointments')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)

    def test_get_appointment_by_id(self):
        """Verifica la obtención de un turno específico por ID."""
        response = self.client.get('/api/appointments/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["client_name"], "Carlos Gómez")

    def test_get_appointment_by_id_not_found(self):
        """Verifica que buscar un ID inexistente retorna 404."""
        response = self.client.get('/api/appointments/999')
        self.assertEqual(response.status_code, 404)

    def test_create_appointment_success(self):
        """Verifica la creación exitosa de un turno con datos válidos."""
        payload = {
            "client_name": "Juan Perez",
            "client_phone": "11 9876 5432",
            "client_email": "juan@perez.com",
            "appointment_date": "2026-08-20",
            "appointment_time": "16:00",
            "service": "Asesoría General",
            "notes": "Cita de prueba automatizada."
        }
        response = self.client.post('/api/appointments', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("id", data)
        self.assertEqual(data["client_name"], "Juan Perez")
        self.assertEqual(data["status"], "Pending")

    def test_create_appointment_validation_errors(self):
        """Verifica que el servidor valida campos obligatorios y formatos incorrectos."""
        payload = {
            "client_name": "J",  # Muy corto (min 3)
            # Falta client_phone obligatoria
            "client_email": "correo-invalido", # Formato inválido
            "appointment_date": "20-08-2026",  # Formato incorrecto (debe ser AAAA-MM-DD)
            "appointment_time": "4 PM",        # Formato incorrecto (debe ser HH:MM)
            "service": "Servicio Inexistente"   # No está en lista de válidos
        }
        response = self.client.post('/api/appointments', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("errors", data)
        errors = data["errors"]
        self.assertIn("client_name", errors)
        self.assertIn("client_phone", errors)
        self.assertIn("client_email", errors)
        self.assertIn("appointment_date", errors)
        self.assertIn("appointment_time", errors)
        self.assertIn("service", errors)

    def test_update_appointment_success(self):
        """Verifica que se actualiza un turno existente correctamente."""
        payload = {
            "client_name": "Carlos Gómez Modificado",
            "client_phone": "11 5555 1234",
            "client_email": "carlos.g@gmail.com",
            "appointment_date": "2026-08-12",
            "appointment_time": "10:30",
            "service": "Consulta Médica",
            "status": "Confirmed",
            "notes": "Notas modificadas en prueba."
        }
        response = self.client.put('/api/appointments/1', 
                                  data=json.dumps(payload),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["client_name"], "Carlos Gómez Modificado")
        self.assertEqual(data["client_email"], "carlos.g@gmail.com")

    def test_delete_appointment_success(self):
        """Verifica la eliminación correcta de un turno."""
        response = self.client.delete('/api/appointments/3')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        # Consultar de nuevo para corroborar la eliminación física
        response_get = self.client.get('/api/appointments/3')
        self.assertEqual(response_get.status_code, 404)

if __name__ == '__main__':
    unittest.main()
