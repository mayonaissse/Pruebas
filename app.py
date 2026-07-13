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

def generar_patron_pdf(imagen_bytes, ancho_puntadas, numero_colores, tamano_bloque=30, margen=60, mostrar_bn=True):
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
    paginas_patron = 4 + (4 if mostrar_bn else 0)
    draw_portada.text((pos_x, y_resumen), f"Tamaño Total: {ancho_puntadas} x {alto_puntadas} pts", fill=(0,0,0), font=f_texto)
    draw_portada.text((pos_x, y_resumen + 25), f"Páginas de Patrón: {paginas_patron}", fill=(0,0,0), font=f_texto)
    draw_portada.text((pos_x, y_resumen + 50), f"Total de Colores: {len(colores_unicos)}", fill=(0,0,0), font=f_texto)

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
        
    # 4 páginas BLANCO Y NEGRO (si está activado)
    if mostrar_bn:
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
Convierte tu foto en un patrón de punto de cruz listo para imprimir.
Sube una imagen, ajusta los parámetros y descarga el PDF.
""")

# Upload first
uploaded_file = st.file_uploader(
    "📤 Sube una imagen (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    help="La imagen se redimensionará al ancho en puntadas especificado manteniendo la proporción."
)

if uploaded_file is not None:
    original_img = Image.open(uploaded_file)
    
    # Calculate preview values for sliders' defaults
    # Default values
    if 'ancho_puntadas' not in st.session_state:
        st.session_state.ancho_puntadas = 80
    if 'numero_colores' not in st.session_state:
        st.session_state.numero_colores = 13
    if 'tamano_bloque' not in st.session_state:
        st.session_state.tamano_bloque = 30
    if 'margen' not in st.session_state:
        st.session_state.margen = 60
    if 'mostrar_bn' not in st.session_state:
        st.session_state.mostrar_bn = True
    
    # Sliders row - horizontal layout above preview
    st.subheader("⚙️ Ajustes")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        ancho_puntadas = st.slider(
            "Ancho (puntos)", 20, 200, st.session_state.ancho_puntadas, 5,
            key="slider_ancho", help="Más puntos = más detalle"
        )
        st.session_state.ancho_puntadas = ancho_puntadas
    with col2:
        numero_colores = st.slider(
            "Colores", 2, 30, st.session_state.numero_colores, 1,
            key="slider_colores", help="Menos = más fácil de bordar"
        )
        st.session_state.numero_colores = numero_colores
    with col3:
        tamano_bloque = st.slider(
            "Tamaño punto (px)", 20, 50, st.session_state.tamano_bloque, 2,
            key="slider_tamano", help="Más grande = más fácil de ver"
        )
        st.session_state.tamano_bloque = tamano_bloque
    with col4:
        margen = st.slider(
            "Margen (px)", 30, 100, st.session_state.margen, 5,
            key="slider_margen", help="Espacio para numeración"
        )
        st.session_state.margen = margen
    with col5:
        st.write("")  # vertical align
        st.write("")
        mostrar_bn = st.checkbox(
            "Incluir B/N", value=st.session_state.mostrar_bn,
            key="check_bn", help="4 páginas extra solo símbolos"
        )
        st.session_state.mostrar_bn = mostrar_bn
    
    st.markdown("---")
    
    # Preview section - full width
    st.subheader("👁️ Vista previa en tiempo real")
    
    # Two columns for original and quantized
    prev_col1, prev_col2 = st.columns(2)
    
    with prev_col1:
        st.caption("📷 Imagen original")
        st.image(original_img, caption=f"Original: {original_img.size[0]}x{original_img.size[1]} px", use_container_width=True)
    
    with prev_col2:
        st.caption("🧵 Patrón cuantizado (simulación)")
        img_preview = original_img.convert("RGB")
        prop = ancho_puntadas / float(img_preview.size[0])
        alto_preview = int(float(img_preview.size[1]) * prop)
        img_pixelada = img_preview.resize((ancho_puntadas, alto_preview), Image.Resampling.NEAREST)
        img_cuantizada = img_pixelada.quantize(colors=numero_colores).convert("RGB")
        preview_display = img_cuantizada.resize((ancho_puntadas * 8, alto_preview * 8), Image.Resampling.NEAREST)
        st.image(preview_display, caption=f"Patrón: {ancho_puntadas}x{alto_preview} pts, {numero_colores} colores", use_container_width=True)
    
    # Info summary
    st.info(f"**Resumen:** {ancho_puntadas}×{alto_preview} puntos | {numero_colores} colores | ~{ancho_puntadas * alto_preview:,} puntadas totales")
    
    # Generate button BELOW preview
    st.markdown("---")
    gen_col1, gen_col2, gen_col3 = st.columns([1, 2, 1])
    with gen_col2:
        if st.button("🎨 Generar Patrón PDF", type="primary", use_container_width=True):
            with st.spinner("Generando patrón... Esto puede tardar unos segundos."):
                try:
                    imagen_bytes = uploaded_file.getvalue()
                    pdf_bytes, num_paginas, w, h, n_colores, leyenda = generar_patron_pdf(
                        imagen_bytes, ancho_puntadas, numero_colores, 
                        tamano_bloque=tamano_bloque, margen=margen, mostrar_bn=mostrar_bn
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

else:
    # No image uploaded - show settings centered
    st.info("👆 Sube una imagen para comenzar")
    
    st.subheader("⚙️ Ajustes del Patrón")
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    with col_a:
        ancho_puntadas = st.slider(
            "Ancho (puntos)", 20, 200, 80, 5,
            help="Más puntos = más detalle"
        )
    with col_b:
        numero_colores = st.slider(
            "Colores", 2, 30, 13, 1,
            help="Menos = más fácil de bordar"
        )
    with col_c:
        tamano_bloque = st.slider(
            "Tamaño punto (px)", 20, 50, 30, 2,
            help="Más grande = más fácil de ver"
        )
    with col_d:
        margen = st.slider(
            "Margen (px)", 30, 100, 60, 5,
            help="Espacio para numeración"
        )
    with col_e:
        st.write("")
        st.write("")
        mostrar_bn = st.checkbox(
            "Incluir B/N", value=True,
            help="4 páginas extra solo símbolos"
        )

    st.markdown("---")

    # Info box
    with st.expander("📄 Qué incluye el PDF", expanded=False):
        st.markdown("""
        - **Portada** con miniatura y resumen
        - **4 páginas a color** (cuadrantes del patrón)
        - **4 páginas blanco y negro** (solo símbolos) — si está activado
        - **Leyenda** con códigos DMC y cantidad de puntos
        """)

st.markdown("---")
st.markdown("""
<small>
Hecho con ❤️ usando Streamlit y Pillow | 
Basado en el script original de generación de patrones de punto de cruz
</small>
""", unsafe_allow_html=True)