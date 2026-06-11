# Importamos las herramientas de Flask para crear la app web, renderizar plantillas,
# manejar peticiones, redirecciones, sesiones, mensajes flash y respuestas personalizadas
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
# Importamos funciones para encriptar y verificar contraseñas de forma segura
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash
# Importamos nuestras funciones para inicializar y conectar la base de datos
from database import init_db, get_db
# Importamos FPDF para poder generar certificados/diplomas en formato PDF
from fpdf import FPDF
import io

# Creamos la aplicación Flask
app = Flask(__name__)
# Definimos una clave secreta usada para firmar las cookies de sesión
app.secret_key = 'clave_maestria_v6'
# Creamos la base de datos y las tablas si todavía no existen
init_db()

# --- ORGANIZACIÓN DE CURSOS POR CATEGORÍA ---
# Este diccionario agrupa el nombre de cada curso dentro de su categoría general.
# Se usa tanto para mostrar los cursos en /categoria/<tipo> como para calcular
# el total de cursos disponibles (necesario para el sistema de logros).
CATEGORIAS = {
    'arte': ['Pintura', 'Escultura', 'Teatro', 'Danza', 'Música'],
    'oficios': ['Carpintería', 'Cocina', 'Costura', 'Mecánica', 'Electricidad'],
    'cultura': ['Historia de México', 'Literatura', 'Cine', 'Paz y sociedad', 'Gastronomía regional'],
    'informatica': ['Computación básica', 'Excel Pro', 'Diseño web', 'Redes sociales']
}

# --- ICONOS Y COLORES PARA LAS TARJETAS DE CADA CURSO ---
# A cada curso se le asigna un icono (de Bootstrap Icons) y un color de
# degradado para que las tarjetas de /categoria/<tipo> se vean más
# creativas y se puedan identificar visualmente de un vistazo.
ICONOS_CURSOS = {
    'Pintura': ('bi-palette-fill', "#5fcfff", '#feb47b'),
    'Escultura': ('bi-gem', '#8e9eab', '#eef2f3'),
    'Teatro': ('bi-mask', '#7f00ff', '#e100ff'),
    'Danza': ('bi-music-note-beamed', '#f857a6', '#ff5858'),
    'Música': ('bi-soundwave', '#43cea2', '#185a9d'),
    'Carpintería': ('bi-tools', '#a8741a', '#e2c290'),
    'Cocina': ('bi-egg-fried', '#ff9966', '#ff5e62'),
    'Costura': ('bi-scissors', '#834d9b', '#d04ed6'),
    'Mecánica': ('bi-gear-wide-connected', '#485563', '#29323c'),
    'Electricidad': ('bi-lightning-charge-fill', '#f7971e', '#ffd200'),
    'Historia de México': ('bi-bank', '#ad5389', '#3c1053'),
    'Literatura': ('bi-book-half', '#56ab2f', '#a8e063'),
    'Cine': ('bi-camera-reels-fill', '#414345', '#232526'),
    'Paz y sociedad': ('bi-people-fill', '#1b4332', '#52b788'),
    'Gastronomía regional': ('bi-cup-hot-fill', '#f46b45', '#eea849'),
    'Computación básica': ('bi-laptop-fill', '#2193b0', '#6dd5ed'),
    'Excel Pro': ('bi-file-earmark-spreadsheet-fill', '#11998e', '#38ef7d'),
    'Diseño web': ('bi-code-slash', '#5f2c82', '#49a09d'),
    'Redes sociales': ('bi-hash', '#36d1dc', '#5b86e5'),
}

# --- SISTEMA DE LOGROS (20 EN TOTAL) ---
# Cada logro se desbloquea cuando el usuario completa cierta cantidad de
# cursos distintos (umbral). El total de cursos disponibles se calcula
# sumando todos los cursos listados en CATEGORIAS (19 cursos = 19 logros
# de progreso). El logro número 20 es un "logro final" que se desbloquea
# únicamente cuando TODOS los demás logros (y por lo tanto todos los
# cursos) ya están completados, y es el que habilita el certificado final.
TOTAL_CURSOS = sum(len(lista) for lista in CATEGORIAS.values())

LOGROS = [
    {'umbral': 1, 'icono': '🌱', 'nombre': 'Primer Paso', 'desc': 'Completa tu primer curso.'},
    {'umbral': 2, 'icono': '📖', 'nombre': 'Aprendiz Curioso', 'desc': 'Completa 2 cursos.'},
    {'umbral': 3, 'icono': '🔥', 'nombre': 'En Racha', 'desc': 'Completa 3 cursos.'},
    {'umbral': 4, 'icono': '🎯', 'nombre': 'Enfocado', 'desc': 'Completa 4 cursos.'},
    {'umbral': 5, 'icono': '⭐', 'nombre': 'Dedicado', 'desc': 'Completa 5 cursos.'},
    {'umbral': 6, 'icono': '🎨', 'nombre': 'Alma Creativa', 'desc': 'Completa 6 cursos.'},
    {'umbral': 7, 'icono': '💪', 'nombre': 'Constante', 'desc': 'Completa 7 cursos.'},
    {'umbral': 8, 'icono': '🚀', 'nombre': 'En Movimiento', 'desc': 'Completa 8 cursos.'},
    {'umbral': 9, 'icono': '🏅', 'nombre': 'Comprometido', 'desc': 'Completa 9 cursos.'},
    {'umbral': 10, 'icono': '🏆', 'nombre': 'Mitad del Camino', 'desc': 'Completa 10 cursos.'},
    {'umbral': 11, 'icono': '🌟', 'nombre': 'Brillante', 'desc': 'Completa 11 cursos.'},
    {'umbral': 12, 'icono': '📚', 'nombre': 'Sabiduría en Aumento', 'desc': 'Completa 12 cursos.'},
    {'umbral': 13, 'icono': '🦾', 'nombre': 'Imparable', 'desc': 'Completa 13 cursos.'},
    {'umbral': 14, 'icono': '🧠', 'nombre': 'Mente Abierta', 'desc': 'Completa 14 cursos.'},
    {'umbral': 15, 'icono': '🥇', 'nombre': 'Casi Experto', 'desc': 'Completa 15 cursos.'},
    {'umbral': 16, 'icono': '🛡️', 'nombre': 'Resiliente', 'desc': 'Completa 16 cursos.'},
    {'umbral': 17, 'icono': '💎', 'nombre': 'Excelencia', 'desc': 'Completa 17 cursos.'},
    {'umbral': 18, 'icono': '🌈', 'nombre': 'Renacer', 'desc': 'Completa 18 cursos.'},
    {'umbral': 19, 'icono': '🎓', 'nombre': 'Maestro Integral', 'desc': f'Completa los {TOTAL_CURSOS} cursos disponibles.'},
    {'umbral': TOTAL_CURSOS, 'icono': '👑', 'nombre': 'Leyenda de Semanas de Paz', 'desc': 'Desbloquea todos los logros y obtén tu certificado final.', 'final': True},
]

