import streamlit as st
import pandas as pd
import io
import xlsxwriter
st.set_page_config(page_title="Registro de Equipos", layout="wide")
# Inicialización del estado
if "estado" not in st.session_state:
   st.session_state.estado = {
       "evento_configurado": False,
       "datos_evento": {},
       "barras": [],
       "datos_barras": [],
       "datos_equipos": []
   }
estado = st.session_state.estado
st.title("📋 Registro de Equipos por Barra")
# 1. Registro de datos del evento
if not estado["evento_configurado"]:
   with st.form("configurar_evento"):
       st.subheader("🔧 Configurar Evento")
       nombre_evento = st.text_input("Nombre del evento")
       codigo_evento = st.text_input("Código del evento")
       num_mostradores = st.number_input("Número total de mostradores", min_value=0, step=1)
       num_botelleros = st.number_input("Número total de botelleros", min_value=0, step=1)
       num_vitrinas = st.number_input("Número total de vitrinas", min_value=0, step=1)
       num_enfriadores = st.number_input("Número total de enfriadores", min_value=0, step=1)
       num_kits = st.number_input("Número total de kits portátiles", min_value=0, step=1)
       num_barras = st.number_input("Número total de barras", min_value=1, step=1)
       submitted = st.form_submit_button("Guardar evento")
       if submitted:
           estado["evento_configurado"] = True
           estado["datos_evento"] = {
               "nombre": nombre_evento,
               "codigo": codigo_evento,
               "mostradores": num_mostradores,
               "botelleros": num_botelleros,
               "vitrinas": num_vitrinas,
               "enfriadores": num_enfriadores,
               "kits": num_kits,
               "num_barras": num_barras
           }
           st.experimental_rerun()
# 2. Registro de barras
elif len(estado["barras"]) < estado["datos_evento"]["num_barras"]:
   num_actual = len(estado["barras"]) + 1
   st.subheader(f"🏷️ Barra {num_actual} de {estado['datos_evento']['num_barras']}")
   with st.form(f"barra_{num_actual}"):
       nombre_barra = st.text_input("Nombre o ubicación de la barra")
       botelleros = st.number_input("Cantidad de botelleros", min_value=0, step=1)
       vitrinas = st.number_input("Cantidad de vitrinas", min_value=0, step=1)
       enfriadores = st.number_input("Cantidad de enfriadores", min_value=0, step=1)
       kits = st.number_input("Cantidad de kits portátiles", min_value=0, step=1)
       mostradores = st.number_input("Cantidad de mostradores", min_value=0, step=1)
       submitted = st.form_submit_button("Guardar barra")
       if submitted:
           barra_id = f"BARRA_{num_actual:02d}"
           estado["barras"].append(barra_id)
           estado["datos_barras"].append({
               "barra_id": barra_id,
               "nombre_barra": nombre_barra,
               "botelleros": botelleros,
               "vitrinas": vitrinas,
               "enfriadores": enfriadores,
               "kits": kits,
               "mostradores": mostradores
           })
           def leer_tags(cantidad, tipo):
               tags = []
               if cantidad > 0:
                   st.info(f"Introduce los tags NFC de {cantidad} {tipo}(s)")
               for i in range(cantidad):
                   tag = st.text_input(f"{tipo} {i + 1}", key=f"{barra_id}_{tipo}_{i}")
                   if tag:
                       tags.append(tag)
               return tags
           for tipo, cantidad in [("Botellero", botelleros), ("Vitrina", vitrinas),
                                  ("Enfriador", enfriadores), ("Kit Portátil", kits)]:
               tags = leer_tags(cantidad, tipo)
               for t in tags:
                   estado["datos_equipos"].append({
                       "barra_id": barra_id,
                       "nombre_barra": nombre_barra,
                       "tipo": tipo,
                       "tag": t
                   })
           st.experimental_rerun()
# 3. Mostrar resumen y permitir edición
else:
   st.success("✅ Registro completo")
   st.subheader("📊 Resumen del evento")
   df_barras = pd.DataFrame(estado["datos_barras"])
   df_equipos = pd.DataFrame(estado["datos_equipos"])
   st.subheader("✏️ Editar información de las barras")
   edited_df = st.data_editor(
       df_barras,
       num_rows="dynamic",
       use_container_width=True,
       key="edicion_barras"
   )
   estado["datos_barras"] = edited_df.to_dict(orient="records")
   st.write("📋 Datos de equipos registrados")
   st.dataframe(df_equipos, use_container_width=True)
   # Generar Excel
   output = io.BytesIO()
   with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
       pd.DataFrame(estado["datos_barras"]).to_excel(writer, index=False, sheet_name='Barras')
       df_equipos.to_excel(writer, index=False, sheet_name='Equipos')
       writer.save()
   st.download_button(
       label="📥 Descargar Excel",
       data=output.getvalue(),
       file_name=f"{estado['datos_evento']['nombre']}_{estado['datos_evento']['codigo']}.xlsx",
       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
   )
