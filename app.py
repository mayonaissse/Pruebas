import streamlit as st
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import io
import tempfile

# ---------------------------------------------------------
# PALETA DE COLORES DMC
# ---------------------------------------------------------
COLORES_DMC = {
    "310":   {"nombre": "Negro", "rgb": (0, 0, 0)},
    "B5200": {"nombre": "Blanco Nieve", "rgb": (255, 255, 255)},
    "415":   {"nombre": "Gris Perla", "rgb": (211, 214, 218)},
    "317":   {"nombre": "Gris Acero", "rgb": (98, 102, 104)},
    "321":   {"nombre": "Rojo", "rgb": (199, 43, 56)},
    "3801":  {"nombre": "Rojo Melón", "rgb": (224, 66, 75)},
    "602":   {"nombre": "Rosa", "rgb": (226, 73, 137)},
    "740":   {"nombre": "Naranja", "rgb": (245, 126, 31)},
    "307":   {"nombre": "Amarillo Limón", "rgb": (254, 222, 73)},
    "444":   {"nombre": "Amarillo Oscuro", "rgb": (255, 204, 0)},
    "700":   {"nombre": "Verde Brillante", "rgb": (15, 117, 63)},
    "905":   {"nombre": "Verde Loro", "rgb": (68, 129, 65)},
    "3850":  {"nombre": "Verde Esmeralda", "rgb": (38, 137, 110)},
    "311":   {"nombre": "Azul Marino", "rgb": (28, 77, 109)},
    "820":   {"nombre": "Azul Real Oscuro", "rgb": (24, 46, 103)},
    "995":   {"nombre": "Azul Eléctrico", "rgb": (0, 137, 182)},
    "208":   {"nombre": "Lavanda", "rgb": (132, 89, 164)},
    "333":   {"nombre": "Morado Oscuro", "rgb": (90, 48, 128)},
    "433":   {"nombre": "Marrón Medio", "rgb": (118, 68, 38)},
    "898":   {"nombre": "Café Oscuro", "rgb": (73, 42, 19)}
}

# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------
def distancia_color_ponderada(c1, c2):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return (2 * (r1 - r2)**2 + 4 * (g1 - g2)**2 + 3 * (b1 - b2)**2) ** 0.5

def color_contraste(color_fondo, umbral=40):
    brillo = (color_fondo[0] * 299 + color_fondo[1] * 587 + color_fondo[2] * 114) / 1000
    porcentaje_gris = 100 - ((brillo / 255) * 100)
    return (255, 255, 255) if porcentaje_gris > umbral else (0, 0, 0)

def obtener_fuentes(tamano_bloque):
    tamano_fuente = int(tamano_bloque * 0.85)
    try:
        # Try common font paths for Linux/Termux/Streamlit Cloud
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "DejaVuSans.ttf",
        ]
        font_path = None
        for fp in font_paths:
            if os.path.exists(fp):
                font_path = fp
                break
        
        if font_path:
            f_simbolos = ImageFont.truetype(font_path, tamano_fuente)
            f_texto = ImageFont.truetype(font_path, 16)
            f_titulo = ImageFont.truetype(font_path, 32)
        else:
            raise IOError("No font found")
        return f_simbolos, f_texto, f_titulo
    except IOError:
        f_defecto = ImageFont.load_default()
        return f_defecto, f_defecto, f_defecto

def dibujar_guias_cuadrante(draw, start_x, end_x, start_y, end_y, ancho_total, alto_total, tamano_bloque, margen, fuente):
    color_linea = (100, 100, 100)
    q_ancho = end_x - start_x
    q_alto = end_y - start_y
    
    for y_line in range(q_alto + 1):
        abs_y = start_y + y_line
        grosor = 3 if abs_y % 10 == 0 else 1
        y_pos = margen + y_line * tamano_bloque
        draw.line([(margen, y_pos), (margen + q_ancho * tamano_bloque, y_pos)], fill=color_linea, width=grosor)
        if abs_y % 10 == 0 and abs_y > 0 and abs_y < alto_total:
            draw.text((margen - 30, y_pos - 8), str(abs_y), fill=(0,0,0), font=fuente)

    for x_line in range(q_ancho + 1):
        abs_x = start_x + x_line
        grosor = 3 if abs_x % 10 == 0 else 1
        x_pos = margen + x_line * tamano_bloque
        draw.line([(x_pos, margen), (x_pos, margen + q_alto * tamano_bloque)], fill=color_linea, width=grosor)
        if abs_x % 10 == 0 and abs_x > 0 and abs_x < ancho_total:
            draw.text((x_pos - 8, margen - 25), str(abs_x), fill=(0,0,0), font=fuente)

    centro_x_abs = ancho_total // 2
    centro_y_abs = alto_total // 2
    
    if start_x <= centro_x_abs <= end_x and start_y == 0:
        cx = margen + (centro_x_abs - start_x) * tamano_bloque
        draw.polygon([(cx, margen - 15), (cx - 6, margen - 5), (cx + 6, margen - 5)], fill="red")
    if start_x <= centro_x_abs <= end_x and end_y == alto_total:
        cx = margen + (centro_x_abs - start_x) * tamano_bloque
        lim_inf = margen + q_alto * tamano_bloque
        draw.polygon([(cx, lim_inf + 15), (cx - 6, lim_inf + 5), (cx + 6, lim_inf + 5)], fill="red")
    if start_y <= centro_y_abs <= end_y and start_x == 0:
        cy = margen + (centro_y_abs - start_y) * tamano_bloque
        draw.polygon([(margen - 15, cy), (margen - 5, cy - 6), (margen - 5, cy + 6)], fill="red")
    if start_y <= centro_y_abs <= end_y and end_x == ancho_total:
        cy = margen + (centro_y_abs - start_y) * tamano_bloque
        lim_der = margen + q_ancho * tamano_bloque
        draw.polygon([(lim_der + 15, cy), (lim_der + 5, cy - 6), (lim_der + 5, cy + 6)], fill="red")

