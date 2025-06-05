from flask import Flask
from routes.main_routes import main_routes, cargar_procesos_desde_archivo

app = Flask(__name__)
app.secret_key = "memoria_virtual"

# Carga los procesos desde archivo JSON o crea los procesos por defecto si el archivo no existe.
cargar_procesos_desde_archivo()

# Registra el blueprint principal con las rutas de la aplicación.
app.register_blueprint(main_routes)

if __name__ == "__main__":
    # Inicia la aplicación Flask en modo debug.
    app.run(debug=True)
