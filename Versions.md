<h1 align="center">Historial de versiones</h1>
<div align="center">
    <p>Versión actual</p>
    <img src="https://img.shields.io/badge/Version-2.0.0-blue.svg" alt="Versión de la app">
</div>
<h2 align="center">Tabla de versiones y cambios</h2>
<table>
    <thead>
        <tr>
            <th>Versión</th>
            <th>Fecha de modificación</th>
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
                        Se cambió el estilo de la UI de la aplicación.
                    </li>
                    <li>
                        Se añadió un botón <strong>git</strong> que abre una ventana para clonar un repositorio de git en la ruta seleccionada, hacer commits y revisar el historial de commits de un repositorio local especificado.
                    </li>
                    <li>
                        Se añadió un menú contextual con la opción de abrir un editor integrado en la aplicación con el propósito de editar archivos de código en una ruta temporal <i>(la cual se crea al iniciar la aplicación y se elimina al finalizarla)</i>.
                    </li>
                    <li>
                        Se agregó un paquete adicional para su instalación a la lista de módulos <strong>(Body-parser)</strong>.
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
                        Se añadió un visor de registros que muestra el comando utilizado para cada tarea de instalación de módulos NPM por parte del programa <i>(se actualiza cada 1 segundo)</i>.
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
                        Se agregaron 2 paquetes adicionales para su instalación a la lista de módulos <strong>(Nodemailer y Axios)</strong>.
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
                        Se modificó el apartado <strong>Información</strong> en la pantalla de la aplicación para incluir la versión de la aplicación.
                    </li>
                    <li>
                        Se agregaron 7 paquetes adicionales para su instalación a la lista de módulos <strong>(Cors, Cloudinary, Express-fileupload, fs-extra, jsonwebtoken, MySQL y Sequelize)</strong>.
                    </li>
                    <li>
                        Se modificó el widget para la entrada de argumentos a una lista desplegable con las opciones seleccionables.
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
                        Se añadió en el apartado <strong>Información</strong> en la pantalla de la aplicación la versión de Node.js y NPM que se está utilizando. <i>(Si la aplicación detecta una actualización de NPM, se mostrará un mensaje en la pantalla de la aplicación)</i>.
                    </li>
                    <li>
                        Se añadió un botón que abre una ventana para seleccionar los módulos que se desean instalar en la ruta seleccionada.
                    </li>
                    <li>
                        Se agregaron 6 paquetes adicionales para su instalación aparte de Express a la lista de módulos <strong>(Mongoose, Nodemon, Morgan, Json-server, Uuid y Bcrypt)</strong>.
                    </li>
                    <li>
                        Se eliminó la opción <strong>Continuar sin confirmación</strong> y se añadieron 2 opciones adicionales:<br>
                        <strong>Eliminar todo el contenido de la carpeta</strong> <i>(si existe la carpeta indicada, se eliminará todo lo que se encuentre en ella)</i> y <br>
                        <strong>Eliminar contenido tras un fallo</strong> <i>(si ocurre un fallo en la instalación de un paquete, se eliminará todo el contenido de la carpeta indicada)</i>.
                    </li>
                </ul>
            </td>
        </tr>
    </tbody>
</table>