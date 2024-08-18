<h1 align="center">Historial de versiones</h1>


<div align="center">
    <p>Version actual</p>
    <img src="https://img.shields.io/badge/Version-2.0.0-blue.svg" alt="Version de la app">
</div>

<h2 align="center">Tabla de versiones y cambios</h2>
<table>
    <thead>
        <tr>
            <th>Versión</th>
            <th>Fecha modificación</th>
            <th>Cambios realizados</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2.0.0</td>
            <td>2024-08-17</td>
            <td>
                <ul>
                    <li>
                        Se cambio el estilo de la UI de la aplicación.
                    </li>
                    <li>
                        Se añadio un boton <strong>git</strong> que abre una ventana que permite clonar un repositorio de git en la ruta seleccionada, hacer commits y revisar el historial de commits de un repositorio local especificado.
                    </li>
                    <li>
                        Se añadió un menu contextual con la opcion de poder abrir un editor integrado en la aplicacion, con el proposito de poder editar archivos de codigo en una ruta temporal <i>(la cual se crea cuando a aplicacion se inicia y se elimina cuando la aplicacion finaliza)</i>.
                    </li>
                    <li>
                        Se agrego 1 paquete adicional para su instalacion a la lista de modulos <strong>(Body-parser)</strong>.
                    </li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>1.4.0</td>
            <td>2024-07-14</td>
            <td>
                <ul>
                    <li>
                        Se añadió un visor de registros el cuál muestra el comando utilizado para cada tarea de instalación de modulos NPM por parte del programa <i>(se actualizá cada 1 segundo)</i>.
                    </li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>1.3.0</td>
            <td>2024-07-13</td>
            <td>
                <ul>
                    <li>
                        Se optimizó el tiempo de carga de cada una de las versiones de paquetes de NPM.
                    </li>
                    <li>
                        Se agregarón 2 paquetes adicionales para su instalación a la lista de modulos <strong>(Nodemailer y Axios)</strong>.
                    </li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>1.2.1</td>
            <td>2024-06-11</td>
            <td>
                <ul>
                    <li>
                        Se modificó el apartado <strong>Información</strong> en la pantalla de la aplicacion, para incluir la versión de la aplicación.
                    </li>
                    <li>
                        Se agregarón 7 paquetes adicionales para su instalación a la lista de modulos <strong>(Cors , Cloudinary, Express-fileupload, fs-extra, jsonwebtoken, MySQL y Sequelize)</strong>.
                    </li>
                    <li>
                        Se modificó el widget para la entrada de argumentos a una lista desplegable con las opciones que se pueden seleccionar.
                    </li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>1.1.0</td>
            <td>2024-05-31</td>
            <td>
                <ul>
                    <li>    
                        Se añadió en el apartado <strong>Información</strong> en la pantalla de la aplicación, la versión de Node.js y NPM que se esta utilizando. <i>(Si la aplicación detecta una actualización de NPM se mostrará un mensaje en la pantalla de la aplicacion)</i>.
                    </li>
                    <li>
                        Se añadió un botón el cual abre una ventana que permite seleccionar los modulos que se desea instalar en la ruta seleccionada.
                    </li>
                    <li>
                        Se agergarón 6 paquetes adicionales para su instalación a parte de Express a la lista de modulos <strong>(Mongoose , Nodemon, Morgan, Json-server, Uuid y Bcrypt)</strong>.
                    </li>
                    <li>    
                        Se eliminó la opción <strong>Continuar sin confirmación</strong> y se añadierón 2 opciones adicionales<br>
                        <strong>Eliminar todo el contenido de la carpeta</strong> <i>(Si existe la carpeta indicada, eliminará todo lo que se encuentre en ella)</i> y, <br> <strong>Eliminar contenido tras un fallo</strong> <i>(Si ocurre un fallo en la instalación de un paquete, se eliminará todo el contenido de la carpeta indicada)</i>.
                    </li>
                </ul>
            </td>
        </tr>
</table>
