import os
import queue

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

respuestas = queue.Queue()

registro_commits = queue.Queue()

keywordsPY = {
    "boolean_values": ['True', 'False', 'None'],
    "control_flow": ['if', 'else', 'elif', 'for', 'while', 'break', 'continue', 'pass', 'return', 'yield'],
    "logical_operators": ['and', 'or', 'not', 'is', 'in'],
    "function_class_declarations": ['def', 'class', 'lambda'],
    "exception_handling": ['try', 'except', 'raise', 'finally', 'assert'],
    "import_statements": ['import', 'from', 'as'],
    "context_management": ['with', 'async', 'await'],
    "scope_declarations": ['global', 'nonlocal'],
    "others": ['del', 'raise']
}

keywordsJS = {
    "boolean_values": ['true', 'false', 'null'],
    "control_flow": ['if', 'else', 'for', 'while', 'do', 'break', 'continue', 'return', 'switch', 'case'],
    "logical_operators": ['&&', '||', '!', 'instanceof'],
    "function_class_declarations": ['function', 'class', 'constructor'],
    "exception_handling": ['try', 'catch', 'finally', 'throw'],
    "import_statements": ['import', 'export', 'as', 'from'],
    "scope_declarations": ['var', 'let', 'const'],
    "others": ['delete', 'typeof', 'new']
}

keywordsHTML = {
    "tags": ['html', 'head', 'body', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'select', 'option', 'textarea', 'label', 'br', 'hr'],
    "attributes": ['id', 'class', 'style', 'src', 'href', 'alt', 'title', 'width', 'height', 'colspan', 'rowspan', 'type', 'name', 'value', 'placeholder', 'required', 'disabled', 'readonly', 'checked', 'selected', 'multiple', 'for', 'action', 'method', 'enctype', 'target']
}
