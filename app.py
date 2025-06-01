from flask import Flask
from routes.main_routes import main_routes, cargar_procesos_desde_archivo

app = Flask(__name__)
app.secret_key = "memoria_virtual"

# Cargar procesos desde archivo si existen (o crear por defecto si no)
cargar_procesos_desde_archivo()

# Registrar las rutas principales
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True)
