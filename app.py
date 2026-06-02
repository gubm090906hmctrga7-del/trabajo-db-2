from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash
from database import init_db, get_db
from fpdf import FPDF
import io

app = Flask(__name__)
app.secret_key = 'clave_maestria_v6'
init_db()

# --- DATOS DE LOS CURSOS ---
CURSOS_DATA = {
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

    'Escultura': {
        'info': 'La escultura es el arte de crear formas tridimensionales en materiales como piedra, madera, metal, barro o yeso. Incluye técnicas como modelado (añadir material), talla (quitar material), ensamblaje y vaciado. Se estudian conceptos como volumen, espacio, proporción, equilibrio y textura. También se utilizan herramientas como cinceles, martillos, espátulas y moldes. Existen esculturas clásicas, modernas, abstractas y cinéticas.',
        'preguntas': [
            {'p': '¿Qué es modelado?', 'a': 'Añadir material', 'b': 'Quitar', 'c': 'Pintar', 'ok': 'a'},
            {'p': '¿Qué es talla?', 'a': 'Quitar material', 'b': 'Añadir', 'c': 'Pintar', 'ok': 'a'},
            {'p': '¿Qué es volumen?', 'a': 'Forma 3D', 'b': 'Color', 'c': 'Luz', 'ok': 'a'},
            {'p': '¿Qué material se usa?', 'a': 'Arcilla', 'b': 'Agua', 'c': 'Tela', 'ok': 'a'},
            {'p': '¿Qué es relieve?', 'a': 'Fondo', 'b': 'Libre', 'c': 'Plano', 'ok': 'a'},
            {'p': '¿Qué es molde?', 'a': 'Forma', 'b': 'Color', 'c': 'Herramienta', 'ok': 'a'},
            {'p': '¿Qué es proporción?', 'a': 'Tamaño', 'b': 'Color', 'c': 'Luz', 'ok': 'a'},
            {'p': '¿Qué es textura?', 'a': 'Superficie', 'b': 'Forma', 'c': 'Color', 'ok': 'a'},
            {'p': '¿Qué es escultura cinética?', 'a': 'Movimiento', 'b': 'Fija', 'c': 'Plano', 'ok': 'a'},
            {'p': '¿Qué es equilibrio?', 'a': 'Estabilidad', 'b': 'Color', 'c': 'Movimiento', 'ok': 'a'}
        ]
    },

    'Teatro': {
        'info': 'El teatro es el arte de representar historias mediante actuación en un escenario. Incluye expresión corporal, voz, dicción, improvisación, creación de personajes, guion, escenografía, iluminación y dirección. Se desarrollan habilidades de comunicación, confianza y creatividad.',
        'preguntas': [
            {'p': '¿Qué es actuación?', 'a': 'Interpretar', 'b': 'Leer', 'c': 'Cantar', 'ok': 'a'},
            {'p': 'Improvisación:', 'a': 'Sin guion', 'b': 'Leer', 'c': 'Copiar', 'ok': 'a'},
            {'p': 'Guion:', 'a': 'Texto', 'b': 'Escena', 'c': 'Vestuario', 'ok': 'a'},
            {'p': 'Escenografía:', 'a': 'Decorado', 'b': 'Texto', 'c': 'Voz', 'ok': 'a'},
            {'p': 'Personaje:', 'a': 'Rol', 'b': 'Actor', 'c': 'Director', 'ok': 'a'},
            {'p': 'Diálogo:', 'a': 'Conversación', 'b': 'Silencio', 'c': 'Acción', 'ok': 'a'},
            {'p': 'Monólogo:', 'a': 'Uno', 'b': 'Grupo', 'c': 'Narrador', 'ok': 'a'},
            {'p': 'Ensayo:', 'a': 'Práctica', 'b': 'Final', 'c': 'Inicio', 'ok': 'a'},
            {'p': 'Escena:', 'a': 'Parte', 'b': 'Todo', 'c': 'Final', 'ok': 'a'},
            {'p': 'Voz escénica:', 'a': 'Proyección', 'b': 'Silencio', 'c': 'Ruido', 'ok': 'a'}
        ]
    },

    'Danza': {
        'info': 'La danza es una forma de expresión artística mediante el movimiento del cuerpo. Incluye coordinación, ritmo, flexibilidad, equilibrio y expresión emocional. Existen diferentes estilos como ballet, danza contemporánea, folclórica y urbana.',
        'preguntas': [
            {'p': 'Danza clásica:', 'a': 'Ballet', 'b': 'Hip hop', 'c': 'Salsa', 'ok': 'a'},
            {'p': 'Ritmo:', 'a': 'Tiempo', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
            {'p': 'Coreografía:', 'a': 'Secuencia', 'b': 'Vestuario', 'c': 'Música', 'ok': 'a'},
            {'p': 'Flexibilidad:', 'a': 'Movilidad', 'b': 'Fuerza', 'c': 'Salto', 'ok': 'a'},
            {'p': 'Folclor:', 'a': 'Tradicional', 'b': 'Moderno', 'c': 'Urbano', 'ok': 'a'},
            {'p': 'Expresión:', 'a': 'Emoción', 'b': 'Color', 'c': 'Técnica', 'ok': 'a'},
            {'p': 'Movimiento:', 'a': 'Base', 'b': 'Color', 'c': 'Texto', 'ok': 'a'},
            {'p': 'Ensayo:', 'a': 'Práctica', 'b': 'Final', 'c': 'Inicio', 'ok': 'a'},
            {'p': 'Vestuario:', 'a': 'Ropa', 'b': 'Música', 'c': 'Escena', 'ok': 'a'},
            {'p': 'Improvisar:', 'a': 'Crear', 'b': 'Copiar', 'c': 'Leer', 'ok': 'a'}
        ]
    },

    'Música': {
        'info': 'La música es el arte de organizar sonidos en el tiempo. Incluye ritmo, melodía, armonía, lectura de partituras, uso de instrumentos y teoría musical. Se estudian escalas, acordes, tempo, dinámica y estilos musicales.',
        'preguntas': [
            {'p': 'Notas escala:', 'a': '7', 'b': '5', 'c': '12', 'ok': 'a'},
            {'p': 'Tempo:', 'a': 'Velocidad', 'b': 'Volumen', 'c': 'Autor', 'ok': 'a'},
            {'p': 'Acorde:', 'a': 'Varias notas', 'b': 'Una', 'c': 'Silencio', 'ok': 'a'},
            {'p': 'Melodía:', 'a': 'Notas', 'b': 'Ruido', 'c': 'Silencio', 'ok': 'a'},
            {'p': 'Ritmo:', 'a': 'Tiempo', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
            {'p': 'Clave de sol:', 'a': 'Agudos', 'b': 'Graves', 'c': 'Medios', 'ok': 'a'},
            {'p': 'Instrumento cuerda:', 'a': 'Violín', 'b': 'Flauta', 'c': 'Tambor', 'ok': 'a'},
            {'p': 'Crescendo:', 'a': 'Sube volumen', 'b': 'Baja', 'c': 'Para', 'ok': 'a'},
            {'p': 'Silencio:', 'a': 'Pausa', 'b': 'Nota', 'c': 'Clave', 'ok': 'a'},
            {'p': 'Partitura:', 'a': 'Lectura musical', 'b': 'Instrumento', 'c': 'Sonido', 'ok': 'a'}
        ]
    },
    'Carpintería': {
        'info': 'La carpintería es el oficio dedicado al trabajo con madera para crear muebles, estructuras y objetos decorativos. Incluye selección de maderas (blandas y duras), lectura de planos, medición precisa, corte, ensamblaje (espiga, cola de milano), lijado, barnizado y acabados. Se utilizan herramientas manuales y eléctricas como sierras, taladros y cepillos. También se estudian normas de seguridad y mantenimiento de herramientas.',
        'preguntas': [
            {'p': '¿Qué es lijado?', 'a': 'Suavizar', 'b': 'Cortar', 'c': 'Pintar', 'ok': 'a'},
            {'p': 'Madera blanda:', 'a': 'Pino', 'b': 'Encino', 'c': 'Caoba', 'ok': 'a'},
            {'p': 'Herramienta corte:', 'a': 'Sierra', 'b': 'Martillo', 'c': 'Regla', 'ok': 'a'},
            {'p': 'Ensamble:', 'a': 'Unión', 'b': 'Corte', 'c': 'Color', 'ok': 'a'},
            {'p': 'Barniz:', 'a': 'Protege', 'b': 'Corta', 'c': 'Une', 'ok': 'a'},
            {'p': 'Medir:', 'a': 'Flexómetro', 'b': 'Martillo', 'c': 'Pincel', 'ok': 'a'},
            {'p': 'Cepillado:', 'a': 'Nivelar', 'b': 'Cortar', 'c': 'Pegar', 'ok': 'a'},
            {'p': 'Formón:', 'a': 'Huecos', 'b': 'Medir', 'c': 'Pintar', 'ok': 'a'},
            {'p': 'Veta:', 'a': 'Fibras', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
            {'p': 'Seguridad:', 'a': 'Protección', 'b': 'Velocidad', 'c': 'Color', 'ok': 'a'}
        ]
    },

    'Cocina': {
        'info': 'La cocina es el arte de preparar alimentos mediante técnicas culinarias. Incluye cortes (juliana, brunoise), métodos de cocción (hervir, freír, hornear), higiene y seguridad alimentaria, manejo de ingredientes, balance nutricional y presentación de platillos. También se estudian recetas, sazón, tiempos de cocción y uso correcto de utensilios.',
        'preguntas': [
            {'p': 'Brunoise:', 'a': 'Cubos pequeños', 'b': 'Tiras', 'c': 'Rodajas', 'ok': 'a'},
            {'p': 'Hervir:', 'a': 'Agua caliente', 'b': 'Frío', 'c': 'Seco', 'ok': 'a'},
            {'p': 'Freír:', 'a': 'Aceite', 'b': 'Agua', 'c': 'Aire', 'ok': 'a'},
            {'p': 'Higiene:', 'a': 'Limpieza', 'b': 'Corte', 'c': 'Fuego', 'ok': 'a'},
            {'p': 'Cuchillo chef:', 'a': 'Principal', 'b': 'Pequeño', 'c': 'Decorativo', 'ok': 'a'},
            {'p': 'Hornear:', 'a': 'Calor seco', 'b': 'Agua', 'c': 'Aceite', 'ok': 'a'},
            {'p': 'Sazonar:', 'a': 'Dar sabor', 'b': 'Cortar', 'c': 'Hervir', 'ok': 'a'},
            {'p': 'Receta:', 'a': 'Instrucciones', 'b': 'Herramienta', 'c': 'Ingrediente', 'ok': 'a'},
            {'p': 'Utensilios:', 'a': 'Herramientas', 'b': 'Comida', 'c': 'Fuego', 'ok': 'a'},
            {'p': 'Temperatura:', 'a': 'Cocción', 'b': 'Color', 'c': 'Forma', 'ok': 'a'}
        ]
    },

    'Costura': {
        'info': 'La costura es el oficio de unir telas mediante hilo y aguja o máquina. Incluye tipos de puntadas, uso de patrones, corte de tela, medición, confección de prendas, reparación de ropa y diseño básico. También se estudian tipos de telas, herramientas y acabados.',
        'preguntas': [
            {'p': 'Herramienta básica:', 'a': 'Aguja', 'b': 'Martillo', 'c': 'Sierra', 'ok': 'a'},
            {'p': 'Puntada:', 'a': 'Recta', 'b': 'Curva', 'c': 'Circular', 'ok': 'a'},
            {'p': 'Tela común:', 'a': 'Algodón', 'b': 'Metal', 'c': 'Vidrio', 'ok': 'a'},
            {'p': 'Patrón:', 'a': 'Molde', 'b': 'Corte', 'c': 'Hilo', 'ok': 'a'},
            {'p': 'Máquina:', 'a': 'Coser', 'b': 'Cortar', 'c': 'Pintar', 'ok': 'a'},
            {'p': 'Hilo:', 'a': 'Unir', 'b': 'Cortar', 'c': 'Medir', 'ok': 'a'},
            {'p': 'Tijeras:', 'a': 'Cortar', 'b': 'Unir', 'c': 'Medir', 'ok': 'a'},
            {'p': 'Medir:', 'a': 'Cinta', 'b': 'Regla', 'c': 'Lápiz', 'ok': 'a'},
            {'p': 'Dobladillo:', 'a': 'Borde', 'b': 'Centro', 'c': 'Inicio', 'ok': 'a'},
            {'p': 'Plancha:', 'a': 'Alisar', 'b': 'Coser', 'c': 'Cortar', 'ok': 'a'}
        ]
    },

    'Mecánica': {
        'info': 'La mecánica automotriz estudia el funcionamiento y reparación de vehículos. Incluye motores, sistemas de transmisión, frenos, suspensión, lubricación, diagnóstico de fallas y mantenimiento preventivo.',
        'preguntas': [
            {'p': 'Motor:', 'a': 'Genera energía', 'b': 'Frena', 'c': 'Dirige', 'ok': 'a'},
            {'p': 'Aceite:', 'a': 'Lubrica', 'b': 'Quema', 'c': 'Enfría', 'ok': 'a'},
            {'p': 'Frenos:', 'a': 'Detener', 'b': 'Acelerar', 'c': 'Girar', 'ok': 'a'},
            {'p': 'Batería:', 'a': 'Energía', 'b': 'Combustible', 'c': 'Agua', 'ok': 'a'},
            {'p': 'Llanta:', 'a': 'Movimiento', 'b': 'Motor', 'c': 'Freno', 'ok': 'a'},
            {'p': 'Suspensión:', 'a': 'Estabilidad', 'b': 'Velocidad', 'c': 'Color', 'ok': 'a'},
            {'p': 'Radiador:', 'a': 'Enfriar', 'b': 'Calentar', 'c': 'Mover', 'ok': 'a'},
            {'p': 'Transmisión:', 'a': 'Velocidad', 'b': 'Color', 'c': 'Luz', 'ok': 'a'},
            {'p': 'Herramienta:', 'a': 'Llave', 'b': 'Pincel', 'c': 'Regla', 'ok': 'a'},
            {'p': 'Diagnóstico:', 'a': 'Detectar fallas', 'b': 'Pintar', 'c': 'Cortar', 'ok': 'a'}
        ]
    },

    'Electricidad': {
        'info': 'La electricidad estudia el flujo de corriente eléctrica y su aplicación. Incluye circuitos, voltaje, resistencia, uso de herramientas, instalación eléctrica, seguridad y mantenimiento.',
        'preguntas': [
            {'p': 'Corriente:', 'a': 'Flujo eléctrico', 'b': 'Agua', 'c': 'Aire', 'ok': 'a'},
            {'p': 'Voltaje:', 'a': 'Potencial', 'b': 'Peso', 'c': 'Color', 'ok': 'a'},
            {'p': 'Resistencia:', 'a': 'Oposición', 'b': 'Flujo', 'c': 'Energía', 'ok': 'a'},
            {'p': 'Cable:', 'a': 'Conduce', 'b': 'Corta', 'c': 'Pinta', 'ok': 'a'},
            {'p': 'Interruptor:', 'a': 'Controla', 'b': 'Genera', 'c': 'Corta', 'ok': 'a'},
            {'p': 'Multímetro:', 'a': 'Medir', 'b': 'Cortar', 'c': 'Unir', 'ok': 'a'},
            {'p': 'Circuito:', 'a': 'Conexión', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
            {'p': 'Seguridad:', 'a': 'Protección', 'b': 'Velocidad', 'c': 'Color', 'ok': 'a'},
            {'p': 'Fusible:', 'a': 'Protege', 'b': 'Corta', 'c': 'Une', 'ok': 'a'},
            {'p': 'Energía:', 'a': 'Electricidad', 'b': 'Agua', 'c': 'Fuego', 'ok': 'a'}
        ]
    },
    'Historia de México': {
        'info': 'La Historia de México estudia los procesos sociales, políticos y culturales desde las civilizaciones prehispánicas hasta la actualidad. Incluye culturas como olmecas, mayas y mexicas; la conquista española; el virreinato; la independencia en 1810; la reforma liberal; la revolución mexicana en 1910; y el México contemporáneo. Se analizan personajes clave, movimientos sociales, cambios económicos y construcción de la identidad nacional.',
        'preguntas': [
            {'p': 'Inicio de Independencia:', 'a': '1810', 'b': '1910', 'c': '1821', 'ok': 'a'},
            {'p': 'Padre de la patria:', 'a': 'Hidalgo', 'b': 'Juárez', 'c': 'Díaz', 'ok': 'a'},
            {'p': 'Revolución mexicana:', 'a': '1910', 'b': '1810', 'c': '2000', 'ok': 'a'},
            {'p': 'Capital mexica:', 'a': 'Tenochtitlán', 'b': 'Roma', 'c': 'Madrid', 'ok': 'a'},
            {'p': 'Conquista por:', 'a': 'España', 'b': 'Francia', 'c': 'Italia', 'ok': 'a'},
            {'p': 'Benito Juárez fue:', 'a': 'Presidente', 'b': 'Rey', 'c': 'General', 'ok': 'a'},
            {'p': 'Porfiriato:', 'a': 'Díaz', 'b': 'Madero', 'c': 'Villa', 'ok': 'a'},
            {'p': 'Virreinato:', 'a': 'Colonia', 'b': 'Actualidad', 'c': 'Futuro', 'ok': 'a'},
            {'p': 'Madero inició:', 'a': 'Revolución', 'b': 'Independencia', 'c': 'Colonia', 'ok': 'a'},
            {'p': 'México actual:', 'a': 'Contemporáneo', 'b': 'Antiguo', 'c': 'Colonial', 'ok': 'a'}
        ]
    },

    'Literatura': {
        'info': 'La literatura es el arte de la expresión escrita y oral. Abarca géneros como narrativa (cuento, novela), lírica (poesía) y dramática (teatro). Se estudian figuras literarias (metáfora, símil), análisis de textos, comprensión lectora, redacción y estilos literarios. También se exploran autores importantes, corrientes literarias y el impacto cultural de la escritura.',
        'preguntas': [
            {'p': 'Narrativa:', 'a': 'Historia', 'b': 'Número', 'c': 'Color', 'ok': 'a'},
            {'p': 'Poesía:', 'a': 'Verso', 'b': 'Prosa', 'c': 'Plano', 'ok': 'a'},
            {'p': 'Autor:', 'a': 'Escritor', 'b': 'Lector', 'c': 'Editor', 'ok': 'a'},
            {'p': 'Metáfora:', 'a': 'Comparación', 'b': 'Número', 'c': 'Dato', 'ok': 'a'},
            {'p': 'Novela:', 'a': 'Larga', 'b': 'Corta', 'c': 'Simple', 'ok': 'a'},
            {'p': 'Cuento:', 'a': 'Breve', 'b': 'Largo', 'c': 'Técnico', 'ok': 'a'},
            {'p': 'Drama:', 'a': 'Teatro', 'b': 'Música', 'c': 'Danza', 'ok': 'a'},
            {'p': 'Texto:', 'a': 'Escrito', 'b': 'Sonido', 'c': 'Imagen', 'ok': 'a'},
            {'p': 'Lectura crítica:', 'a': 'Analizar', 'b': 'Copiar', 'c': 'Memorizar', 'ok': 'a'},
            {'p': 'Prosa:', 'a': 'Texto continuo', 'b': 'Verso', 'c': 'Rima', 'ok': 'a'}
        ]
    },

    'Cine': {
        'info': 'El cine es el arte de contar historias mediante imágenes en movimiento. Incluye guion, dirección, actuación, fotografía, edición, sonido y producción. Se estudian géneros (drama, comedia, acción), lenguaje cinematográfico (planos, ángulos), narrativa visual y análisis de películas.',
        'preguntas': [
            {'p': 'Guion:', 'a': 'Historia escrita', 'b': 'Cámara', 'c': 'Actor', 'ok': 'a'},
            {'p': 'Director:', 'a': 'Coordina', 'b': 'Actúa', 'c': 'Escribe', 'ok': 'a'},
            {'p': 'Plano:', 'a': 'Toma', 'b': 'Audio', 'c': 'Guion', 'ok': 'a'},
            {'p': 'Edición:', 'a': 'Cortar escenas', 'b': 'Grabar', 'c': 'Actuar', 'ok': 'a'},
            {'p': 'Género:', 'a': 'Tipo', 'b': 'Actor', 'c': 'Cámara', 'ok': 'a'},
            {'p': 'Fotografía:', 'a': 'Imagen', 'b': 'Audio', 'c': 'Texto', 'ok': 'a'},
            {'p': 'Escena:', 'a': 'Parte', 'b': 'Final', 'c': 'Inicio', 'ok': 'a'},
            {'p': 'Actor:', 'a': 'Interpreta', 'b': 'Dirige', 'c': 'Escribe', 'ok': 'a'},
            {'p': 'Sonido:', 'a': 'Audio', 'b': 'Imagen', 'c': 'Color', 'ok': 'a'},
            {'p': 'Película:', 'a': 'Obra audiovisual', 'b': 'Libro', 'c': 'Música', 'ok': 'a'}
        ]
    },

    'Paz y Sociedad': {
        'info': 'Este curso estudia la convivencia social, resolución de conflictos, valores como respeto, tolerancia y justicia. Incluye derechos humanos, cultura de paz, inclusión social, participación ciudadana y desarrollo comunitario.',
        'preguntas': [
            {'p': 'Paz:', 'a': 'Armonía', 'b': 'Conflicto', 'c': 'Violencia', 'ok': 'a'},
            {'p': 'Respeto:', 'a': 'Valorar', 'b': 'Ignorar', 'c': 'Rechazar', 'ok': 'a'},
            {'p': 'Conflicto:', 'a': 'Problema', 'b': 'Solución', 'c': 'Valor', 'ok': 'a'},
            {'p': 'Diálogo:', 'a': 'Hablar', 'b': 'Pelear', 'c': 'Callar', 'ok': 'a'},
            {'p': 'Tolerancia:', 'a': 'Aceptar', 'b': 'Rechazar', 'c': 'Ignorar', 'ok': 'a'},
            {'p': 'Justicia:', 'a': 'Equidad', 'b': 'Desigualdad', 'c': 'Violencia', 'ok': 'a'},
            {'p': 'Derechos humanos:', 'a': 'Libertad', 'b': 'Control', 'c': 'Castigo', 'ok': 'a'},
            {'p': 'Sociedad:', 'a': 'Grupo', 'b': 'Individuo', 'c': 'Objeto', 'ok': 'a'},
            {'p': 'Participación:', 'a': 'Involucrarse', 'b': 'Ignorar', 'c': 'Salir', 'ok': 'a'},
            {'p': 'Valores:', 'a': 'Principios', 'b': 'Objetos', 'c': 'Números', 'ok': 'a'}
        ]
    },

    'Gastronomía Regional': {
        'info': 'La gastronomía regional estudia los platillos tradicionales de diferentes regiones, sus ingredientes, técnicas y cultura culinaria. Incluye historia de la comida, uso de productos locales, recetas típicas y diversidad gastronómica.',
        'preguntas': [
            {'p': 'Gastronomía:', 'a': 'Arte culinario', 'b': 'Música', 'c': 'Arte visual', 'ok': 'a'},
            {'p': 'Ingrediente:', 'a': 'Elemento', 'b': 'Receta', 'c': 'Utensilio', 'ok': 'a'},
            {'p': 'Platillo típico:', 'a': 'Tradicional', 'b': 'Moderno', 'c': 'Extranjero', 'ok': 'a'},
            {'p': 'Receta:', 'a': 'Instrucciones', 'b': 'Herramienta', 'c': 'Ingrediente', 'ok': 'a'},
            {'p': 'Cocción:', 'a': 'Preparar', 'b': 'Servir', 'c': 'Comprar', 'ok': 'a'},
            {'p': 'Cultura:', 'a': 'Costumbres', 'b': 'Objetos', 'c': 'Números', 'ok': 'a'},
            {'p': 'Sazón:', 'a': 'Sabor', 'b': 'Color', 'c': 'Forma', 'ok': 'a'},
            {'p': 'Utensilio:', 'a': 'Herramienta', 'b': 'Ingrediente', 'c': 'Receta', 'ok': 'a'},
            {'p': 'Región:', 'a': 'Zona', 'b': 'Persona', 'c': 'Objeto', 'ok': 'a'},
            {'p': 'Diversidad:', 'a': 'Variedad', 'b': 'Igual', 'c': 'Único', 'ok': 'a'}
        ]
    },
    'Computación Básica': {
        'info': 'La computación básica enseña el uso fundamental de una computadora. Incluye شناخت de hardware (CPU, monitor, teclado, mouse), software (sistema operativo como Windows o Linux), manejo de archivos y carpetas, uso de programas básicos (Word, navegador), internet, correo electrónico y buenas prácticas de seguridad. También abarca encendido/apagado correcto, almacenamiento en USB, y conceptos básicos de redes.',
        'preguntas': [
            {'p': '¿Qué es CPU?', 'a': 'Procesador', 'b': 'Pantalla', 'c': 'Mouse', 'ok': 'a'},
            {'p': 'Mouse sirve para:', 'a': 'Mover cursor', 'b': 'Escribir', 'c': 'Escuchar', 'ok': 'a'},
            {'p': 'Teclado:', 'a': 'Escribir', 'b': 'Mover', 'c': 'Ver', 'ok': 'a'},
            {'p': 'Archivo:', 'a': 'Documento', 'b': 'Pantalla', 'c': 'Programa', 'ok': 'a'},
            {'p': 'Carpeta:', 'a': 'Organizar', 'b': 'Borrar', 'c': 'Abrir', 'ok': 'a'},
            {'p': 'Internet:', 'a': 'Red global', 'b': 'PC', 'c': 'Cable', 'ok': 'a'},
            {'p': 'Navegador:', 'a': 'Chrome', 'b': 'Word', 'c': 'Excel', 'ok': 'a'},
            {'p': 'Guardar:', 'a': 'Almacenar', 'b': 'Eliminar', 'c': 'Cerrar', 'ok': 'a'},
            {'p': 'USB:', 'a': 'Almacenamiento', 'b': 'Pantalla', 'c': 'Audio', 'ok': 'a'},
            {'p': 'Correo electrónico:', 'a': 'Enviar mensajes', 'b': 'Editar fotos', 'c': 'Jugar', 'ok': 'a'}
        ]
    },

    'Excel Pro': {
        'info': 'Excel Pro se enfoca en el manejo avanzado de hojas de cálculo. Incluye fórmulas (SUMA, SI, BUSCARV/XLOOKUP), tablas dinámicas, gráficos, análisis de datos, filtros, macros, validación de datos y automatización. Se utiliza para finanzas, reportes, estadísticas y gestión empresarial.',
        'preguntas': [
            {'p': 'Fórmula inicia con:', 'a': '=', 'b': '+', 'c': '#', 'ok': 'a'},
            {'p': 'SUMA:', 'a': 'Agregar', 'b': 'Restar', 'c': 'Multiplicar', 'ok': 'a'},
            {'p': 'Celda:', 'a': 'Fila/columna', 'b': 'Hoja', 'c': 'Archivo', 'ok': 'a'},
            {'p': 'Ctrl+C:', 'a': 'Copiar', 'b': 'Pegar', 'c': 'Cerrar', 'ok': 'a'},
            {'p': 'BuscarV:', 'a': 'Buscar datos', 'b': 'Borrar', 'c': 'Sumar', 'ok': 'a'},
            {'p': 'Extensión:', 'a': '.xlsx', 'b': '.docx', 'c': '.pptx', 'ok': 'a'},
            {'p': 'Macro:', 'a': 'Automatizar', 'b': 'Imagen', 'c': 'Texto', 'ok': 'a'},
            {'p': '$:', 'a': 'Fijar celda', 'b': 'Sumar', 'c': 'Borrar', 'ok': 'a'},
            {'p': 'Tabla dinámica:', 'a': 'Resumen', 'b': 'Texto', 'c': 'Imagen', 'ok': 'a'},
            {'p': 'Función SI:', 'a': 'Condición', 'b': 'Suma', 'c': 'Texto', 'ok': 'a'}
        ]
    },

    'Diseño Web': {
        'info': 'El diseño web consiste en crear sitios web visuales y funcionales. Incluye HTML (estructura), CSS (estilos), JavaScript (interactividad), diseño responsivo, experiencia de usuario (UX), interfaces (UI), uso de editores de código y publicación en internet.',
        'preguntas': [
            {'p': 'HTML:', 'a': 'Estructura', 'b': 'Diseño', 'c': 'Base de datos', 'ok': 'a'},
            {'p': 'CSS:', 'a': 'Estilo', 'b': 'Código', 'c': 'Servidor', 'ok': 'a'},
            {'p': 'JavaScript:', 'a': 'Interacción', 'b': 'Color', 'c': 'Texto', 'ok': 'a'},
            {'p': 'Página web:', 'a': 'Sitio', 'b': 'Archivo', 'c': 'Programa', 'ok': 'a'},
            {'p': 'Responsive:', 'a': 'Adaptable', 'b': 'Rápido', 'c': 'Grande', 'ok': 'a'},
            {'p': 'UX:', 'a': 'Experiencia usuario', 'b': 'Código', 'c': 'Servidor', 'ok': 'a'},
            {'p': 'UI:', 'a': 'Interfaz', 'b': 'Base datos', 'c': 'Archivo', 'ok': 'a'},
            {'p': 'Dominio:', 'a': 'Nombre web', 'b': 'Código', 'c': 'Imagen', 'ok': 'a'},
            {'p': 'Hosting:', 'a': 'Servidor', 'b': 'Diseño', 'c': 'Texto', 'ok': 'a'},
            {'p': 'Editor código:', 'a': 'Programar', 'b': 'Diseñar', 'c': 'Jugar', 'ok': 'a'}
        ]
    },

    'Redes Sociales': {
        'info': 'Las redes sociales son plataformas digitales para comunicación y contenido. Incluye creación de contenido, marketing digital, algoritmos, engagement, branding personal, métricas (alcance, interacción), publicidad y gestión de comunidades.',
        'preguntas': [
            {'p': 'Red social:', 'a': 'Plataforma', 'b': 'Programa', 'c': 'Archivo', 'ok': 'a'},
            {'p': 'Contenido:', 'a': 'Publicación', 'b': 'Código', 'c': 'Archivo', 'ok': 'a'},
            {'p': 'Engagement:', 'a': 'Interacción', 'b': 'Compra', 'c': 'Venta', 'ok': 'a'},
            {'p': 'Algoritmo:', 'a': 'Ordena contenido', 'b': 'Crea imágenes', 'c': 'Edita videos', 'ok': 'a'},
            {'p': 'Seguidores:', 'a': 'Usuarios', 'b': 'Bots', 'c': 'Datos', 'ok': 'a'},
            {'p': 'Like:', 'a': 'Me gusta', 'b': 'Compartir', 'c': 'Guardar', 'ok': 'a'},
            {'p': 'Comentario:', 'a': 'Opinar', 'b': 'Guardar', 'c': 'Borrar', 'ok': 'a'},
            {'p': 'Hashtag:', 'a': 'Etiqueta', 'b': 'Foto', 'c': 'Video', 'ok': 'a'},
            {'p': 'Publicidad:', 'a': 'Promoción', 'b': 'Mensaje', 'c': 'Texto', 'ok': 'a'},
            {'p': 'Alcance:', 'a': 'Personas vistas', 'b': 'Ventas', 'c': 'Clicks', 'ok': 'a'}
        ]
    },

    'Seguridad Digital': {
        'info': 'La seguridad digital se enfoca en proteger la información y privacidad en internet. Incluye contraseñas seguras, antivirus, phishing, protección de datos, navegación segura, redes WiFi seguras, autenticación de dos factores y prevención de fraudes.',
        'preguntas': [
            {'p': 'Contraseña segura:', 'a': 'Compleja', 'b': '1234', 'c': 'abcd', 'ok': 'a'},
            {'p': 'Virus:', 'a': 'Malware', 'b': 'Archivo', 'c': 'Foto', 'ok': 'a'},
            {'p': 'Phishing:', 'a': 'Engaño', 'b': 'Juego', 'c': 'Programa', 'ok': 'a'},
            {'p': 'Antivirus:', 'a': 'Protección', 'b': 'Juego', 'c': 'Texto', 'ok': 'a'},
            {'p': 'WiFi segura:', 'a': 'Contraseña', 'b': 'Abierta', 'c': 'Gratis', 'ok': 'a'},
            {'p': 'Datos personales:', 'a': 'Privados', 'b': 'Públicos', 'c': 'Abiertos', 'ok': 'a'},
            {'p': '2FA:', 'a': 'Doble verificación', 'b': 'Contraseña', 'c': 'Correo', 'ok': 'a'},
            {'p': 'Spam:', 'a': 'Correo basura', 'b': 'Mensaje', 'c': 'Archivo', 'ok': 'a'},
            {'p': 'Firewall:', 'a': 'Protege red', 'b': 'Corta luz', 'c': 'Guarda datos', 'ok': 'a'},
            {'p': 'Privacidad:', 'a': 'Protección datos', 'b': 'Compartir', 'c': 'Eliminar', 'ok': 'a'}
        ]
    }
}

@app.route('/')
def home():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/registro', methods=['POST'])
def registro():
    db = get_db(); cur = db.cursor()
    pw = generate_password_hash(request.form['password'])
    try:
        cur.execute("INSERT INTO usuarios (nombre, edad, correo, password) VALUES (%s,%s,%s,%s)",
                    (request.form['nombre'], request.form['edad'], request.form['correo'], pw))
        db.commit()
        flash("¡Bienvenido! Has dado el paso más importante.", "success")
    except: flash("El correo ya está en uso.", "danger")
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE correo = %s", (request.form['correo'],))
    user = cur.fetchone()
    if user and check_password_hash(user['password'], request.form['password']):
        session['user_id'] = user['id']
        session['nombre'] = user['nombre']
        return redirect(url_for('dashboard'))
    flash("Datos incorrectos.", "danger")
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('home'))
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT curso_nombre FROM boletas WHERE user_id = %s", (session['user_id'],))
    completados = [r['curso_nombre'] for r in cur.fetchall()]
    cur.execute("SELECT curso_nombre FROM favoritos WHERE user_id = %s", (session['user_id'],))
    favoritos = [r['curso_nombre'] for r in cur.fetchall()]
    return render_template('dashboard.html', completados=completados, favoritos=favoritos)

@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if 'user_id' not in session: return redirect(url_for('home'))
    db = get_db(); cur = db.cursor()
    nombre = request.form['nombre']
    edad = request.form['edad'] # Ahora sí lo tomamos del formulario
    correo = request.form['correo']
    password = request.form['password']
    
    if password:
        pw_hash = generate_password_hash(password)
        cur.execute("UPDATE usuarios SET nombre=%s, edad=%s, correo=%s, password=%s WHERE id=%s",
                    (nombre, edad, correo, pw_hash, session['user_id']))
    else:
        cur.execute("UPDATE usuarios SET nombre=%s, edad=%s, correo=%s WHERE id=%s",
                    (nombre, edad, correo, session['user_id']))
    
    db.commit()
    session['nombre'] = nombre
    flash("Información actualizada correctamente.", "success")
    return redirect(url_for('perfil'))


@app.route('/categoria/<tipo>')
def categoria(tipo):
    data = {
        'arte': ['Pintura', 'Escultura', 'Teatro', 'Danza', 'Música'],
        'oficios': ['Carpintería', 'Cocina', 'Costura', 'Mecánica', 'Electricidad'],
        'cultura': ['Historia de México', 'Literatura', 'Cine', 'Paz y Sociedad'],
        'informatica': ['Computación Básica', 'Excel Pro', 'Diseño Web', 'Seguridad Digital']
    }
    return render_template('categoria.html', tipo=tipo, cursos=data.get(tipo, []))

# --- RUTA CURSO CON NOTAS ---
@app.route('/curso/<nombre>')
def ver_curso(nombre):
    if 'user_id' not in session: return redirect(url_for('home'))
    datos = CURSOS_DATA.get(nombre)
    
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT contenido FROM notas WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))
    nota = cur.fetchone()
    
    cur.execute("SELECT * FROM favoritos WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))
    es_favorito = cur.fetchone()
    
    return render_template('curso.html', nombre=nombre, datos=datos, user_id=session['user_id'], nota=nota, es_favorito=es_favorito)

# --- SISTEMA DE FAVORITOS ---
@app.route('/toggle_favorito/<nombre>')
def toggle_favorito(nombre):
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT * FROM favoritos WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))
    if cur.fetchone():
        cur.execute("DELETE FROM favoritos WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], nombre))
    else:
        cur.execute("INSERT INTO favoritos (user_id, curso_nombre) VALUES (%s,%s)", (session['user_id'], nombre))
    db.commit()
    return redirect(request.referrer)

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


@app.route('/recuperar_password', methods=['POST'])
def recuperar_password():
    nombre = request.form['nombre']
    edad = request.form['edad']
    correo = request.form['correo']
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, correo FROM usuarios WHERE nombre=%s AND edad=%s AND correo=%s", (nombre, edad, correo))
    user = cur.fetchone()
    
    if user:
        session['recovery_id'] = user['id']
        return render_template('restablecer.html', correo=user['correo'])
    
    flash("Información incorrecta. Validación fallida.", "danger")
    return redirect(url_for('home'))

@app.route('/cambiar_password_recuperacion', methods=['POST'])
def cambiar_password_recuperacion():
    nueva_password = request.form['password']
    usuario_id = session.get('recovery_id')

    if usuario_id:
        # Encriptamos la contraseña antes de guardarla
        password_encriptada = generate_password_hash(nueva_password)
        
        db = get_db()
        cur = db.cursor()
        # Guardamos el hash, no el texto plano
        cur.execute("UPDATE usuarios SET password=%s WHERE id=%s", (password_encriptada, usuario_id))
        db.commit()
        
        session.pop('recovery_id', None)
        flash("Contraseña actualizada con éxito.", "success")
        return redirect(url_for('home'))
    
    flash("Error en la sesión de recuperación.", "danger")
    return redirect(url_for('home'))


# --- SISTEMA DE NOTAS ---
@app.route('/guardar_nota', methods=['POST'])
def guardar_nota():
    db = get_db(); cur = db.cursor()
    curso = request.form['curso_nombre']
    texto = request.form['contenido']
    cur.execute("DELETE FROM notas WHERE user_id=%s AND curso_nombre=%s", (session['user_id'], curso))
    cur.execute("INSERT INTO notas (user_id, curso_nombre, contenido) VALUES (%s,%s,%s)", (session['user_id'], curso, texto))
    db.commit()
    flash("Nota guardada.", "success")
    return redirect(url_for('ver_curso', nombre=curso))

@app.route('/descargar_diploma/<int:boleta_id>')
def descargar_diploma(boleta_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM boletas WHERE id = %s AND user_id = %s", (boleta_id, session['user_id']))
    b = cur.fetchone()
    if not b: return "Error: No encontrado", 404

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


@app.route('/evaluar', methods=['POST'])
def evaluar():
    if 'user_id' not in session: return redirect(url_for('home'))
    curso_nombre = request.form['curso_nombre']
    datos = CURSOS_DATA.get(curso_nombre)
    score = 0
    if datos:
        for i, preg in enumerate(datos['preguntas'], 1):
            if request.form.get(f'q{i}') == preg['ok']: score += 1
    
    if score >= 6:
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO boletas (user_id, curso_nombre, puntuacion) VALUES (%s,%s,%s)",
                    (session['user_id'], curso_nombre, score))
        db.commit()
    return render_template('boleta.html', score=score, curso=curso_nombre)

@app.route('/perfil')
def perfil():
    if 'user_id' not in session: return redirect(url_for('home'))
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.execute("SELECT * FROM boletas WHERE user_id = %s ORDER BY fecha DESC", (session['user_id'],))
    boletas = cur.fetchall()
    # Obtenemos favoritos para el perfil
    cur.execute("SELECT curso_nombre FROM favoritos WHERE user_id = %s", (session['user_id'],))
    favoritos = cur.fetchall()
    return render_template('perfil.html', user=user, boletas=boletas, favoritos=favoritos)
@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('home'))

if __name__ == '__main__': app.run(debug=True)
