# Archivo principal de la aplicación EcoAcción
# Aquí se manejan las rutas, la base de datos y la lógica del sitio

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Creamos la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_ecoaccion"  # Necesaria para usar sesiones

# Lista fija de retos ecológicos, ahora organizados por categoría
# Cada reto es una tupla: (nombre del reto, categoría)
RETOS_FIJOS = [
    ("Ahorrar agua al cepillarte los dientes", "Agua"),
    ("Cerrar bien la llave para evitar goteras", "Agua"),
    ("Reciclar una botella o envase de plástico", "Basura"),
    ("Separar la basura en orgánica e inorgánica", "Basura"),
    ("Apagar las luces innecesarias", "Energía"),
    ("Desconectar un cargador que no estés usando", "Energía"),
    ("Sembrar una planta", "Naturaleza"),
    ("Cuidar una planta o árbol de tu barrio", "Naturaleza"),
    ("Caminar en lugar de usar vehículo", "Movilidad"),
    ("Usar bicicleta o transporte público", "Movilidad"),
]


# Esta función crea la conexión con la base de datos SQLite
def obtener_conexion():
    conexion = sqlite3.connect("ecoaccion.db")
    conexion.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conexion


# Esta función crea las tablas de la base de datos si no existen todavía
def crear_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    """)

    # Tabla de retos (uno por usuario, por cada reto fijo)
    # Se agrega la columna "categoria" para poder agrupar los retos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL DEFAULT 'General',
            completado INTEGER DEFAULT 0,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conexion.commit()
    conexion.close()


# Esta función crea los retos fijos para un usuario recién registrado
def crear_retos_para_usuario(usuario_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    for nombre_reto, categoria in RETOS_FIJOS:
        cursor.execute(
            "INSERT INTO retos (nombre, categoria, completado, usuario_id) VALUES (?, ?, 0, ?)",
            (nombre_reto, categoria, usuario_id)
        )
    conexion.commit()
    conexion.close()


# Ruta de la página de inicio
@app.route("/")
def inicio():
    return render_template("index.html")


# Ruta para registrar un nuevo usuario
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        # Encriptamos la contraseña antes de guardarla
        contrasena_encriptada = generate_password_hash(contrasena)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificamos si el correo ya está registrado
        cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            conexion.close()
            return render_template("register.html", error="Ese correo ya está registrado")

        # Guardamos el nuevo usuario en la base de datos
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena) VALUES (?, ?, ?)",
            (nombre, correo, contrasena_encriptada)
        )
        conexion.commit()

        # Obtenemos el id del usuario recién creado
        usuario_id = cursor.lastrowid
        conexion.close()

        # Creamos los retos fijos para este usuario
        crear_retos_para_usuario(usuario_id)

        return redirect(url_for("login"))

    return render_template("register.html")


# Ruta para iniciar sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
        usuario = cursor.fetchone()
        conexion.close()

        # Verificamos que el usuario exista y la contraseña sea correcta
        if usuario and check_password_hash(usuario["contrasena"], contrasena):
            session["usuario_id"] = usuario["id"]
            session["nombre"] = usuario["nombre"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Correo o contraseña incorrectos")

    return render_template("login.html")


# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


# Ruta del dashboard del usuario
@app.route("/dashboard")
def dashboard():
    # Si no hay sesión iniciada, redirigimos al login
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Contamos cuántos retos ha completado el usuario
    cursor.execute(
        "SELECT COUNT(*) FROM retos WHERE usuario_id = ? AND completado = 1",
        (session["usuario_id"],)
    )
    completados = cursor.fetchone()[0]

    # Contamos el total de retos que tiene ese usuario
    cursor.execute(
        "SELECT COUNT(*) FROM retos WHERE usuario_id = ?",
        (session["usuario_id"],)
    )
    total_retos = cursor.fetchone()[0]
    conexion.close()

    # Calculamos el porcentaje de progreso para la barra (evitando dividir entre 0)
    progreso = int((completados / total_retos) * 100) if total_retos > 0 else 0

    return render_template(
        "dashboard.html",
        nombre=session["nombre"],
        completados=completados,
        total=total_retos,
        progreso=progreso
    )


# Ruta que muestra la lista de retos ecológicos, agrupados por categoría
@app.route("/retos")
def retos():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM retos WHERE usuario_id = ? ORDER BY categoria",
        (session["usuario_id"],)
    )
    lista_retos = cursor.fetchall()
    conexion.close()

    # Agrupamos los retos en un diccionario: {"Agua": [reto, reto...], "Basura": [...]}
    retos_por_categoria = {}
    for reto in lista_retos:
        categoria = reto["categoria"]
        if categoria not in retos_por_categoria:
            retos_por_categoria[categoria] = []
        retos_por_categoria[categoria].append(reto)

    # Revisamos si ya se completaron todos los retos para mostrar el mensaje final
    todos_completados = all(reto["completado"] == 1 for reto in lista_retos) if lista_retos else False

    return render_template(
        "retos.html",
        retos_por_categoria=retos_por_categoria,
        todos_completados=todos_completados
    )


# Ruta para marcar un reto como completado
@app.route("/completar_reto/<int:reto_id>")
def completar_reto(reto_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    # Solo actualizamos el reto si pertenece al usuario que inició sesión
    cursor.execute(
        "UPDATE retos SET completado = 1 WHERE id = ? AND usuario_id = ?",
        (reto_id, session["usuario_id"])
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("retos"))


# Punto de entrada del programa
if __name__ == "__main__":
    crear_base_datos()  # Aseguramos que la base de datos y tablas existan
    app.run(debug=True)