def crear_pagina_patron(pixeles, leyenda_colores, start_x, end_x, start_y, end_y, ancho_total, alto_total, tamano_bloque, margen, f_simbolos, f_texto, titulo_seccion, modo="color"):
    q_ancho = end_x - start_x
    q_alto = end_y - start_y
    
    img_pagina = Image.new("RGB", (q_ancho * tamano_bloque + margen * 2, q_alto * tamano_bloque + margen * 2), color=(255, 255, 255))
    draw = ImageDraw.Draw(img_pagina)
    
    draw.text((margen, margen - 40), f"Sección: {titulo_seccion} ({modo.upper()})", fill=(50, 50, 50), font=f_texto)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            color_actual = pixeles[x, y]
            letra = leyenda_colores[color_actual]["simbolo"]
            
            px = x - start_x
            py = y - start_y
            x0 = margen + (px * tamano_bloque)
            y0 = margen + (py * tamano_bloque)
            x1 = x0 + tamano_bloque
            y1 = y0 + tamano_bloque
            
            if modo == "color":
                draw.rectangle([x0, y0, x1, y1], fill=color_actual)
                color_texto = color_contraste(color_actual, umbral=40)
            else:
                color_texto = (0, 0, 0)
                
            try:
                left, top, right, bottom = f_simbolos.getbbox(letra)
                w, h = right - left, bottom - top
            except AttributeError:
                w, h = 10, 15
                
            offset_x = (tamano_bloque - w) / 2
            offset_y = (tamano_bloque - h) / 2 - 2
            
            draw.text((x0 + offset_x, y0 + offset_y), letra, fill=color_texto, font=f_simbolos)
            
    dibujar_guias_cuadrante(draw, start_x, end_x, start_y, end_y, ancho_total, alto_total, tamano_bloque, margen, f_texto)
    return img_pagina

