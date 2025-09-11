npm_modules = sorted([
    "Cloudinary",
    "Body-parser",
    "Dotenv",
    "Bcrypt",
    "Cors",
    "Express",
    "Axios",
    "Express-fileupload",
    "Json-server",
    "Fs-extra",
    "Mongoose",
    "Uuid",
    "Jsonwebtoken",
    "Typescript",
    "MySQL2",
    "Morgan",
    "Sequelize",
    "Nodemon",
    "Express-validator",
    "Nodemailer",
    "Swagger-jsdoc",
    "Swagger-ui-express"
], key=str.lower)

npm_args_list = [
    "-g", # --global
    "-S", # --save
    "-D", # --save-dev
    "-O", # --save-optional
    "--no-save",
    "--production",
    "--only=dev",
    "--only=prod",
    "-E", # --exact
    "-f", # --force
    "--no-optional",
    "-P", # --peer
    "--dry-run",
    "--legacy-peer-deps",
    "--strict-peer-deps",
    "--global-style",
]