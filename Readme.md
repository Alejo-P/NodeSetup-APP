<h1>NodeSetup-APP</h1>

<div align="center">
    <img src="https://img.shields.io/badge/Version-1.2.1-blue.svg" alt="Version de la app">
</div>
<h2>Descripción</h2>

<!--Reservado para la imagen-->
<div style="display:flex;" align = "center">
    <div>
        <img
        src="https://github.com/Alejo-P/NodeSetup-APP/assets/150528715/557f2356-4170-428c-8c8c-5a22e668fb6d"
        alt="NodeSetup-APP"
        style="width:90%; height:auto;"
        >
    </div>
    <div>
        <img
        src="https://github.com/Alejo-P/NodeSetup-APP/assets/150528715/cc092be2-3661-4f7f-8931-27e322b6b1a6"
        alt="NodeSetup-APP"
        style="width:80%; height:auto;"
        >
    </div>
</div>

<p>NodeSetup es una aplicacion GUI de escritorio desarrollada con Python, la aplicacion permite estabelcer e inicializar un proyecto con Node.js en un directorio seleccionado e instalar paquetes que el usuario escoja, a continuacion se explica cada parte de los cmoponentes GUI de la app:</p>

<h3>1. Ventana Principal</h3>

<p>La ventana principal de la aplicacion cuenta con las siguientes opciones:</p>

<div align = "center">
    <img
    src="https://github.com/Alejo-P/NodeSetup-APP/assets/150528715/618ca78f-ede2-4fce-8786-d30df888e42f"
    alt="NodeSetup-APP"
    style="width:80%; height:auto;"
    >
</div>

<ul>
    <li>
        <h4>1. Seleccionar Directorio</h4>
        <p>Cuenta con un entry para ingresar la ruta deseada y un boton llamado <strong>"Explorar"</strong> que permite al usuario seleccionar el directorio donde se creara el proyecto de Node.js.</p>
    </li>
    <li>
        <h4>2. Configuraciones adicionales</h4>
        <p>Cuadros de seleccion multiple permiten al usuario seleccionar algunos parametros adicionames a realizar:</p>
        <ul>
            <li>
                <strong>Eliminar todo el contenido de la carpeta</strong>
                <p>Esta opcion eliminara todo el contenido de la carpeta antes de crear el proyecto.<br>
                <strong>(Se recomienda revisar el contenido de la carpeta y asegurarse de que este vacia o el contenido no sea importante antes de marcar esta opcion)</strong></p>
            </li>
            <li>
                <strong>Crear ruta si no existe</strong>
                <p>Esta opcion creara la ruta seleccionada si no existe, de lo contrario se creara el proyecto en la ruta seleccionada</p>
            </li>
            <li>
                <strong>Eliminar contenido tras un fallo</strong>
                <p>Esta opcion eliminara el contenido de la carpeta en caso de que ocurra un fallo durante la creacion del proyecto, como un problema al instalar un paquete</p>
            </li>
            <li>
                <strong>Detener en caso de fallo</strong>
                <p>Esta opcion detendra la creacion del proyecto en caso de que ocurra un fallo durante la creacion del proyecto, si se la desmarca la apicacion continuará con la instalación omitiendo el fallo</p>
            </li>
        </ul>
    </li>
    <li>
        <h4>3. Informacion sobre versiones</h4>
        <p>En la parte superior de la ventana  bajo el titulo se muestra la version de la aplicacion, la version de Node.js y la version de NPM que estan instalados actualmente</p>
    </li>
    <li>
        <h4>4. Opciones para la inicializacion del proyecto</h4>
        <p>En este apartado se encuentran operaciones adicionales que se pueden realiar una vez inicializado el proyecto, como la instalacion de paquetes externos, crear la carpeta <code>'src/'</code> y su contenido <strong>(en el programa esta opcion se llama 'Crear archivos adicionales')</strong> y abrir el proyecto con VS Code al finalizar la creacion del proyecto</p>
    </li>
    <li>
        <h4>5. Progreso de la tarea</h4>
        <p>En la parte inferior del programa se ubica una barra de progreso que indica el progreso que lleva la aplicacion en la creacion del proyecto, y en la etiqueta <strong>Descripcion</strong> se especifica la tarea que se esta llevando a cabo</p>
    </li>
    <li>
        <h4>6. Boton de creacion del proyecto y salir de la aplicacion</h4>
        <p>El boton <strong>"Crear"</strong> inicia el proceso de creacion del proyecto, una vez que se ha seleccionado el directorio y se han marcado las opciones deseadas, y el boton <strong>"Salir"</strong> cierra el programa</p>
    </li>
</ul>

<h3>2. Ventana de seleccion de modulos</h3>

<p>Cuando el usuario ha presionado el boton <strong>"Instalar modulos"</strong> se creará una ventana nueva en la cual podra escoger los modulos que desea instalar en el proyecto, la ventana cuenta con las siguientes opciones:</p>

<div align = "center">
    <img
    src="https://github.com/Alejo-P/NodeSetup-APP/assets/150528715/b2240646-e2c1-4ebe-9c6e-8f926cea31e3"
    alt="NodeSetup-APP"
    style="width:80%; height:auto;"
    >
</div>

<ul>
    <li>
        <h4>1. Selecion de modulos</h4>
        <p>En esta columna se encuentran cuadros de marcado que el usuario puede marcar para seleccionar el modulo que desee incluir en la creacion del proyecto</p>
        <p>Comando usado:</p>
    </li>
    <li>
        <h4>2. Nombre del modulo</h4>
        <p>En esta columna se muestra el nombre del modulo que se puede instalar en el proyecto</p>
    </li>
    <li>
        <h4>3. Argumentos de instalacion para el modulo</h4>
        <p>En esta columna se muestra listas desplegables con argumentos adicionales para la instalacion del modulo, el valor predeterminado es la cadena vacia, lo que indica que el modulo no tiene argumentos adicionales para su instalación</p>
    </li>
    <li>
        <h4>4. Versiones disponibles para cada modulo</h4>
        <p>En esta columna se muestra una lista desplegable que permite escojer la version para instalar el modulo, la version mas reciente del modulo es el valor predeterminado</p>
    </li>
    <li>
        <h4>5. Instalacion global del modulo</h4>
        <p>En esta columna se muestra cuadros de marcado que permiten seleccionar que modulos instalar globalmente</p>
    </li>
</ul>

<p>Al final la estructura del comando que se ejecutara
para cada modulo es el siguiente:</p>

<pre><code>
    npm install [-g] [nombre del modulo]@[version] [argumentos de instalacion]
</code></pre>

<p>
    Donde:
    <ul>
        <li>
            <strong>[-g]</strong> es un argumento opcional que indica que el modulo se instalará globalmente
        </li>
        <li>
            <strong>[nombre del modulo]</strong> es el nombre del modulo que se instalará
        </li>
        <li>
            <strong>[version]</strong> es la version del modulo que se instalará
        </li>
        <li>
            <strong>[argumentos de instalacion]</strong> son argumentos adicionales que se pueden pasar al comando de instalacion del modulo
        </li>
    </ul>
</p>