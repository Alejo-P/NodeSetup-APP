import os

listaArgumentos = [
    "",
    "-S",
    "-D",
    "-O",
    "--no-save",
    "--production",
    "--only=dev",
    "--only=prod",
    "-E",
    "-f",
    "--no-optional",
    "-P",
    "--dry-run",
    "--legacy-peer-deps",
    "--strict-peer-deps",
    "--global-style",
]

carpetas = [
    "config",
    "controllers",
    "helpers",
    "models",
    "public",
    "routers",
    "views"
]

archivos_p = [
    ".env",
    ".env.example",
    ".gitignore"
]

archivos = [
    "database.js",
    "server.js",
    "index.js"
]

lista_modulosNPM = [
    {
        "usar": None,
        "nombre": "Axios",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Bcrypt",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Cloudinary",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None    
    },
    {
        "usar": None,
        "nombre": "Cors",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None    
    },
    {
        "usar": None,
        "nombre": "Dotenv",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None    
    },
    {
        "usar": None,
        "nombre": "Express",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None    
    },
    {
        "usar": None,
        "nombre": "Express-fileupload",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None    
    },
    {
        "usar": None,
        "nombre": "Fs-extra",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None    
    },
    {
        "usar": None,
        "nombre": "Json-server",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Jsonwebtoken",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Mongoose",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Morgan",
        "argumento": None, 
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "MySQL2",
        "argumento": None, 
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Nodemailer",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Nodemon",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Sequelize",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None
    },
    {
        "usar": None,
        "nombre": "Uuid",
        "argumento": None,
        "version": None,
        "versiones": None,
        "global": None  
    }
]

Registro_hilos = []

Registro_eventos = []

ruta = os.getcwd()