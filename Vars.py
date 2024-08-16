import os, sys
import queue
from pathlib import Path

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
        "nombre": "Body-parser",
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

BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))

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

keywordsCSS = {
    "tags": ['html', 'head', 'body', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'select', 'option', 'textarea', 'label', 'br', 'hr'],
    "selectors": [r'\*', 'element', '.class', '#id', 'element.class', 'element#id', 'element1 element2', 'element1 > element2', 'element1 + element2', 'element1 ~ element2'],
    "properties": ['color', 'background-color', 'font-size', 'font-family', 'font-weight', 'font-style', 'text-align', 'text-decoration', 'line-height', 'letter-spacing', 'width', 'height', 'margin', 'padding', 'border', 'border-radius', 'display', 'position', 'top', 'right', 'bottom', 'left', 'z-index', 'overflow', 'visibility', 'opacity', 'transform', 'transition', 'animation', 'box-shadow', 'text-shadow', 'background-image', 'background-position', 'background-size', 'background-repeat', 'background-attachment', 'background-clip', 'background-origin', 'background-color', 'background-blend-mode', 'background', 'box-sizing', 'outline', 'cursor', 'pointer-events', 'user-select', 'resize', 'overflow-wrap', 'word-break', 'white-space', 'text-overflow', 'word-wrap', 'text-transform', 'text-shadow', 'text-justify', 'text-indent' ],
    "values": ['inherit', 'initial', 'unset', 'none', 'auto', 'block', 'inline', 'inline-block', 'flex', 'grid', 'inline-flex', 'inline-grid', 'table', 'table-cell', 'table-row', 'table-row-group', 'table-column', 'table-column-group', 'table-header-group', 'table-footer-group', 'table-caption', 'absolute', 'relative', 'fixed', 'sticky', 'top', 'right', 'bottom', 'left', 'visible', 'hidden', 'collapse', 'static', 'absolute', 'relative', 'fixed', 'sticky', 'scroll', 'no-repeat', 'repeat', 'repeat-x', 'repeat-y', 'space', 'round', 'border-box', 'content-box', 'padding-box', 'inherit', 'initial', 'unset', 'normal', 'italic', 'oblique', 'bold', 'bolder', 'lighter', 'normal', 'uppercase', 'lowercase', 'capitalize', 'none', 'underline', 'overline', 'line-through', 'blink', 'solid', 'dotted', 'dashed', 'double', 'groove', 'ridge', 'inset', 'outset', 'transparent', 'currentColor', 'rgb()', 'rgba()', 'hsl()', 'hsla()', 'url()', 'linear-gradient()', 'radial-gradient()', 'repeating-linear-gradient()', 'repeating-radial-gradient()', 'calc()', 'var()', 'attr()', 'counter()', 'counters()', 'cubic-bezier()', 'steps()', 'ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear', 'step-start', 'step-end', 'steps()', 'cubic-bezier()', 'infinite', 'alternate', 'alternate-reverse', 'backwards', 'both', 'forwards', 'none', 'running', 'paused', 'normal', 'reverse', 'alternate', 'alternate-reverse', 'horizontal', 'vertical', 'both', 'none', 'solid', 'dotted', 'dashed', 'double', 'groove', 'ridge', 'inset', 'outset', 'thin', 'medium', 'thick', 'small', 'large', 'border-box', 'content-box', 'padding-box', 'scroll', 'auto', 'hidden', 'visible', 'fixed', 'absolute', 'relative', 'static', 'sticky', 'center', 'left', 'right', 'justify', 'inherit', 'initial', 'unset', 'normal', 'italic', 'oblique', 'bold', 'bolder', 'lighter', 'normal', 'uppercase', 'lowercase', 'capitalize', 'none', 'underline', 'overline', 'line-through', 'blink', 'solid', 'dotted', 'dashed', 'double', 'groove', 'ridge', 'inset', 'outset', 'transparent', 'currentColor', 'rgb()', 'rgba()', 'hsl()', 'hsla()', 'url()', 'linear-gradient()', 'radial-gradient()', 'repeating-linear-gradient()', 'repeating-radial-gradient()', 'calc()', 'var()', 'attr()', 'counter()', 'counters()', 'cubic-bezier()', 'steps()', 'ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear', 'step-start', 'step-end', 'steps()']
}
