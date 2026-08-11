# Agenda de Turnos - CRUD Premium de Repaso

Esta es una aplicación tipo **CRUD (Crear, Leer, Actualizar, Borrar)** diseñada para gestionar y reservar turnos. Este proyecto fue construido como un material de repaso práctico de desarrollo web para estudiantes, abarcando conceptos clave tanto de frontend como de backend.

## 🚀 Tecnologías Utilizadas

- **Frontend (Interfaz)**:
  - **HTML5**: Estructura semántica, accesible y uso de elementos modernos como `<dialog>` nativo.
  - **CSS3 Puro**: Hojas de estilo premium con diseño **Glassmorphic** (efectos de vidrio translúcido), variables CSS, Flexbox/Grid para un diseño responsivo y micro-animaciones personalizadas.
  - **JavaScript Vainilla**: Manipulación del DOM en tiempo real, validación de formularios interactiva, comunicación asíncrona mediante **Fetch API** y notificaciones flotantes (Toast) personalizadas.
- **Backend (Servidor)**:
  - **Python 3**: Enrutamiento y control a través de **Flask**.
- **Base de Datos (Persistencia)**:
  - **SQLite**: Persistencia local a través del módulo estándar de Python `sqlite3`.

---

## 🛠️ Estructura del Proyecto

```text
agenda-turnos-repaso/
├── app.py                  # Servidor Flask y Endpoints API REST
├── database.py             # Lógica e inicialización de la Base de Datos SQLite
├── test_api.py             # Suite de pruebas unitarias automatizadas
├── requirements.txt        # Dependencias de Python (Flask)
├── .gitignore              # Archivos excluidos de Git
├── templates/
│   └── index.html          # Vista HTML5 principal de la aplicación
└── static/
    ├── css/
    │   └── style.css       # Estilos CSS premium y responsivos
    └── js/
        └── app.js          # Controlador JavaScript de la interfaz
```

---

## 💻 Instalación y Ejecución Local

Sigue estos pasos para poner en marcha el proyecto en tu entorno local:

### 1. Clonar el repositorio (si aún no lo tienes localmente)
```bash
git clone https://github.com/sergiogimenezclass/agenda-tunros-repaso.git
cd agenda-turnos-repaso
```

### 2. Configurar el Entorno Virtual de Python
Crea y activa un entorno virtual para mantener las dependencias aisladas:

**En Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**En Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar Dependencias
Instala los paquetes necesarios definidos en `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Iniciar la Aplicación
Ejecuta el servidor Flask:
```bash
python app.py
```
El servidor se iniciará en modo depuración (debug) en: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**. Abre esta dirección en tu navegador para ver la aplicación en funcionamiento. La base de datos SQLite `appointments.db` se creará y se inicializará automáticamente con algunos registros semilla si es la primera vez que se ejecuta.

---

## 🧪 Pruebas Unitarias

Para verificar que todos los endpoints CRUD y las validaciones del servidor funcionan correctamente, puedes ejecutar las pruebas unitarias automatizadas:

```bash
python test_api.py
```

El script utiliza una base de datos SQLite en memoria/temporal aislada para evitar alterar tus datos reales de desarrollo.
