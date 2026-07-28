# 🌱 EcoAcción

EcoAcción es una aplicación web educativa que ayuda a las personas a aprender
sobre el cambio climático completando 10 pequeños retos ecológicos.

## Tecnologías utilizadas

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite

## Estructura del proyecto

```
ecoaccion/
│
├── main.py                  -> Archivo principal con las rutas de Flask
├── requirements.txt          -> Dependencias del proyecto
├── ecoaccion.db               -> Base de datos SQLite (se crea automáticamente)
│
├── templates/
│   ├── index.html            -> Página de inicio
│   ├── register.html         -> Página de registro
│   ├── login.html            -> Página de inicio de sesión
│   ├── dashboard.html        -> Panel del usuario
│   └── retos.html            -> Página de los 5 retos ecológicos
│
└── static/
    ├── css/
    │   └── style.css         -> Estilos verdes y blancos
    └── js/
        └── script.js         -> Pequeñas animaciones e interacciones
```

## Cómo ejecutar el proyecto

1. Abre una terminal en la carpeta del proyecto.
2. Instala las dependencias:

```
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```
python main.py
```

4. Abre tu navegador en la dirección que aparece en la terminal
   (normalmente `http://127.0.0.1:5000`).

## Funcionamiento general

1. El usuario ve la página de inicio y presiona "Comenzar ahora".
2. Se registra con su nombre, correo y contraseña.
3. Inicia sesión con su correo y contraseña.
4. En el dashboard ve cuántos retos ha completado y su barra de progreso.
5. En la página de retos puede marcar cada reto como "Completado".
6. Al completar los 5 retos, aparece un mensaje de felicitación 🎉.

## Tablas de la base de datos

**usuarios**: id, nombre, correo, contraseña (encriptada)

**retos**: id, nombre, completado (0 o 1), usuario_id

La base de datos `ecoaccion.db` se crea automáticamente la primera vez
que se ejecuta `main.py`, así que no necesitas crearla manualmente.
