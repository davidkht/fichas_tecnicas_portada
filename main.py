import os
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from fpdf import FPDF
from io import BytesIO

# Función para crear la portada con FPDF
def crear_portada(nombre_equipo, marca_agua_path):
    # Crear un objeto FPDF para generar el PDF de la portada
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Obtener las dimensiones de la página A4
    page_width = 210  # mm
    page_height = 297  # mm

    # Colocar la marca de agua
    if marca_agua_path:
        pdf = agregar_marca_agua(pdf, marca_agua_path, page_width, page_height)

    # Definir el título centrado
    pdf.set_font("helvetica", style='B',size=18)
    # Cambiar el color del texto a azul (#002060)
    pdf.set_text_color(0, 32, 96)  # RGB values for #002060

    # Dividir el texto si es demasiado largo
    max_width = page_width - 20  # Considerar márgenes de 10mm a cada lado
    lines = []
    current_line = ""

    for word in nombre_equipo.split():
        if pdf.get_string_width(current_line + " " + word) <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line.strip())
            current_line = word

    lines.append(current_line.strip())

    # Ajustar la posición del texto para centrado en la mitad de la página
    y_position = (page_height / 2) - (len(lines) * 5)  # Ajustar la posición vertical basada en el número de líneas

    # Escribir cada línea centrada
    for line in lines:
        pdf.set_xy(0, y_position)
        pdf.cell(page_width, 10, text=line, align='C')
        y_position += 10  # Mover hacia abajo para la siguiente línea



    # Guardar el PDF de la portada en un objeto BytesIO para usarlo más tarde
    portada_buffer = BytesIO()
    pdf.output(portada_buffer)
    portada_buffer.seek(0)

    # Cargar el PDF de la portada en PyPDF2
    portada_pdf = PdfReader(portada_buffer)

    return portada_pdf

# Función para agregar la marca de agua a un PDF
def agregar_marca_agua(pdf, marca_agua_path, page_width, page_height):
    marca_agua = Image.open(marca_agua_path)
    # Redimensionar la imagen de la marca de agua al tamaño de la página A4
    marca_agua = marca_agua.resize((int(page_width * 4), int(page_height * 4)), Image.LANCZOS)  # Convertir mm a píxeles (1 mm ≈ 3.78 píxeles)


    # Guardar la imagen como un objeto BytesIO
    marca_buffer = BytesIO()
    marca_agua.save(marca_buffer, format="PNG")
    marca_buffer.seek(0)

    # Agregar la imagen de la marca de agua al PDF
    pdf.image(marca_buffer, x=0, y=0, w=page_width+10, h=page_height+10)

    return pdf

# Función para unir la portada y la ficha técnica en un solo archivo
def unir_pdf(portada_pdf, ficha_tecnica_pdf, output_path):
    # Crear un escritor de PDF
    pdf_writer = PdfWriter()

    # Añadir la portada
    pdf_writer.add_page(portada_pdf.pages[0])

    # Añadir el resto de páginas del PDF original (ficha técnica)
    for page_num in range(len(ficha_tecnica_pdf.pages)):
        page = ficha_tecnica_pdf.pages[page_num]
        pdf_writer.add_page(page)

    # Guardar el archivo final sin sobrescribir los originales
    with open(output_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

def procesar_fichas(marca_agua_path, carpeta_entrada, carpeta_salida):
    # Obtener la lista de archivos PDF en la carpeta de entrada
    for archivo in os.listdir(carpeta_entrada):
        if archivo.endswith(".pdf"):  # Procesar solo archivos PDF
            pdf_path = os.path.join(carpeta_entrada, archivo)
            nombre_equipo = os.path.splitext(os.path.basename(pdf_path))[0]

            # Leer el archivo PDF original (ficha técnica) en memoria
            ficha_tecnica_pdf = PdfReader(pdf_path)

            # Crear la portada con el nombre del equipo y la marca de agua
            portada_pdf = crear_portada(nombre_equipo, marca_agua_path)

            # Definir el nombre del archivo de salida en la carpeta de resultados
            output_path = os.path.join(carpeta_salida, f"{nombre_equipo}.pdf")

            # Unir la portada con la ficha técnica
            unir_pdf(portada_pdf, ficha_tecnica_pdf, output_path)

            print(f"El archivo {output_path} ha sido generado exitosamente.")

if __name__ == "__main__":
    # Rutas de carpetas y archivos
    carpeta_entrada = "fichas_originales"
    carpeta_salida = "resultados"
    marca_agua_path = "marca.png"
    
    # Asegurarse de que la carpeta de salida exista
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Procesar todas las fichas técnicas en la carpeta de entrada
    procesar_fichas(marca_agua_path, carpeta_entrada, carpeta_salida)