import streamlit as st
import pandas as pd
import datetime
import json
from io import BytesIO
st.set_page_config(page_title="Control de Equipos NFC", layout="centered")
# Estado inicial
if "estado" not in st.session_state:
   st.session_state.estado = {
       "evento_registrado": False,
       "barra_actual": 0,
       "datos_barras": [],
       "equipos": [],
       "registro_completo": False
   }
# Guardar estado
def guardar_estado():
   datos = {
       "evento_info": st.session_state.estado["evento_info"],
       "barra_actual": st.session_state.estado["barra_actual"],
       "datos_barras": st.session_state.estado["datos_barras"],
       "equipos": st.session_state.estado["equipos"],
       "registro_completo": st.session_state.estado["registro_completo"]
   }
   return json.dumps(datos, default=str)
# Cargar estado
def cargar_estado(data):
   estado = json.loads(data)
   st.session_state.estado["evento_info"] = estado["evento_info"]
   st.session_state.estado["barra_actual"] = estado["barra_actual"]
   st.session_state.estado["datos_barras"] = estado["datos_barras"]
   st.session_state.estado["equipos"] = estado["equipos"]
   st.session_state.estado["evento_registrado"] = True
   st.session_state.estado["registro_completo"] = estado.get("registro_completo", False)
st.title("🧊 Control de Equipos de Frío por NFC")
# Cargar archivo
archivo_cargado = st.file_uploader("📂 Cargar evento guardado (.json)", type=["json"])
if archivo_cargado is not None and not st.session_state.estado["evento_registrado"]:
   cargar_estado(archivo_cargado.read().decode())
   st.experimental_rerun()
# Paso 1: Datos del evento
if not st.session_state.estado["evento_registrado"]:
   st.header("🔧 Configuración del Evento")
   nombre_evento = st.text_input("Nombre del evento")
   codigo_evento = st.text_input("Código del evento")
   num_mostradores = st.number_input("Total de Mostradores", min_value=0)
   num_botelleros = st.number_input("Total de Botelleros", min_value=0)
   num_vitrinas = st.number_input("Total de Vitrinas", min_value=0)
   num_enfriadores = st.number_input("Total de Enfriadores", min_value=0)
   num_kits = st.number_input("Total de Kits portátiles", min_value=0)
   num_barras = st.number_input("Número total de barras", min_value=1)
   if st.button("✅ Iniciar registro por barra"):
       st.session_state.estado["evento_info"] = {
           "nombre": nombre_evento,
           "codigo": codigo_evento,
           "mostradores": num_mostradores,
           "botelleros": num_botelleros,
           "vitrinas": num_vitrinas,
           "enfriadores": num_enfriadores,
           "kits": num_kits,
           "num_barras": int(num_barras)
       }
       st.session_state.estado["evento_registrado"] = True
       st.experimental_rerun()
# Paso 2: Registro de barras
elif st.session_state.estado["barra_actual"] < st.session_state.estado["evento_info"]["num_barras"]:
   idx = st.session_state.estado["barra_actual"]
   st.header(f"📍 Barra {idx+1} de {st.session_state.estado['evento_info']['num_barras']}")
   nombre_barra = st.text_input("Nombre de la barra", key=f"nombre_barra_{idx}")
   mostradores = st.number_input("Mostradores", min_value=0, key=f"most_{idx}")
   botelleros = st.number_input("Nº Botelleros", min_value=0, key=f"bot_{idx}")
   vitrinas = st.number_input("Nº Vitrinas", min_value=0, key=f"vit_{idx}")
   enfriadores = st.number_input("Nº Enfriadores", min_value=0, key=f"enf_{idx}")
   kits = st.number_input("Nº Kits portátiles", min_value=0, key=f"kit_{idx}")
   equipos_barra = []
   def leer_tags(tipo, cantidad):
       st.subheader(f"{tipo}s")
       for i in range(int(cantidad)):
           tag = st.text_input(f"{tipo} {i+1}", key=f"{tipo}_{idx}_{i}")
           if tag:
               if tag.strip() in [e["serial"] for e in st.session_state.estado["equipos"]]:
                   st.warning(f"{tipo} {i+1}: Este código ya fue registrado")
               else:
                   equipos_barra.append({
                       "evento": st.session_state.estado["evento_info"]["nombre"],
                       "codigo_evento": st.session_state.estado["evento_info"]["codigo"],
                       "barra": nombre_barra,
                       "tipo": tipo,
                       "serial": tag.strip(),
                       "timestamp": datetime.datetime.now().isoformat()
                   })
   leer_tags("Botellero", botelleros)
   leer_tags("Vitrina", vitrinas)
   leer_tags("Enfriador", enfriadores)
   leer_tags("Kit portátil", kits)
   col1, col2 = st.columns(2)
   if col1.button("⬅️ Volver a barra anterior", disabled=idx == 0):
       st.session_state.estado["barra_actual"] -= 1
       st.experimental_rerun()
   if col2.button("💾 Guardar barra y continuar"):
       if idx < len(st.session_state.estado["datos_barras"]):
           st.session_state.estado["datos_barras"][idx] = {
               "evento": st.session_state.estado["evento_info"]["nombre"],
               "codigo_evento": st.session_state.estado["evento_info"]["codigo"],
               "barra": nombre_barra,
               "mostradores": mostradores,
               "botelleros": botelleros,
               "vitrinas": vitrinas,
               "enfriadores": enfriadores,
               "kits_portatiles": kits
           }
       else:
           st.session_state.estado["datos_barras"].append({
               "evento": st.session_state.estado["evento_info"]["nombre"],
               "codigo_evento": st.session_state.estado["evento_info"]["codigo"],
               "barra": nombre_barra,
               "mostradores": mostradores,
               "botelleros": botelleros,
               "vitrinas": vitrinas,
               "enfriadores": enfriadores,
               "kits_portatiles": kits
           })
       st.session_state.estado["equipos"].extend(equipos_barra)
       st.session_state.estado["barra_actual"] += 1
       json_bytes = guardar_estado().encode()
       st.download_button(
           "💾 Descargar progreso (.json)",
           data=json_bytes,
           file_name=f"{st.session_state.estado['evento_info']['codigo']}_progreso.json",
           mime="application/json"
       )
       st.experimental_rerun()
# Paso final
elif not st.session_state.estado["registro_completo"]:
   st.session_state.estado["registro_completo"] = True
   st.success("🎉 Registro de todas las barras completado")
   df_barras = pd.DataFrame(st.session_state.estado["datos_barras"])
   df_equipos = pd.DataFrame(st.session_state.estado["equipos"])
   st.subheader("📊 Resumen por barra")
   st.dataframe(df_barras)
   st.subheader("📦 Equipos registrados (por tag NFC)")
   st.dataframe(df_equipos)
   output = BytesIO()
   with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
       df_barras.to_excel(writer, sheet_name="Resumen por barra", index=False)
       df_equipos.to_excel(writer, sheet_name="Equipos por tag", index=False)
   output.seek(0)
   st.download_button(
       "📥 Descargar Excel completo",
       data=output,
       file_name=f"{st.session_state.estado['evento_info']['codigo']}_registro_evento.xlsx",
       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
   )
