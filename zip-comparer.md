
# Comparador de ficheros Zips

Vamos a realizar un proyecto completo, incluyendo su diseño, código, pruebas y tests automáticos

Se trata de un comparador de archivos ZIPs, que nos mostraré visualmente las diferencias entre dos ficheros.

Usaremos [Grok](https://grok.com/share/bGVnYWN5_34d4e29c-5e6d-43c2-a3e7-5a22c8700074) como ayuda para la generación de código.

Implementaremos un sistema de versiones con 3 números:

* El primero indica la versión principal (será 0 en estas primeras frases hasta que tengamos una aplicación funcional).
* El segundo irá indicando los cambios de funcionalidad.
* El tercero, si existe, indicará corrección de errores.

He creado un[ repositorio github con el contenido](https://github.com/javacasm/CompZIPAS). En lugar de hacer versiones sobre el código, que sería lo habitual, he preferido mantener todos los ficheros con nombres que incluyen la versión para ver el proceso de creación del código.

Para subir el contenido del proyecto a github, he hecho lo siguiente, en la carpeta del proyecto:

* He inicializado un repositorio git con `git init`.
* He añadido los ficheros a git con `git add fichero`.
* Excluimos algunos fichero del sistema de versiones incluyéndolos en el fichero `.gitignore`
```
codigo/test1.zip
codigo/test2.zip
codigo/recent_zips.txt
.gitignore
```
* Hacemos un commit de los ficheros con `git commit -m "v0.1"`

## v0.0

Vamos a empezar viendo si existen herramientas similares en el mercado y si adecuan a nuestras necesidades.

```prompt
Tengo 2 ficheros zip del mismo directorio de momentos distintos, con miles de ficheros dentro, y quiero saber las diferencias entre ambos ¿hay alguna herramienta para hacerlo?
```

Sí, hay varias herramientas que pueden ayudarte a comparar las diferencias entre dos archivos ZIP, especialmente cuando contienen miles de ficheros. Dependiendo de tu sistema operativo y preferencias (GUI o línea de comandos), aquí te detallo algunas opciones recomendadas. La mayoría requieren extraer los archivos temporalmente para una comparación detallada, pero algunas pueden manejar ZIP directamente.

### Opciones GUI (Interfaz Gráfica)
- **[Beyond Compare](https://www.scootersoftware.com/)**   : Una herramienta potente y popular para comparar carpetas, archivos y archivos ZIP directamente. Puede expandir los ZIP sin extraerlos permanentemente y mostrar diferencias en contenido, nombres de archivos, tamaños y más. Es ideal para grandes volúmenes de datos. Disponible para Windows, macOS y Linux (versión de prueba gratuita, luego de pago).
- **[WinMerge](https://winmerge.org/?lang=es)** : Gratuita y de código abierto, excelente para comparar carpetas. Extrae los ZIP a directorios temporales y compara recursivamente. Muestra diferencias visuales de manera clara. Principalmente para Windows, pero hay ports para otros SO.
- **[ExCompare](https://www.easexp.com/excompare/)** : Diseñada específicamente para comparar carpetas y archivos como ZIP, RAR o 7Z. Muestra diferencias en una interfaz simple y es gratuita para uso básico.

### Opciones de Línea de Comandos (CLI)
- **zipcmp** : Una utilidad específica para comparar archivos ZIP sin extraerlos. Identifica diferencias en contenido, metadatos y estructura. Disponible en Linux (instálala con paquetes como `zipcmp` en repositorios), y es rápida para grandes archivos.
- **diff** (con unzip) : En Unix/Linux/macOS, extrae ambos ZIP a directorios temporales con `unzip archivo1.zip -d dir1` y `unzip archivo2.zip -d dir2`, luego usa `diff -r dir1 dir2` para una comparación recursiva. Para Windows, puedes usar Git Bash o WSL.
- **ZipDiff** (de .NET) : Una herramienta de código abierto en GitHub que compara ZIP directamente y soporta varios formatos de salida (como JSON). Requiere .NET instalado.

### Opciones con Programación
- **Python con módulo zipfile** : Si prefieres un script personalizado, puedes usar Python para listar y comparar el contenido de los ZIP sin extraer todo. Por ejemplo, un script simple que chequea hashes de archivos para detectar cambios.

Para grandes cantidades de ficheros, elige herramientas que eviten extraer todo si es posible (como Beyond Compare o zipcmp) para ahorrar tiempo y espacio. 

---

El resultado es bueno, encontrando las opciones más recomendadas, salvo una aplicación online, [zipcomparetool](https://zipcomparetool.com/) 

![](zipcomparetool.png)

Que en nuestro caso no nos sirve porque son ficheros demasiado grandes para subirlos online, además de las connotaciones de falta de privacidad de subir ficheros a una web... 

Tras ver que las opciones gratuitas WinMerge y exCompare son para Windows, nos decantamos por crear una aplicación.
## v0.1

Vamos a comenzar a generar el código

```prompt
Crea código para una aplicación visual en python para que compare dos ficheros zip. 

Muestra en la ventana 2 componentes lado a lado con el nombre de los ficheros, su tamaño y fecha, mostrando de distintos colores si son distintos, pudiendo navegar recursivamente los ficheros
```

![](./images/zip_comparer_v0.1.png)

El resultado es una aplicación operativa y que cumple su función. Es un buen punto de partida para ir añadiendo opciones y adecuada para aprender.
## v0.2

```prompt
Vamos a crear una visualización con 2 árboles, colocados visualmente uno al lado del otro. 

Al movernos por uno se moverá el otro, manteiendo los ficheros alineados, si un fichero sólo está en uno de los ficheros en el arbol asociado al otro fichero se verá una línea en blanco.

Añade trazas usando logging y la consola, pudiendo configurar el nivel de log que se envía a la consola, a medida que se va recuperando información de los ficheros.
Genera 2 ficheros zip de prueba para probar la funcionalidad
```

![](./images/zip-comparer_v0.2.png)



Con errores...

![](zip-comparar_error_v0.2.png)


# v0.3

- Etiqueta cada versión con un número, la próxima será la 0.3.0, cambiando el segundo número con funcionalidad nueva y el tercero para corrección de errores
- Incluye un comentario al principio del código indicado la versión
- Genera ficheros zip de prueba más complejos    
- Marca los directorios con colores diferentes cuando contienen diferencias y sin color cuando son iguales    
- Muestra la leyenda de colores y su significado
- Pon los controles de los selecctores de ficheros en una misma línea, cada uno encima de su tree

![](zip-comparer_v0.3.1.png)


## v0.4

Tras 6 versiones...  se solucionan los problemas de sincronización
```prompts

- No funciona la sincronización entre los dos treeviews, pero al menos no hay bucle infinito. Crea una variable en el código para activar/desactivar la sincronización
- Traduce al castellano los comentarios y las etiquetas
- Utiliza un color de texto diferente (gris claro) para los elementos no que no están en uno de los zips
- Guarda los ficheros recientes usados anteriormente y cambia el selector de finchero por un combo con los anteriores zips usados
- Corrección: muestras los textos de la leyenda con su correspondiente color background  
...

- Ya funciona la sinconización, falta que al desplegar un directorio en uno se despliegue el equivalente en el otro

- No guardes en la lista de recientes los ficheros utilizados repetidos

...

Aunque se establezca como nivel de log ERROR, se siguen mostrando por consola los mensajes de DEBUG ¿no deberían de mostrarse sólo lode nivel error y critical?

...

Vamos a mover las trazas sobre el número de archivos de los zip y el nymero de miembros únicos al nivel Info,
```

![](./images/zip-comparer_v0.4.5.png)
## v0.5 - Future

* Seleccionar comparación por fechas, tamaño, contenido (se marcan como activas o no en la leyenda)
* Detalles de cada uno de los zips: tamaño, fecha, número de ficheros ¿algo más?
* ¿Cachear la información de los zips?
* Tamaño de las columnas ajustado al contenido
* Menú contextual con:
	* Visores de diferencias:
		* Texto (txt, md)
		* Imágenes
	* Mostrar información de los directorios: número de ficheros/directorios ¿tamaño? ¿fecha?  
	* Desplegar todo el árbol
  