def generar_patron_pdf(imagen_bytes, ancho_puntadas, numero_colores):
    """Genera el PDF del patrón de punto de cruz y retorna los bytes del PDF."""
    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
    
    nombre_base = "patron_punto_cruz"
    
    proporcion = ancho_puntadas / float(img.size[0])
    alto_puntadas = int(float(img.size[1]) * float(proporcion))
    
    img_pixelada = img.resize((ancho_puntadas, alto_puntadas), Image.Resampling.NEAREST)
    img_cuantizada = img_pixelada.quantize(colors=numero_colores).convert("RGB")
    pixeles = img_cuantizada.load()
    
    colores_unicos = []
    conteo_puntadas = {}
    for y in range(alto_puntadas):
        for x in range(ancho_puntadas):
            color = pixeles[x, y]
            if color not in colores_unicos:
                colores_unicos.append(color)
                conteo_puntadas[color] = 0
            conteo_puntadas[color] += 1
                
    lista_simbolos = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#%&+=?★♦♠♣♥♫☼▲▼◄►")
    leyenda_colores = {}
    
    for indice, color in enumerate(colores_unicos):
        mejor_codigo_dmc = None
        menor_dist = float('inf')
        for codigo, info in COLORES_DMC.items():
            dist = distancia_color_ponderada(color, info["rgb"])
            if dist < menor_dist:
                menor_dist = dist
                mejor_codigo_dmc = codigo
                
        simbolo = lista_simbolos[indice % len(lista_simbolos)]
        leyenda_colores[color] = {
            "simbolo": simbolo,
            "dmc_cod": mejor_codigo_dmc,
            "dmc_nombre": COLORES_DMC[mejor_codigo_dmc]["nombre"],
            "puntadas": conteo_puntadas[color]
        }
        
    tamano_bloque = 30 
    margen = 60
    f_simbolos, f_texto, f_titulo = obtener_fuentes(tamano_bloque)
    
    # PÁGINA 1: PORTADA
    ancho_portada = ((ancho_puntadas // 2) * tamano_bloque) + (margen * 2)
    alto_portada = ((alto_puntadas // 2) * tamano_bloque) + (margen * 2)
    
    pag1_portada = Image.new("RGB", (ancho_portada, alto_portada), color=(255, 255, 255))
    draw_portada = ImageDraw.Draw(pag1_portada)
    
    draw_portada.text((margen, margen), "Patrón de Punto de Cruz", fill=(0,0,0), font=f_titulo)
    draw_portada.text((margen, margen + 50), f"Proyecto: {nombre_base}", fill=(100,100,100), font=f_texto)
    
    tamano_miniatura = int(min(ancho_portada, alto_portada) * 0.4)
    img_miniatura = img.resize((tamano_miniatura, int(tamano_miniatura * (alto_puntadas/ancho_puntadas))), Image.Resampling.LANCZOS)
    pos_x = (ancho_portada - img_miniatura.width) // 2
    pos_y = margen + 100
    pag1_portada.paste(img_miniatura, (pos_x, pos_y))
    
    y_resumen = pos_y + img_miniatura.height + 40
    total_puntadas = ancho_puntadas * alto_puntadas
    draw_portada.text((pos_x, y_resumen), f"Tamaño Total: {ancho_puntadas} x {alto_puntadas} pts", fill=(0,0,0), font=f_texto)
    draw_portada.text((pos_x, y_resumen + 25), f"Páginas de Patrón: 4", fill=(0,0,0), font=f_texto)
    draw_portada.text((pos_x, y_resumen + 50), f"Total de Colores: {numero_colores}", fill=(0,0,0), font=f_texto)

    # PÁGINAS DEL PATRÓN (2x2 GRID)
    mid_x = ancho_puntadas // 2
    mid_y = alto_puntadas // 2
    
    cuadrantes = [
        (0, mid_x, 0, mid_y, "Superior Izquierda"),
        (mid_x, ancho_puntadas, 0, mid_y, "Superior Derecha"),
        (0, mid_x, mid_y, alto_puntadas, "Inferior Izquierda"),
        (mid_x, ancho_puntadas, mid_y, alto_puntadas, "Inferior Derecha")
    ]
    
    paginas_adicionales = []
    
    # 4 páginas A COLOR
    for sx, ex, sy, ey, titulo in cuadrantes:
        img_q = crear_pagina_patron(pixeles, leyenda_colores, sx, ex, sy, ey, ancho_puntadas, alto_puntadas, tamano_bloque, margen, f_simbolos, f_texto, titulo, modo="color")
        paginas_adicionales.append(img_q)
        
    # 4 páginas BLANCO Y NEGRO
    for sx, ex, sy, ey, titulo in cuadrantes:
        img_q = crear_pagina_patron(pixeles, leyenda_colores, sx, ex, sy, ey, ancho_puntadas, alto_puntadas, tamano_bloque, margen, f_simbolos, f_texto, titulo, modo="bn")
        paginas_adicionales.append(img_q)
            
    # PÁGINA FINAL: LEYENDA
    pag_leyenda = Image.new("RGB", (ancho_portada, max(alto_portada, 800)), color=(255, 255, 255))
    draw_leyenda = ImageDraw.Draw(pag_leyenda)
    
    draw_leyenda.text((margen, margen), "LEYENDA DE COLORES Y PUNTADAS", fill=(0,0,0), font=f_titulo)
    
    x_offset = margen
    y_offset = margen + 60
    limite_y = pag_leyenda.height - 100
    
    colores_ordenados = sorted(leyenda_colores.items(), key=lambda item: item[1]['puntadas'], reverse=True)
    
    for color, datos in colores_ordenados:
        letra = datos["simbolo"]
        dmc_cod = datos["dmc_cod"]
        dmc_nom = datos["dmc_nombre"]
        puntadas = datos["puntadas"]
        
        if y_offset > limite_y:
            y_offset = margen + 60
            x_offset += int(ancho_portada / 2) 
        
        draw_leyenda.rectangle([x_offset, y_offset, x_offset + tamano_bloque, y_offset + tamano_bloque], fill=color, outline=(0,0,0))
        color_txt_leyenda = color_contraste(color, umbral=40)
        
        try:
            w = f_simbolos.getbbox(letra)[2] - f_simbolos.getbbox(letra)[0]
        except AttributeError:
            w = 10
        offset_x_leyenda = (tamano_bloque - w) / 2
        
        draw_leyenda.text((x_offset + offset_x_leyenda, y_offset - 2), letra, fill=color_txt_leyenda, font=f_simbolos)
        
        texto_leyenda = f"DMC {dmc_cod} ({dmc_nom})"
        draw_leyenda.text((x_offset + tamano_bloque + 15, y_offset + 5), texto_leyenda, fill=(0,0,0), font=f_texto)
        draw_leyenda.text((x_offset + tamano_bloque + 250, y_offset + 5), f"[{puntadas} pts]", fill=(100,100,100), font=f_texto)
        
        y_offset += 45

    paginas_adicionales.append(pag_leyenda)

    # Guardar PDF en memoria
    pdf_buffer = io.BytesIO()
    pag1_portada.save(pdf_buffer, "PDF", save_all=True, append_images=paginas_adicionales)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue(), len(paginas_adicionales) + 1, ancho_puntadas, alto_puntadas, len(colores_unicos), leyenda_colores


# ---------------------------------------------------------
# STREAMLIT APP
# ---------------------------------------------------------
st.set_page_config(
    page_title="Generador de Patrones de Punto de Cruz",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Generador de Patrones de Punto de Cruz")
st.markdown("""
Convierte cualquier imagen en un patrón profesional de punto de cruz (cross-stitch) 
con leyenda de colores DMC, guías de cuadrante y PDF listo para imprimir.
""")

with st.sidebar:
    st.header("⚙️ Parámetros")
    ancho_puntadas = st.slider("Ancho en puntadas", 20, 200, 80, 5,
                               help="Número de puntos de ancho. Más ancho = más detalle pero patrón más grande.")
    numero_colores = st.slider("Número de colores", 2, 30, 13, 1,
                               help="Cantidad de colores DMC a usar. Menos colores = patrón más simple.")
    
    st.markdown("---")
    st.markdown("### 📋 Información")
    st.markdown("""
    - **Salida**: PDF de 10 páginas (portada, 4 cuadrantes color, 4 cuadrantes B/N, leyenda)
    - **Colores**: Basado en paleta DMC oficial
    - **Símbolos**: Letras, números y símbolos únicos por color
    """)

# Upload
uploaded_file = st.file_uploader(
    "📤 Sube una imagen (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    help="La imagen se redimensionará al ancho en puntadas especificado manteniendo la proporción."
)

if uploaded_file is not None:
    # Show preview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📷 Imagen original")
        original_img = Image.open(uploaded_file)
        st.image(original_img, caption=f"Original: {original_img.size[0]}x{original_img.size[1]} px", use_container_width=True)
    
    with col2:
        st.subheader("👁️ Vista previa del patrón (cuantizada)")
        # Generate preview
        img_preview = original_img.convert("RGB")
        prop = ancho_puntadas / float(img_preview.size[0])
        alto_preview = int(float(img_preview.size[1]) * prop)
        img_pixelada = img_preview.resize((ancho_puntadas, alto_preview), Image.Resampling.NEAREST)
        img_cuantizada = img_pixelada.quantize(colors=numero_colores).convert("RGB")
        # Scale up for visibility
        preview_display = img_cuantizada.resize((ancho_puntadas * 8, alto_preview * 8), Image.Resampling.NEAREST)
        st.image(preview_display, caption=f"Patrón: {ancho_puntadas}x{alto_preview} pts, {numero_colores} colores", use_container_width=True)
    
    if st.button("🎨 Generar Patrón PDF", type="primary", use_container_width=True):
        with st.spinner("Generando patrón... Esto puede tardar unos segundos."):
            try:
                imagen_bytes = uploaded_file.getvalue()
                pdf_bytes, num_paginas, w, h, n_colores, leyenda = generar_patron_pdf(
                    imagen_bytes, ancho_puntadas, numero_colores
                )
                
                st.success(f"✅ Patrón generado: {num_paginas} páginas | {w}x{h} pts | {n_colores} colores")
                
                # Download button
                st.download_button(
                    label="📥 Descargar PDF del Patrón",
                    data=pdf_bytes,
                    file_name=f"patron_punto_cruz_{ancho_puntadas}x{numero_colores}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Show legend table
                st.subheader("📋 Leyenda de Colores")
                legend_data = []
                for color, datos in sorted(leyenda.items(), key=lambda x: x[1]['puntadas'], reverse=True):
                    r, g, b = color
                    legend_data.append({
                        "Símbolo": datos["simbolo"],
                        "DMC": datos["dmc_cod"],
                        "Nombre": datos["dmc_nombre"],
                        "Puntadas": datos["puntadas"],
                        "Color": f"#{r:02x}{g:02x}{b:02x}"
                    })
                
                st.dataframe(legend_data, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"❌ Error al generar el patrón: {str(e)}")
                st.exception(e)

st.markdown("---")
st.markdown("""
<small>
Hecho con ❤️ usando Streamlit y Pillow | 
Basado en el script original de generación de patrones de punto de cruz
</small>
""", unsafe_allow_html=True)