# --- DATOS DE LOS CURSOS ---
# Diccionario principal: cada clave es el nombre del curso y su valor contiene
# la información teórica ('info'), los videos de apoyo ('videos') y el
# examen final de opción múltiple ('preguntas') con la respuesta correcta ('ok').
CURSOS_DATA = {
   # Curso de Pintura: técnicas básicas de color, forma y textura
   'Pintura': {
    'info': 'Bienvenido(a) a este curso de pintura.\nAquí no importa tu experiencia previa, edad o situación actual. Este es un espacio para aprender, expresarte y desarrollar una habilidad que puede convertirse en una forma de trabajo, disciplina y crecimiento personal.\nLa pintura no solo es arte, también es una herramienta para concentrarte, relajarte y construir algo con tus propias manos. Paso a paso, vas a aprender desde lo más básico hasta poder crear tus propias obras.\n\nLa pintura es una forma de expresión visual que utiliza colores, formas y técnicas para representar ideas, emociones o imágenes.\nSe trabaja principalmente con:\nColor,Forma,Luz,sombra yTextura',
    'videos': [
        {'titulo': 'Técnicas de pintura capitulo 1 - YouTube', 'url': 'https://www.youtube.com/embed/f2jUpqIOI1E?si=nj7ybPqzLRSj2rOR'},
        {'titulo': 'Técnicas de pintura capitulo 2 - YouTube', 'url': 'https://www.youtube.com/embed/juF5Xq9CgdM?si=e08oqffKPzGJFASe'},
        {'titulo': 'Técnicas de pintura capitulo 3 - YouTube', 'url': 'https://www.youtube.com/embed/h9LStKUwVXs?si=Vnc46Dc1ED8nk-1W'},
        {'titulo': 'Técnicas de pintura capitulo 4 - YouTube', 'url': 'https://www.youtube.com/embed/cj1YMnsUmuU?si=ahaD-iT3GBNBqzW4'},
        {'titulo': 'Técnicas de pintura capitulo 5 - YouTube', 'url': 'https://www.youtube.com/embed/YQKsLX4cy4c?si=eaqe325k6w4TLbd5'},
        {'titulo': 'Técnicas de pintura capitulo 6 - YouTube', 'url': 'https://www.youtube.com/embed/Y0zkt66UQRo?si=ytty65UfSOpcgjU4'}
    ],
    'preguntas': [
    {'p': '¿Cuál es una técnica básica que se enseña al inicio de la pintura?', 'a': 'Escultura', 'b': 'Mezcla de colores', 'c': 'Grabado', 'ok': 'b'},
    {'p': '¿Qué se logra al mezclar colores primarios?', 'a': 'Colores metálicos', 'b': 'Colores transparentes', 'c': 'Colores secundarios', 'ok': 'c'},
    {'p': '¿Para qué se utiliza la técnica de degradado?', 'a': 'Para dibujar líneas rectas', 'b': 'Para crear transiciones suaves entre colores', 'c': 'Para recortar figuras', 'ok': 'b'},
    {'p': '¿Qué herramienta es más común en las técnicas básicas de pintura?', 'a': 'Pincel', 'b': 'Tijeras', 'c': 'Regla', 'ok': 'a'},
    {'p': '¿Qué permite la técnica de luz y sombra en una pintura?', 'a': 'Hacer la pintura más rápida', 'b': 'Evitar usar colores', 'c': 'Dar volumen y profundidad', 'ok': 'c'},
    {'p': '¿Qué es la textura en pintura?', 'a': 'El tamaño del lienzo', 'b': 'La sensación visual o táctil de una superficie', 'c': 'El tipo de marco', 'ok': 'b'},
    {'p': '¿Qué sucede si agregas blanco a un color?', 'a': 'Se aclara el color', 'b': 'Se oscurece el color', 'c': 'Desaparece el color', 'ok': 'a'},
    {'p': '¿Cuál es el objetivo de practicar diferentes técnicas?', 'a': 'Terminar más rápido', 'b': 'Usar menos materiales', 'c': 'Mejorar habilidades y estilo propio', 'ok': 'c'},
    {'p': '¿Qué se recomienda hacer antes de una pintura final?', 'a': 'Comprar más pinceles', 'b': 'Bocetos o pruebas', 'c': 'Tirar la pintura', 'ok': 'b'},
    {'p': '¿Qué se busca al final del aprendizaje de estas técnicas?', 'a': 'Copiar exactamente al maestro', 'b': 'Solo ver videos', 'c': 'Crear obras propias', 'ok': 'c'}
        ]
    },
    # Curso de Escultura: trabajo con volumen, materiales y modelado
    'Escultura': {
'info': 'Bienvenido(a) a este curso de escultura.\nAquí aprenderás a transformar materiales en obras tridimensionales mediante técnicas manuales y creativas.\nNo importa tu experiencia, este curso está diseñado para desarrollar tu creatividad, paciencia y precisión.\n\nLa escultura es una forma de arte que trabaja con volumen y espacio.\nSe utilizan materiales como barro, madera, yeso o piedra.\n\nSe trabaja principalmente con:\nForma,Volumen,Textura,Proporción yEquilibrio',
'videos': [
    {'titulo': 'Que son las esculturas y como se hacen- YouTube', 'url': 'https://www.youtube.com/embed/27l6RulFhfY?si=PpEIpLS6E1mTR0mC'},
    {'titulo': 'Las esculturas más famosas del mundo- YouTube', 'url': 'https://www.youtube.com/embed/tfoEheeVSIY?si=LefIbgdy-dlZRmLQ'},
    {'titulo': 'Tipos de escultura- YouTube', 'url': 'https://www.youtube.com/embed/-QdAvPtKxnE?si=k1e50ODv3f-WcX7Q'},
    ],
'preguntas': [
{'p': '¿Qué define a la escultura?', 'a': 'El color', 'b': 'El volumen', 'c': 'El sonido', 'ok': 'b'},
{'p': '¿Qué material es común?', 'a': 'Barro', 'b': 'Papel', 'c': 'Tela', 'ok': 'a'},
{'p': '¿Qué es volumen?', 'a': 'Espacio ocupado', 'b': 'Color', 'c': 'Luz', 'ok': 'a'},
{'p': '¿Qué permite la textura?', 'a': 'Sensación visual', 'b': 'Velocidad', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué es proporción?', 'a': 'Relación de tamaños', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué herramienta se usa?', 'a': 'Cincel', 'b': 'Pluma', 'c': 'Regla', 'ok': 'a'},
{'p': '¿Qué es modelado?', 'a': 'Dar forma', 'b': 'Pintar', 'c': 'Cortar papel', 'ok': 'a'},
{'p': '¿Qué desarrolla?', 'a': 'Creatividad', 'b': 'Velocidad', 'c': 'Memoria', 'ok': 'a'},
{'p': '¿Qué es equilibrio?', 'a': 'Estabilidad', 'b': 'Color', 'c': 'Tamaño', 'ok': 'a'},
{'p': '¿Qué busca el escultor?', 'a': 'Crear formas', 'b': 'Escribir', 'c': 'Cortar papel', 'ok': 'a'}
]
},

# Curso de Teatro: actuación, voz y expresión corporal
'Teatro': {
'info': 'Bienvenido(a) a este curso de teatro.\nAquí aprenderás a expresarte mediante la actuación, la voz y el movimiento.\nDesarrollarás confianza, creatividad y habilidades de comunicación.\n\nEl teatro es un arte escénico donde se representan historias frente a un público.\n\nSe trabaja con:\nVoz,Expresión corporal,Interpretación,Emoción yEscena',
'videos': [
    {'titulo': 'que es el teatro?- YouTube', 'url': 'https://www.youtube.com/embed/OdzNr0pzoC0?si=z5tmlSIk8Lf7k_wi'},
    {'titulo': 'El guion teatral y sus elementos- YouTube', 'url': 'https://www.youtube.com/embed/OZerBzxysj4?si=QL5xZHbSzxDG-k3I'},
    {'titulo': 'Impacto del teatro en la sociedad- YouTube', 'url': 'https://www.youtube.com/embed/JI0WndSbVis?si=ie2UK5YI3osPz7Ca'},
    {'titulo': '- YouTube', 'url': ''},
    ],
'preguntas': [
{'p': '¿Qué es el teatro?', 'a': 'Arte escénico', 'b': 'Deporte', 'c': 'Ciencia', 'ok': 'a'},
{'p': '¿Qué se usa en teatro?', 'a': 'Voz', 'b': 'Martillo', 'c': 'Pintura', 'ok': 'a'},
{'p': '¿Qué es actuación?', 'a': 'Interpretar', 'b': 'Leer', 'c': 'Escribir', 'ok': 'a'},
{'p': '¿Qué desarrolla?', 'a': 'Confianza', 'b': 'Fuerza', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué es escena?', 'a': 'Lugar de acción', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se expresa?', 'a': 'Emociones', 'b': 'Números', 'c': 'Datos', 'ok': 'a'},
{'p': '¿Qué es guion?', 'a': 'Texto', 'b': 'Color', 'c': 'Herramienta', 'ok': 'a'},
{'p': '¿Qué requiere?', 'a': 'Práctica', 'b': 'Fuerza', 'c': 'Velocidad', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Comunicación', 'b': 'Peso', 'c': 'Tamaño', 'ok': 'a'},
{'p': '¿Qué es personaje?', 'a': 'Rol actuado', 'b': 'Objeto', 'c': 'Lugar', 'ok': 'a'}
]
},

# Curso de Danza: movimiento, ritmo y coordinación
'Danza': {
'info': 'Bienvenido(a) a este curso de danza.\nAprenderás a expresarte mediante el movimiento del cuerpo.\nDesarrollarás coordinación, ritmo y disciplina.\n\nLa danza es una forma de expresión artística acompañada de música.\n\nSe trabaja con:\nRitmo,Coordinación,Movimiento,Expresión yEquilibrio',
'videos': [
    {'titulo': 'Que es la danza- YouTube', 'url': 'https://www.youtube.com/embed/_tTikl4sEnw?si=y990Lzeo_f-07UEe'},
    {'titulo': 'Todos los beneficios de la danza- YouTube', 'url': 'https://www.youtube.com/embed/mEhJfNgKhIY?si=bwrMYNG3h4HmPPQS'},
    {'titulo': 'Breve historia de la Danza- YouTube', 'url': 'https://www.youtube.com/embed/zULkOuv0U6g?si=LfSGCMWb-9RKK7cZ'},
    
    
],
'preguntas': [
{'p': '¿Qué es danza?', 'a': 'Movimiento con ritmo', 'b': 'Escritura', 'c': 'Cálculo', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Coordinación', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué es ritmo?', 'a': 'Patrón de tiempo', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué expresa?', 'a': 'Emociones', 'b': 'Datos', 'c': 'Códigos', 'ok': 'a'},
{'p': '¿Qué requiere?', 'a': 'Práctica', 'b': 'Papel', 'c': 'Tinta', 'ok': 'a'},
{'p': '¿Qué es equilibrio?', 'a': 'Estabilidad', 'b': 'Velocidad', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué acompaña?', 'a': 'Música', 'b': 'Silencio', 'c': 'Texto', 'ok': 'a'},
{'p': '¿Qué es coreografía?', 'a': 'Secuencia', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Flexibilidad', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Cuerpo', 'b': 'Lápiz', 'c': 'Regla', 'ok': 'a'}
]
},

# Curso de Historia de México: etapas históricas y pensamiento crítico
'Historia de México': {
'info': 'Bienvenido(a) a este curso de Historia de México.\nAprenderás los principales acontecimientos que han formado el país.\nDesarrollarás pensamiento crítico y comprensión del pasado.\n\nSe estudian etapas como:\nÉpoca prehispánica,Conquista,Colonia,Independencia yRevolución.\n\nSe trabaja con:\nFechas,Procesos históricos,Personajes yContexto social',
'videos': [
    {'titulo': '✅✅✅Historia de México- YouTube', 'url': 'https://www.youtube.com/embed/qkw3ujp4DrY?si=KC6ywEObW3bCimWY'},
    {'titulo': 'Toda La Historia De México Para Dormir- YouTube', 'url': 'https://www.youtube.com/embed/FQcUTLLSOC0?si=0Y1wGgcM4UqOgzGI'},
    {'titulo': 'LA HISTORIA DE MÉXICO: todo lo que debes saber en 45 minutos- YouTube', 'url': 'https://www.youtube.com/embed/sKTy8hrPvR8?si=aL_XKy_e6fWqpuH1'},
    
           ],
'preguntas': [
{'p': '¿Qué estudia la historia?', 'a': 'El pasado', 'b': 'El futuro', 'c': 'El espacio', 'ok': 'a'},
{'p': '¿Qué fue la independencia?', 'a': 'Separación', 'b': 'Unión', 'c': 'Guerra mundial', 'ok': 'a'},
{'p': '¿Qué es colonia?', 'a': 'Dominio', 'b': 'Fiesta', 'c': 'Juego', 'ok': 'a'},
{'p': '¿Qué se analizan?', 'a': 'Procesos', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'},
{'p': '¿Qué es revolución?', 'a': 'Cambio', 'b': 'Paz', 'c': 'Arte', 'ok': 'a'},
{'p': '¿Qué ayuda a entender?', 'a': 'El presente', 'b': 'Colores', 'c': 'Números', 'ok': 'a'},
{'p': '¿Qué se estudia?', 'a': 'Eventos', 'b': 'Pinturas', 'c': 'Códigos', 'ok': 'a'},
{'p': '¿Qué es contexto?', 'a': 'Entorno', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se analiza?', 'a': 'Causas', 'b': 'Colores', 'c': 'Sonidos', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Comprender', 'b': 'Olvidar', 'c': 'Ignorar', 'ok': 'a'}
]
},

# Curso de Computación Básica: uso de hardware, software y navegación
'Computación básica': {
'info': 'Bienvenido(a) a este curso de computación básica.\nAprenderás el uso correcto de la computadora y herramientas digitales.\nDesarrollarás habilidades tecnológicas esenciales.\n\nSe trabaja con:\nHardware,Software,Archivos,Sistemas yNavegación',
'videos': [
    {'titulo': 'computacion basica para principiantes- YouTube', 'url': 'https://www.youtube.com/embed/sjj54sdHJpQ?si=QFtyHCFUfdz9kyDP'},
    {'titulo': 'Computacion basica para adultos- YouTube', 'url': 'https://www.youtube.com/embed/jxAgVn73OWg?si=DsdwY_ffdM6tFDNG'},
    {'titulo': 'convinaciones secretas de tu teclado- YouTube', 'url': 'https://www.youtube.com/embed/rj-NLFhmZxM?si=f4qdqTWSWZjeS_-5'},
           ],
'preguntas': [
{'p': '¿Qué es hardware?', 'a': 'Parte física', 'b': 'Programa', 'c': 'Internet', 'ok': 'a'},
{'p': '¿Qué es software?', 'a': 'Programa', 'b': 'Teclado', 'c': 'Pantalla', 'ok': 'a'},
{'p': '¿Qué es archivo?', 'a': 'Documento digital', 'b': 'Cable', 'c': 'Monitor', 'ok': 'a'},
{'p': '¿Qué es sistema?', 'a': 'Conjunto', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué permite navegar?', 'a': 'Internet', 'b': 'Papel', 'c': 'Tinta', 'ok': 'a'},
{'p': '¿Qué es teclado?', 'a': 'Entrada', 'b': 'Salida', 'c': 'Color', 'ok': 'a'},
{'p': '¿Qué es mouse?', 'a': 'Control', 'b': 'Pantalla', 'c': 'Cable', 'ok': 'a'},
{'p': '¿Qué es carpeta?', 'a': 'Organizar', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es programa?', 'a': 'Aplicación', 'b': 'Cable', 'c': 'Pantalla', 'ok': 'a'},
{'p': '¿Qué desarrolla?', 'a': 'Habilidad digital', 'b': 'Fuerza', 'c': 'Peso', 'ok': 'a'}
]
},

# Curso de Costura: confección y reparación de prendas
'Costura': {
'info': 'Bienvenido(a) a este curso de costura.\nAprenderás a confeccionar prendas y reparar ropa.\nDesarrollarás precisión, creatividad y habilidades manuales.\n\nLa costura es el arte de unir telas mediante hilo y aguja o máquina.\n\nSe trabaja con:\nTela,Hilo,Aguja,Patrones yMedición',
'videos': [
    {'titulo': 'CURSO DE COSTURA PARA PRINCIPIANTES- YouTube', 'url': 'https://www.youtube.com/embed/binJXLpOdeo?si=OEb-qm_9Cp2ZbhVD'},
    {'titulo': 'PARTES DE LA MAQUINA DE COSER BASICA O FAMILIAR, PARA QUE SIRVEN Y ACCESORIOS QUE NECESITAS- YouTube', 'url': 'https://www.youtube.com/embed/T49rCHlSTd8?si=IU9mnszsiKCf3PtR'},
    {'titulo': 'APRENDE A COSER CON ESTOS EJERCICIOS BÁSICOS. Primeros pasos con tu máquina de coser.- YouTube', 'url': 'https://www.youtube.com/embed/eaRyRxJlRJQ?si=0u365h9wu2owhRvq'},
    {'titulo': 'Que debemos tener en cuenta al comprar una MÁQUINA DE COSER/Consejos y Guía para escoger la mejor.- YouTube', 'url': 'https://www.youtube.com/embed/pepn1i1HZCw?si=ex6WDTqWTG07YynV'},
    {'titulo': 'Limpieza y lubricación de su máquina de coser, un asunto importante de aprender Con Luzkita- YouTube', 'url': 'https://www.youtube.com/embed/u1y3fevgYmk?si=fsxBX2Hqd-Dh_x9Z'},
           ],
'preguntas': [
{'p': '¿Qué une la costura?', 'a': 'Telas', 'b': 'Madera', 'c': 'Metal', 'ok': 'a'},
{'p': '¿Qué herramienta se usa?', 'a': 'Aguja', 'b': 'Martillo', 'c': 'Taladro', 'ok': 'a'},
{'p': '¿Qué es un patrón?', 'a': 'Guía', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se usa con la aguja?', 'a': 'Hilo', 'b': 'Papel', 'c': 'Plástico', 'ok': 'a'},
{'p': '¿Qué permite medir?', 'a': 'Precisión', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se puede hacer?', 'a': 'Ropa', 'b': 'Muebles', 'c': 'Edificios', 'ok': 'a'},
{'p': '¿Qué desarrolla?', 'a': 'Habilidad manual', 'b': 'Fuerza', 'c': 'Velocidad', 'ok': 'a'},
{'p': '¿Qué es confección?', 'a': 'Crear prendas', 'b': 'Cortar madera', 'c': 'Pintar', 'ok': 'a'},
{'p': '¿Qué requiere?', 'a': 'Paciencia', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Precisión', 'b': 'Color', 'c': 'Ruido', 'ok': 'a'}
]
},

# Curso de Mecánica: funcionamiento y reparación de máquinas
'Mecánica': {
'info': 'Bienvenido(a) a este curso de mecánica.\nAprenderás el funcionamiento y reparación de máquinas y vehículos.\nDesarrollarás habilidades técnicas y de diagnóstico.\n\nLa mecánica estudia el movimiento y funcionamiento de sistemas.\n\nSe trabaja con:\nHerramientas,Motores,Diagnóstico yReparación',
'videos': [
    {'titulo': 'Mecánica Básica desde Cero | Clase de Mecánica completa para Principiantes 🚙🔧- YouTube', 'url': 'https://www.youtube.com/embed/rXlBDVEihOQ?si=PriP_9WCAGTiHjmj'},
    {'titulo': 'Cómo cambiar TODOS LOS LÍQUIDOS del Automóvil (aceite, transmisión, refrigerante, frenos y más)- YouTube', 'url': 'https://www.youtube.com/embed/YUFiOdxefbQ?si=3DNcIaFa4owK-QW6'},
    {'titulo': 'Todas Las HERRAMIENTAS NECESARIAS Para Abrir un TALLER MECANICO- YouTube', 'url': 'https://www.youtube.com/embed/8aArsTX5wVo?si=v2b-ClpAwNldS9iv'},
           ],
'preguntas': [
{'p': '¿Qué estudia la mecánica?', 'a': 'Movimiento', 'b': 'Color', 'c': 'Sonido', 'ok': 'a'},
{'p': '¿Qué se repara?', 'a': 'Motores', 'b': 'Papel', 'c': 'Tela', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Herramientas', 'b': 'Plumas', 'c': 'Reglas', 'ok': 'a'},
{'p': '¿Qué es diagnóstico?', 'a': 'Detectar fallas', 'b': 'Pintar', 'c': 'Medir', 'ok': 'a'},
{'p': '¿Qué requiere?', 'a': 'Conocimiento técnico', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se revisa?', 'a': 'Sistema', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué es motor?', 'a': 'Genera movimiento', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Reparar', 'b': 'Dibujar', 'c': 'Escribir', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Habilidad técnica', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se necesita?', 'a': 'Precisión', 'b': 'Color', 'c': 'Sonido', 'ok': 'a'}
]
},

# Curso de Electricidad: instalaciones eléctricas seguras
'Electricidad': {
'info': 'Bienvenido(a) a este curso de electricidad.\nAprenderás a trabajar con instalaciones eléctricas de forma segura.\nDesarrollarás habilidades técnicas y de prevención.\n\nLa electricidad estudia el flujo de energía eléctrica.\n\nSe trabaja con:\nCorriente,Circuitos,Voltaje ySeguridad',
'videos': [
    {'titulo': 'CURSO de ELECTRICIDAD-01► FUNDAMENTOS. [PASO a PASO]⚡- YouTube', 'url': 'https://www.youtube.com/embed/ZL4hYPMd4ik?si=6Jf_0Ss7UMvDOC85'},
    {'titulo': 'CABLEADO de una INSTALACION ELECTRICA de una casa paso a paso- YouTube', 'url': 'https://www.youtube.com/embed/7CQxUFt8kFg?si=SJ3tmDY-__kbVxm3'},
    {'titulo': 'INSTALACION ELECTRICA de una casa paso a paso, como armar el TABLERO ELECTRICO- YouTube', 'url': 'https://www.youtube.com/embed/ELqsMCCNlvA?si=LBQXaO6dw6D2qded'},
    {'titulo': 'Herramientas Basicas Para electricidad Domiciliaria ⚡- YouTube', 'url': 'https://www.youtube.com/embed/5Np4XDJdtUQ?si=zYY5t-Y-g64NrDlG'},
           ],
'preguntas': [
{'p': '¿Qué es electricidad?', 'a': 'Energía', 'b': 'Color', 'c': 'Sonido', 'ok': 'a'},
{'p': '¿Qué es corriente?', 'a': 'Flujo eléctrico', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué es voltaje?', 'a': 'Diferencia eléctrica', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es circuito?', 'a': 'Camino cerrado', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué es importante?', 'a': 'Seguridad', 'b': 'Color', 'c': 'Tamaño', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Cables', 'b': 'Tela', 'c': 'Papel', 'ok': 'a'},
{'p': '¿Qué puede causar riesgo?', 'a': 'Mala conexión', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué se mide?', 'a': 'Voltaje', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Instalar', 'b': 'Dibujar', 'c': 'Cortar', 'ok': 'a'},
{'p': '¿Qué se evita?', 'a': 'Accidentes', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'}
]
},

# Curso de Literatura: análisis y comprensión de textos
'Literatura': {
'info': 'Bienvenido(a) a este curso de literatura.\nAprenderás a analizar textos y desarrollar comprensión lectora.\nDesarrollarás imaginación y pensamiento crítico.\n\nLa literatura es el arte de la palabra escrita.\n\nSe trabaja con:\nLectura,Análisis,Interpretación yEscritura',
'videos': [
    {'titulo': '¿Qué es la LITERATURA? Características, tipos, géneros literarios, autores y sus obras- YouTube', 'url': 'https://www.youtube.com/embed/xOBTFL_Qeng?si=moDYGMrZ5EvnxVe6'},
    {'titulo': 'LITERATURA - INTRODUCCIÓN A LA LITERATURA- YouTube', 'url': 'https://www.youtube.com/embed/DU0IRxBFjFQ?si=PBiqPQoEeq5DI1rP'},
    
           ],
'preguntas': [
{'p': '¿Qué es literatura?', 'a': 'Arte escrito', 'b': 'Deporte', 'c': 'Ciencia', 'ok': 'a'},
{'p': '¿Qué se analiza?', 'a': 'Textos', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'},
{'p': '¿Qué desarrolla?', 'a': 'Imaginación', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué es interpretación?', 'a': 'Comprender', 'b': 'Cortar', 'c': 'Pintar', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Lenguaje', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es lectura?', 'a': 'Comprensión', 'b': 'Velocidad', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Comprensión', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué se escribe?', 'a': 'Textos', 'b': 'Colores', 'c': 'Sonidos', 'ok': 'a'},
{'p': '¿Qué es narración?', 'a': 'Contar historia', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Entender', 'b': 'Ignorar', 'c': 'Borrar', 'ok': 'a'}
]
},

# Curso de Cine: producción audiovisual y narrativa visual
'Cine': {
'info': 'Bienvenido(a) a este curso de cine.\nAprenderás sobre producción audiovisual y narrativa visual.\nDesarrollarás creatividad y análisis visual.\n\nEl cine es el arte de contar historias con imágenes en movimiento.\n\nSe trabaja con:\nGuion,Imagen,Sonido,Edición yNarrativa',
'videos': [
    {'titulo': 'CURSO GRATIS de iniciación a la VIDEOGRAFÍA | Parte 1: Grabación- YouTube', 'url': 'https://www.youtube.com/embed/xR0OnfVUhJA?si=7FTmTCA4A37LSonQ'},
    {'titulo': 'CURSO GRATIS de iniciación a la VIDEOGRAFÍA | Parte 2: Postproducción- YouTube', 'url': 'https://www.youtube.com/embed/rsSAyvjNJHM?si=eADrTUquAwpHuqWM'},
    {'titulo': 'CURSO GRATIS de iniciación a la VIDEOGRAFÍA | Parte 3: Q&A- YouTube', 'url': 'https://www.youtube.com/embed/lt-c1UYeRCM?si=BW15WlqT3grVvFBc'},
           ],
'preguntas': [
{'p': '¿Qué es cine?', 'a': 'Arte visual', 'b': 'Deporte', 'c': 'Juego', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Cámara', 'b': 'Martillo', 'c': 'Regla', 'ok': 'a'},
{'p': '¿Qué es guion?', 'a': 'Historia escrita', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es edición?', 'a': 'Organizar video', 'b': 'Pintar', 'c': 'Cortar papel', 'ok': 'a'},
{'p': '¿Qué incluye?', 'a': 'Sonido', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se cuenta?', 'a': 'Historia', 'b': 'Número', 'c': 'Dato', 'ok': 'a'},
{'p': '¿Qué se analiza?', 'a': 'Escenas', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'},
{'p': '¿Qué se desarrolla?', 'a': 'Creatividad', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué es narrativa?', 'a': 'Forma de contar', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Imagen', 'b': 'Tela', 'c': 'Madera', 'ok': 'a'}
]
},

# Curso de Gastronomía Regional: platillos típicos y tradición culinaria
'Gastronomía regional': {
'info': 'Bienvenido(a) a este curso de gastronomía regional.\nAprenderás sobre platillos típicos y tradiciones culinarias.\nDesarrollarás conocimiento cultural y habilidades en cocina.\n\nLa gastronomía regional representa la cultura de una zona.\n\nSe trabaja con:\nIngredientes,Tradición,Sabor yPreparación',
'videos': [
    {'titulo': 'Cocina Mexicana 1: Raíces de una tradición- YouTube', 'url': 'https://www.youtube.com/embed/HUuQfzmCOLM?si=nTAZEKYrUsE5ofLN'},
    {'titulo': 'Cocina prehispánica II- YouTube', 'url': 'https://www.youtube.com/embed/5JcYV-hc7oA?si=8JwAN_WfikdvaIqE'},
    {'titulo': 'THE BEST MEXICAN FOOD- YouTube', 'url': 'https://www.youtube.com/embed/hDjhoirqZQk?si=0NioiLSBUNTSeIQJ'},
           ],
'preguntas': [
{'p': '¿Qué representa?', 'a': 'Cultura', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Platillos', 'b': 'Formas', 'c': 'Colores', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Ingredientes', 'b': 'Papel', 'c': 'Tela', 'ok': 'a'},
{'p': '¿Qué es tradición?', 'a': 'Costumbre', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se desarrolla?', 'a': 'Cultura', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se prepara?', 'a': 'Comida', 'b': 'Madera', 'c': 'Metal', 'ok': 'a'},
{'p': '¿Qué es sabor?', 'a': 'Percepción', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué se conoce?', 'a': 'Región', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Recetas', 'b': 'Códigos', 'c': 'Planos', 'ok': 'a'},
{'p': '¿Qué se valora?', 'a': 'Tradición', 'b': 'Velocidad', 'c': 'Peso', 'ok': 'a'}
]
},

# Curso de Paz y Sociedad: convivencia, valores y resolución de conflictos
'Paz y sociedad': {
'info': 'Bienvenido(a) a este curso de paz y sociedad.\nAprenderás sobre convivencia, valores y resolución de conflictos.\nDesarrollarás habilidades sociales y emocionales.\n\nEste curso promueve la cultura de paz.\n\nSe trabaja con:\nRespeto,Empatía,Comunicación yValores',
'videos': [
    {'titulo': 'Cultura de paz- YouTube', 'url': 'https://www.youtube.com/embed/fk3CKXytKsE?si=BGqpbSk8ym4Kn79_'},
    {'titulo': '¿Qué es la cultura de paz?- YouTube', 'url': 'https://www.youtube.com/embed/X30UDx-H4zE?si=yL6yuMZnmp5_IyC5'},
    {'titulo': 'La Cultura de Paz y Transformación de Conflictos- YouTube', 'url': 'https://www.youtube.com/embed/1wGvkCdfrkg?si=MRTvKD58y-QSlb6i'},
           ],
'preguntas': [
{'p': '¿Qué promueve?', 'a': 'Paz', 'b': 'Conflicto', 'c': 'Ruido', 'ok': 'a'},
{'p': '¿Qué es respeto?', 'a': 'Valor', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es empatía?', 'a': 'Comprender', 'b': 'Ignorar', 'c': 'Borrar', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Convivencia', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué es comunicación?', 'a': 'Expresar', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué evita?', 'a': 'Conflictos', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'},
{'p': '¿Qué se desarrolla?', 'a': 'Valores', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Dialogar', 'b': 'Cortar', 'c': 'Pintar', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Armonía', 'b': 'Ruido', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Relaciones', 'b': 'Color', 'c': 'Forma', 'ok': 'a'}
]
},

# Curso de Carpintería: trabajo y diseño con madera
'Carpintería': {
'info': 'Bienvenido(a) a este curso de carpintería.\nAprenderás a trabajar la madera para crear objetos funcionales y decorativos.\nDesarrollarás precisión, creatividad y habilidades manuales.\n\nLa carpintería consiste en diseñar, cortar y ensamblar piezas de madera.\n\nSe trabaja con:\nMedición,Corte,Ensamble,Diseño yAcabado',
'videos': [
    {'titulo': 'CURSO GRATIS DE CARPINTERIA CLASE 1- YouTube', 'url': 'https://www.youtube.com/embed/5e290TCqf6o?si=AefrMisuALha-RPi'},
    {'titulo': 'URSO DE CARPINTERIA - ANEXO 1 - DISCOS DE CORTE- YouTube', 'url': 'https://www.youtube.com/embed/RukJ6HcVtJU?si=a5kxBIpb0uDyR0e6'},
    {'titulo': 'CURSO GRATIS DE CARPINTERIA - CLASE 2 - HERRAMIENTAS DE CORTE- YouTube', 'url': 'https://www.youtube.com/embed/U7yEF9N2BYU?si=UitzQOujzXYWNvXV'},
    {'titulo': 'CURSO GRATIS DE CARPINTERIA - CLASE 3 - UNION Y ENSAMBLE- YouTube', 'url': 'https://www.youtube.com/embed/WSUQ_TxoVrY?si=xPMCwzFfVA-TifP9'},
    {'titulo': 'CURSO GRATIS DE CARPINTERIA - CLASE 5 - ARMAR MUEBLE- YouTube', 'url': 'https://www.youtube.com/embed/c8w1TTHr_co?si=lkaXa-Xf-6HCZyfm'},
    {'titulo': 'CURSO GRATIS DE CARPINTERIA - CLASE 6 - COMO LIJAR- YouTube', 'url': 'https://www.youtube.com/embed/EfJxsfSBT2c?si=Fgq4JNniXiQ-_YyI'},
    {'titulo': 'CURSO GRATIS DE CARPINTERIA - CLASE 7 - ARMAR CAJONES- YouTube', 'url': 'https://www.youtube.com/embed/AmEXL1jYp24?si=kFvxlLSQcHhN5yk_'},
    
           ],
'preguntas': [
{'p': '¿Qué material se utiliza?', 'a': 'Madera', 'b': 'Tela', 'c': 'Vidrio', 'ok': 'a'},
{'p': '¿Qué es medir?', 'a': 'Calcular tamaño', 'b': 'Pintar', 'c': 'Cortar', 'ok': 'a'},
{'p': '¿Qué es ensamblar?', 'a': 'Unir piezas', 'b': 'Cortar', 'c': 'Medir', 'ok': 'a'},
{'p': '¿Qué herramienta es común?', 'a': 'Serrucho', 'b': 'Pluma', 'c': 'Regla', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Precisión', 'b': 'Color', 'c': 'Sonido', 'ok': 'a'},
{'p': '¿Qué es acabado?', 'a': 'Detalle final', 'b': 'Corte', 'c': 'Medida', 'ok': 'a'},
{'p': '¿Qué se crea?', 'a': 'Muebles', 'b': 'Ropa', 'c': 'Papel', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Habilidad manual', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué requiere?', 'a': 'Precisión', 'b': 'Velocidad', 'c': 'Color', 'ok': 'a'},
{'p': '¿Qué se usa para cortar?', 'a': 'Sierra', 'b': 'Aguja', 'c': 'Hilo', 'ok': 'a'}
]
},

# Curso de Cocina: preparación de alimentos segura y organizada
'Cocina': {
'info': 'Bienvenido(a) a este curso de cocina.\nAprenderás a preparar alimentos de manera segura y organizada.\nDesarrollarás creatividad, higiene y técnicas culinarias.\n\nLa cocina es el arte de preparar y combinar alimentos.\n\nSe trabaja con:\nIngredientes,Técnicas,Higiene,Temperatura ySabor',
'videos': [
    {'titulo': 'écnicas básicas de cocina clase 1 Escuela de Gastronomía- YouTube', 'url': 'https://www.youtube.com/embed/j_8AvR3Hi0o?si=6xqFkZha9BRd_RMJ'},
    {'titulo': 'Técnicas Básicas de Cocina clase 2 Escuela de Gastronomía 1- YouTube', 'url': 'https://www.youtube.com/embed/JdOYnWT0z0c?si=nc712iuXbt7mlXza'},
    {'titulo': 'Técnicas Básicas de Cocina clase 7 Escuela de Gastronomía- YouTube', 'url': 'https://www.youtube.com/embed/mbOQ2fov0Z8?si=JVKHqcKzBG7D1mTM'},
    {'titulo': '25 Trucos De Cocina Que Aprendí En Restaurantes- YouTube', 'url': 'https://www.youtube.com/embed/7uHT11gxdik?si=dKe30PYl89zy2lBN'},
    
           ],
'preguntas': [
{'p': '¿Qué es cocinar?', 'a': 'Preparar alimentos', 'b': 'Cortar madera', 'c': 'Escribir', 'ok': 'a'},
{'p': '¿Qué es importante?', 'a': 'Higiene', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué son ingredientes?', 'a': 'Elementos para cocinar', 'b': 'Herramientas', 'c': 'Máquinas', 'ok': 'a'},
{'p': '¿Qué es técnica?', 'a': 'Forma de hacer', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se controla?', 'a': 'Temperatura', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Buen sabor', 'b': 'Ruido', 'c': 'Color', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Recetas', 'b': 'Códigos', 'c': 'Planos', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Organización', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Utensilios', 'b': 'Tela', 'c': 'Madera', 'ok': 'a'},
{'p': '¿Qué evita?', 'a': 'Contaminación', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'}
]
},

# Curso de Música: ritmo, melodía y armonía
'Música': {
'info': 'Bienvenido(a) a este curso de música.\nAprenderás los fundamentos del sonido, ritmo y melodía.\nDesarrollarás habilidades auditivas y creatividad.\n\nLa música es el arte de organizar sonidos en el tiempo.\n\nSe trabaja con:\nRitmo,Melodía,Armonía,Compás ySonido',
'videos': [
    {'titulo': 'Que es la musica?- YouTube', 'url': 'https://www.youtube.com/embed/ygrbitQHLm0?si=fZMGnW2RrMJ2kz3S'},
    {'titulo': 'Historia de la musica- YouTube', 'url': 'https://www.youtube.com/embed/If_T1Q9u6FM?si=A_hWnMcjpx2GjP5I'},
    {'titulo': 'Como influye la musica en nuestro cerebro- YouTube', 'url': 'https://www.youtube.com/embed/ED_Mok754DQ?si=QfldJi7M1DHvIso1'},
    
],
'preguntas': [
{'p': '¿Qué es música?', 'a': 'Organización de sonidos', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué es ritmo?', 'a': 'Patrón de tiempo', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es melodía?', 'a': 'Secuencia de notas', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué es armonía?', 'a': 'Combinación de sonidos', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué es compás?', 'a': 'Medida musical', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se desarrolla?', 'a': 'Oído', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Instrumentos', 'b': 'Martillo', 'c': 'Sierra', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Coordinación', 'b': 'Peso', 'c': 'Color', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Notas', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'},
{'p': '¿Qué expresa?', 'a': 'Emociones', 'b': 'Datos', 'c': 'Códigos', 'ok': 'a'}
]
},

# Curso de Diseño Web: construcción de sitios con HTML, CSS y diseño responsive
'Diseño web': {
'info': 'Bienvenido(a) a este curso de diseño web.\nAprenderás a crear páginas web funcionales y visualmente atractivas.\nDesarrollarás habilidades digitales y creativas.\n\nEl diseño web consiste en construir sitios para internet.\n\nSe trabaja con:\nHTML,CSS,Estructura,Diseño yResponsive',
'videos': [
    {'titulo': 'Como crear una paguina web?? YouTube', 'url': 'https://www.youtube.com/embed/STNnG5K3jdM?si=M9cVsSK7p1EsvclJ'},
    {'titulo': 'Todo sobre diseño de paguinas web- YouTube', 'url': 'https://www.youtube.com/embed/ELSm-G201Ls?si=frg1EWcQgO3qCfNe'},
    {'titulo': 'Errores comones en css- YouTube', 'url': 'https://www.youtube.com/embed/a6td69aNF6c?si=xaxrK-OUYfKenzX3'},
           ],
'preguntas': [
{'p': '¿Qué es HTML?', 'a': 'Estructura web', 'b': 'Color', 'c': 'Imagen', 'ok': 'a'},
{'p': '¿Qué hace CSS?', 'a': 'Diseño visual', 'b': 'Texto', 'c': 'Sonido', 'ok': 'a'},
{'p': '¿Qué es web?', 'a': 'Internet', 'b': 'Archivo', 'c': 'Carpeta', 'ok': 'a'},
{'p': '¿Qué es responsive?', 'a': 'Adaptable', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se crea?', 'a': 'Sitios', 'b': 'Ropa', 'c': 'Muebles', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Código', 'b': 'Martillo', 'c': 'Sierra', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Diseño', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué es estructura?', 'a': 'Organización', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Crear páginas', 'b': 'Cortar', 'c': 'Pintar', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Funcionalidad', 'b': 'Ruido', 'c': 'Peso', 'ok': 'a'}
]
},

# Curso de Redes Sociales: uso estratégico de plataformas digitales
'Redes sociales': {
'info': 'Bienvenido(a) a este curso de redes sociales.\nAprenderás a utilizar plataformas digitales de forma estratégica.\nDesarrollarás comunicación y manejo de contenido.\n\nLas redes sociales permiten interactuar y compartir información.\n\nSe trabaja con:\nContenido,Interacción,Estrategia,Seguridad yComunicación',
'videos': [
    {'titulo': '- YouTube', 'url': 'https://www.youtube.com/embed/rctz_w5SB3A?si=87rcqp08kbbMMX80"'},
    {'titulo': '- YouTube', 'url': 'https://www.youtube.com/embed/zpuDDcrZOS8?si=ktqIk4aeW2Vtdngo'},
    {'titulo': '- YouTube', 'url': 'https://www.youtube.com/embed/gzES0MuWqHE?si=QutDiedcKX0GI-SN'},
           ],
'preguntas': [
{'p': '¿Qué son redes sociales?', 'a': 'Plataformas digitales', 'b': 'Programas', 'c': 'Archivos', 'ok': 'a'},
{'p': '¿Qué se comparte?', 'a': 'Contenido', 'b': 'Cable', 'c': 'Pantalla', 'ok': 'a'},
{'p': '¿Qué es interacción?', 'a': 'Comunicación', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se desarrolla?', 'a': 'Comunicación', 'b': 'Peso', 'c': 'Altura', 'ok': 'a'},
{'p': '¿Qué es estrategia?', 'a': 'Plan', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se busca?', 'a': 'Alcance', 'b': 'Peso', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué se mejora?', 'a': 'Contenido', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué es seguridad?', 'a': 'Protección', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Publicar', 'b': 'Cortar', 'c': 'Pintar', 'ok': 'a'},
{'p': '¿Qué se mide?', 'a': 'Interacción', 'b': 'Color', 'c': 'Peso', 'ok': 'a'}
]
},

# Curso de Excel Pro: manejo de datos, fórmulas y análisis avanzado
'Excel Pro': {
'info': 'Bienvenido(a) a este curso de Excel Pro.\nAprenderás a manejar datos, fórmulas avanzadas y análisis.\nDesarrollarás habilidades para el trabajo y la organización.\n\nExcel es una herramienta para gestionar información.\n\nSe trabaja con:\nCeldas,Fórmulas,Funciones,Gráficas yDatos',
'videos': [
    {'titulo': 'Excel basico- YouTube', 'url': 'https://www.youtube.com/embed/jmAUii6Htog?si=dGrka5lyz2N4S5q3'},
    {'titulo': 'Todo sobre Excel- YouTube', 'url': 'https://www.youtube.com/embed/I3yV7E42vFI?si=El1TDnUuTE_W8bUe'},
    {'titulo': 'Curso completo de excel- YouTube', 'url': 'https://www.youtube.com/embed/jqyGUK4VvjQ?si=r19eOi3uF25cbDn6'},
           ],
'preguntas': [
{'p': '¿Qué es Excel?', 'a': 'Programa de datos', 'b': 'Juego', 'c': 'Editor de imágenes', 'ok': 'a'},
{'p': '¿Qué es una celda?', 'a': 'Espacio de datos', 'b': 'Archivo', 'c': 'Pantalla', 'ok': 'a'},
{'p': '¿Qué es fórmula?', 'a': 'Cálculo', 'b': 'Color', 'c': 'Objeto', 'ok': 'a'},
{'p': '¿Qué es función?', 'a': 'Operación', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
{'p': '¿Qué se organiza?', 'a': 'Datos', 'b': 'Colores', 'c': 'Formas', 'ok': 'a'},
{'p': '¿Qué se crea?', 'a': 'Gráficas', 'b': 'Ropa', 'c': 'Muebles', 'ok': 'a'},
{'p': '¿Qué se analiza?', 'a': 'Información', 'b': 'Color', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué mejora?', 'a': 'Organización', 'b': 'Altura', 'c': 'Peso', 'ok': 'a'},
{'p': '¿Qué se usa?', 'a': 'Datos', 'b': 'Tela', 'c': 'Madera', 'ok': 'a'},
{'p': '¿Qué se aprende?', 'a': 'Fórmulas avanzadas', 'b': 'Pintar', 'c': 'Cortar', 'ok': 'a'}
]
}
}

# Ruta principal: si ya hay sesión iniciada, manda al panel; si no, muestra el home
@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))  # Usuario ya logueado -> dashboard
    return render_template('home.html')  # Usuario nuevo -> página de bienvenida/login/registro

# Ruta para crear una cuenta nueva
@app.route('/registro', methods=['POST'])
def registro():
    db = get_db(); cur = db.cursor()  # Abrimos conexión y cursor a la base de datos
    pw = generate_password_hash(request.form['password'])  # Encriptamos la contraseña recibida
    try:
        # Insertamos el nuevo usuario con sus datos básicos
        cur.execute("INSERT INTO usuarios (nombre, edad, correo, password) VALUES (%s,%s,%s,%s)",
                    (request.form['nombre'], request.form['edad'], request.form['correo'], pw))
        db.commit()  # Guardamos los cambios en la base de datos
        flash("¡Bienvenido! Has dado el paso más importante.", "success")  # Mensaje de éxito
    except: flash("El correo ya está en uso.", "danger")  # El correo es UNIQUE, si falla es porque ya existe
    return redirect(url_for('home'))  # Regresamos al inicio para iniciar sesión

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    db = get_db(); cur = db.cursor(dictionary=True)  # Cursor que regresa filas como diccionarios
    cur.execute("SELECT * FROM usuarios WHERE correo = %s", (request.form['correo'],))  # Buscamos al usuario por correo
    user = cur.fetchone()  # Obtenemos el primer (y único) resultado
    if user and check_password_hash(user['password'], request.form['password']):  # Verificamos la contraseña
        session['user_id'] = user['id']  # Guardamos el id del usuario en la sesión
        session['nombre'] = user['nombre']  # Guardamos el nombre para mostrarlo después
        return redirect(url_for('dashboard'))  # Login correcto -> panel de cursos
    flash("Datos incorrectos.", "danger")  # Correo o contraseña incorrectos
    return redirect(url_for('home'))

# Panel principal con las categorías de cursos
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('home'))  # Si no hay sesión, regresamos al inicio
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT curso_nombre FROM boletas WHERE user_id = %s", (session['user_id'],))  # Cursos ya aprobados
    completados = [r['curso_nombre'] for r in cur.fetchall()]
    cur.execute("SELECT curso_nombre FROM favoritos WHERE user_id = %s", (session['user_id'],))  # Cursos marcados como favoritos
    favoritos = [r['curso_nombre'] for r in cur.fetchall()]
    return render_template('dashboard.html', completados=completados, favoritos=favoritos)

# Ruta para actualizar los datos del perfil del usuario
@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if 'user_id' not in session: return redirect(url_for('home'))  # Protegemos la ruta: requiere sesión
    db = get_db(); cur = db.cursor()
    nombre = request.form['nombre']  # Nuevo nombre escrito en el formulario
    edad = request.form['edad'] # Ahora sí lo tomamos del formulario
    correo = request.form['correo']  # Nuevo correo escrito en el formulario
    password = request.form['password']  # Nueva contraseña (puede venir vacía)

    if password:
        # Si el usuario escribió una nueva contraseña, la encriptamos y actualizamos junto con el resto
        pw_hash = generate_password_hash(password)
        cur.execute("UPDATE usuarios SET nombre=%s, edad=%s, correo=%s, password=%s WHERE id=%s",
                    (nombre, edad, correo, pw_hash, session['user_id']))
    else:
        # Si no escribió contraseña nueva, dejamos la actual sin cambios
        cur.execute("UPDATE usuarios SET nombre=%s, edad=%s, correo=%s WHERE id=%s",
                    (nombre, edad, correo, session['user_id']))

    db.commit()  # Guardamos los cambios
    session['nombre'] = nombre  # Actualizamos el nombre mostrado en la sesión actual
    flash("Información actualizada correctamente.", "success")
    return redirect(url_for('perfil'))


# Muestra los cursos que pertenecen a una categoría (arte, oficios, cultura, informatica)
@app.route('/categoria/<tipo>')
def categoria(tipo):
    if 'user_id' not in session: return redirect(url_for('home'))  # Protegemos la ruta: requiere sesión
    cursos = CATEGORIAS.get(tipo, [])  # Lista de nombres de curso para esta categoría (vacía si no existe)
    # Armamos una lista de tuplas (nombre_curso, icono, color1, color2) para que la
    # plantilla pueda dibujar tarjetas creativas con icono y degradado por curso
    cursos_info = [(c,) + ICONOS_CURSOS.get(c, ('bi-mortarboard-fill', '#2D6A4F', '#52b788')) for c in cursos]
    return render_template('categoria.html', tipo=tipo, cursos=cursos_info)

# --- RUTA CURSO CON NOTAS ---
# Muestra el contenido teórico, videos, notas y examen de un curso específico
@app.route('/curso/<nombre>')
def ver_curso(nombre):
    if 'user_id' not in session: return redirect(url_for('home'))  # Protegemos la ruta: requiere sesión
    datos = CURSOS_DATA.get(nombre)  # Información completa del curso (info, videos, preguntas)

    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT contenido FROM notas WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))  # Nota guardada por el usuario para este curso
    nota = cur.fetchone()

    cur.execute("SELECT * FROM favoritos WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))  # Verificamos si el curso está en favoritos
    es_favorito = cur.fetchone()

    return render_template('curso.html', nombre=nombre, datos=datos, user_id=session['user_id'], nota=nota, es_favorito=es_favorito)

# --- SISTEMA DE FAVORITOS ---
# Agrega o quita un curso de la lista de favoritos del usuario
@app.route('/toggle_favorito/<nombre>')
def toggle_favorito(nombre):
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT * FROM favoritos WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))  # ¿Ya es favorito?
    if cur.fetchone():
        cur.execute("DELETE FROM favoritos WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))  # Si ya estaba, lo quitamos
    else:
        cur.execute("INSERT INTO favoritos (user_id, curso_nombre) VALUES (%s,%s)", (session['user_id'], nombre))  # Si no estaba, lo agregamos
    db.commit()
    return redirect(request.referrer)  # Regresamos a la página desde donde se hizo clic

# Permite al usuario consultar su correo si recuerda nombre, edad y contraseña
@app.route('/recuperar_correo', methods=['POST'])
def recuperar_correo():
    nombre = request.form['nombre']
    edad = request.form['edad']
    password_ingresada = request.form['password']

    db = get_db()
    cur = db.cursor(dictionary=True)
    # Buscamos por nombre y edad
    cur.execute("SELECT correo, password FROM usuarios WHERE nombre=%s AND edad=%s", (nombre, edad))
    user = cur.fetchone()

    if user and check_password_hash(user['password'], password_ingresada):
        # Si la contraseña coincide, le avisamos cuál es su correo
        flash(f"Tu correo registrado es: {user['correo']}", "info")
    else:
        flash("Los datos no coinciden. No podemos mostrar el correo.", "danger")

    return redirect(url_for('home'))


# Permite iniciar el proceso de cambio de contraseña validando nombre, edad y correo
@app.route('/recuperar_password', methods=['POST'])
def recuperar_password():
    nombre = request.form['nombre']
    edad = request.form['edad']
    correo = request.form['correo']

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, correo FROM usuarios WHERE nombre=%s AND edad=%s AND correo=%s", (nombre, edad, correo))  # Validamos los 3 datos
    user = cur.fetchone()

    if user:
        session['recovery_id'] = user['id']  # Guardamos temporalmente el id para autorizar el cambio de password
        return render_template('restablecer.html', correo=user['correo'])

    flash("Información incorrecta. Validación fallida.", "danger")
    return redirect(url_for('home'))

# Guarda la nueva contraseña una vez que el usuario fue validado en /recuperar_password
@app.route('/cambiar_password_recuperacion', methods=['POST'])
def cambiar_password_recuperacion():
    nueva_password = request.form['password']
    usuario_id = session.get('recovery_id')  # Solo existe si pasó la validación previa

    if usuario_id:
        # Encriptamos la contraseña antes de guardarla
        password_encriptada = generate_password_hash(nueva_password)

        db = get_db()
        cur = db.cursor()
        # Guardamos el hash, no el texto plano
        cur.execute("UPDATE usuarios SET password=%s WHERE id=%s", (password_encriptada, usuario_id))
        db.commit()

        session.pop('recovery_id', None)  # Limpiamos el permiso temporal de recuperación
        flash("Contraseña actualizada con éxito.", "success")
        return redirect(url_for('home'))

    flash("Error en la sesión de recuperación.", "danger")
    return redirect(url_for('home'))


# --- SISTEMA DE NOTAS ---
# Guarda (o reemplaza) la nota personal del usuario para un curso
@app.route('/guardar_nota', methods=['POST'])
def guardar_nota():
    db = get_db(); cur = db.cursor()
    curso = request.form['curso_nombre']
    texto = request.form['contenido']
    cur.execute("DELETE FROM notas WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], curso))  # Borramos la nota anterior (si existía)
    cur.execute("INSERT INTO notas (user_id, curso_nombre, contenido) VALUES (%s,%s,%s)", (session['user_id'], curso, texto))  # Insertamos la nota nueva
    db.commit()
    flash("Nota guardada.", "success")
    return redirect(url_for('ver_curso', nombre=curso))

# Genera y descarga el diploma en PDF de una boleta (curso aprobado) específica
@app.route('/descargar_diploma/<int:boleta_id>')
def descargar_diploma(boleta_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM boletas WHERE id = %s AND user_id = %s", (boleta_id, session['user_id']))  # Verificamos que la boleta sea del usuario logueado
    b = cur.fetchone()
    if not b: return "Error: No encontrado", 404  # Si no existe o no es del usuario, error 404

    # Configuración de página Horizontal (Landscape)
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # --- DISEÑO DE FONDO Y BORDES PROFESIONALES ---
    # Rectángulo Verde Exterior (Marco Principal)
    pdf.set_draw_color(27, 67, 50) # Verde Oscuro
    pdf.set_line_width(3)
    pdf.rect(5, 5, 287, 200) 

    # Rectángulo Dorado Interior (Línea de Elegancia)
    pdf.set_draw_color(184, 134, 11) # Dorado (Gold)
    pdf.set_line_width(1)
    pdf.rect(8, 8, 281, 194)

    # --- ENCABEZADO ---
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 15, "CERTIFICADO DE EXCELENCIA", 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, "SEMANAS DE PAZ", 0, 1, 'C')
    
    pdf.set_draw_color(184, 134, 11)
    pdf.line(100, 55, 197, 55) # Línea decorativa bajo el título

    # --- CUERPO DEL DIPLOMA ---
    pdf.ln(15)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Este documento certifica oficialmente que:", 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(184, 134, 11)
    # Limpieza de caracteres especiales para evitar PDF en blanco
    nombre_user = session['nombre'].encode('latin-1', 'ignore').decode('latin-1')
    pdf.cell(0, 25, nombre_user.upper(), 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Ha concluido exitosamente el programa de capacitacion en:", 0, 1, 'C')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 26)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 15, b['curso_nombre'].upper(), 0, 1, 'C')
    
    # --- PIE DE PÁGINA (Calificación y Sello) ---
    pdf.ln(20)
    # Dibujamos un pequeño cuadro para la calificación (Parece un sello)
    pdf.set_fill_color(27, 67, 50)
    pdf.rect(120, 160, 57, 25, 'F')
    
    pdf.set_xy(120, 165)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(57, 8, "CALIFICACION", 0, 1, 'C')
    pdf.set_x(120)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(57, 10, f"{int(b['puntuacion'])} / 10", 0, 1, 'C')

    # Texto de validez
    pdf.set_xy(10, 190)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Este certificado es personal e intransferible. Documento generado digitalmente por el Sistema de Gestion de Semanas de Paz.", 0, 0, 'C')

    # --- SALIDA DEL ARCHIVO (IMPORTANTE PARA QUE NO SALGA EN BLANCO) ---
    # Generamos los bytes del PDF
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Certificado_{b["curso_nombre"]}.pdf'
    return response


# Procesa las respuestas del examen final y genera la boleta de resultado
@app.route('/evaluar', methods=['POST'])
def evaluar():
    if 'user_id' not in session: return redirect(url_for('home'))  # Protegemos la ruta: requiere sesión
    curso_nombre = request.form['curso_nombre']  # Nombre del curso evaluado
    datos = CURSOS_DATA.get(curso_nombre)  # Obtenemos las preguntas correctas de ese curso
    score = 0  # Contador de respuestas correctas
    if datos:
        for i, preg in enumerate(datos['preguntas'], 1):  # Recorremos cada pregunta (1, 2, 3...)
            if request.form.get(f'q{i}') == preg['ok']: score += 1  # Sumamos 1 punto si la respuesta coincide

    if score >= 6:  # Si aprobó (6 o más de 10), guardamos la boleta/certificado
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO boletas (user_id, curso_nombre, puntuacion) VALUES (%s,%s,%s)",
                    (session['user_id'], curso_nombre, score))
        db.commit()
    return render_template('boleta.html', score=score, curso=curso_nombre)  # Mostramos el resultado al usuario

# Página de perfil: datos del usuario, certificaciones, favoritos y logros
@app.route('/perfil')
def perfil():
    if 'user_id' not in session: return redirect(url_for('home'))  # Protegemos la ruta: requiere sesión
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (session['user_id'],))  # Datos del usuario
    user = cur.fetchone()
    cur.execute("SELECT * FROM boletas WHERE user_id = %s ORDER BY fecha DESC", (session['user_id'],))  # Cursos aprobados, del más reciente al más antiguo
    boletas = cur.fetchall()
    # Obtenemos favoritos para el perfil
    cur.execute("SELECT curso_nombre FROM favoritos WHERE user_id = %s", (session['user_id'],))
    favoritos = cur.fetchall()

    # --- CÁLCULO DE LOGROS DESBLOQUEADOS ---
    # Usamos un set para contar cursos distintos (si repite un curso no debe contar doble)
    cursos_completados = {b['curso_nombre'] for b in boletas}
    num_completados = len(cursos_completados)

    # Construimos la lista de logros indicando si cada uno está desbloqueado o no
    logros = []
    for logro in LOGROS:
        item = dict(logro)  # Copiamos el diccionario para no modificar la lista original LOGROS
        item['desbloqueado'] = num_completados >= logro['umbral']  # True si ya alcanzó el umbral requerido
        logros.append(item)

    # El certificado final solo aparece cuando se completaron TODOS los cursos disponibles
    certificado_final = num_completados >= TOTAL_CURSOS

    return render_template('perfil.html', user=user, boletas=boletas, favoritos=favoritos,
                            logros=logros, num_completados=num_completados,
                            total_cursos=TOTAL_CURSOS, certificado_final=certificado_final)

# Genera el certificado especial "Leyenda de Semanas de Paz" cuando se completan todos los cursos
@app.route('/descargar_certificado_maestro')
def descargar_certificado_maestro():
    if 'user_id' not in session: return redirect(url_for('home'))  # Protegemos la ruta: requiere sesión

    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT curso_nombre FROM boletas WHERE user_id = %s", (session['user_id'],))  # Cursos distintos completados
    completados = cur.fetchall()

    # Si todavía no completa todos los cursos, no se le permite descargar el certificado final
    if len(completados) < TOTAL_CURSOS:
        flash("Aún no has completado todos los cursos para obtener este certificado.", "danger")
        return redirect(url_for('perfil'))

    # Configuración de página Horizontal (Landscape), igual que el diploma individual
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # Marco exterior dorado para diferenciarlo del diploma normal (verde)
    pdf.set_draw_color(184, 134, 11)  # Dorado
    pdf.set_line_width(3)
    pdf.rect(5, 5, 287, 200)

    # Marco interior verde
    pdf.set_draw_color(27, 67, 50)
    pdf.set_line_width(1)
    pdf.rect(8, 8, 281, 194)

    # Encabezado
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 15, "CERTIFICADO DE HONOR", 0, 1, 'C')

    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 10, "LEYENDA DE SEMANAS DE PAZ", 0, 1, 'C')

    pdf.set_draw_color(184, 134, 11)
    pdf.line(80, 55, 217, 55)  # Línea decorativa bajo el título

    # Cuerpo del certificado
    pdf.ln(15)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Este documento certifica oficialmente que:", 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(184, 134, 11)
    nombre_user = session['nombre'].encode('latin-1', 'ignore').decode('latin-1')  # Limpieza de caracteres especiales
    pdf.cell(0, 25, nombre_user.upper(), 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Ha completado los {TOTAL_CURSOS} cursos del programa y desbloqueado", 0, 1, 'C')
    pdf.cell(0, 10, "los 20 logros del Sistema de Gestion de Semanas de Paz.", 0, 1, 'C')

    # Sello inferior
    pdf.ln(15)
    pdf.set_fill_color(184, 134, 11)
    pdf.rect(108, 165, 80, 25, 'F')

    pdf.set_xy(108, 170)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, "PROGRAMA COMPLETO", 0, 1, 'C')
    pdf.set_x(108)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(80, 10, f"{TOTAL_CURSOS}/{TOTAL_CURSOS} CURSOS - 20/20 LOGROS", 0, 1, 'C')

    # Texto de validez
    pdf.set_xy(10, 180)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Este certificado es personal e intransferible. Documento generado digitalmente por el Sistema de Gestion de Semanas de Paz.", 0, 0, 'C')

    # Generamos los bytes del PDF y los enviamos como descarga
    pdf_output = pdf.output(dest='S').encode('latin-1')

    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=Certificado_Leyenda_SemanasDePaz.pdf'
    return response

# Cierra la sesión del usuario y regresa al inicio
@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('home'))

# Punto de entrada: ejecuta el servidor de desarrollo de Flask
if __name__ == '__main__': app.run(debug=True)
