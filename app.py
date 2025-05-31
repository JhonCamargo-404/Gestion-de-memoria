from flask import Flask
from routes.main_routes import main_routes

app = Flask(__name__)
app.secret_key = "simulador_memoria"

# Registrar las rutas desde el blueprint
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True)
