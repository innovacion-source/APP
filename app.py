import streamlit as st
import pandas as pd
import datetime

# Configuración de la página
st.set_page_config(page_title="Hotel Innova - Buzón de Ideas", layout="wide")

# Simulación de una base de datos simple (en una app real, esto se conectaría a Google Sheets)
if 'db_ideas' not in st.session_state:
    st.session_state.db_ideas = pd.DataFrame(columns=["Fecha", "Colaborador", "Departamento", "Idea", "Estado"])

# --- BARRA LATERAL (Navegación) ---
st.sidebar.title("Navegación")
modo = st.sidebar.radio("Ir a:", ["Portal de Ideas (Usuario)", "Panel de Control (Admin)"])

# --- MODO USUARIO ---
if modo == "Portal de Ideas (Usuario)":
    st.title("💡 Comparte tu idea para mejorar el Hotel")
    st.write("Tu experiencia es clave para nuestra innovación.")

    with st.form("form_idea", clear_on_submit=True):
        nombre = st.text_input("Nombre (Opcional)")
        depto = st.selectbox("Tu Departamento", ["Recepción", "A&B", "Housekeeping", "Mantenimiento", "Administración"])
        idea_texto = st.text_area("Describe tu idea o mejora:")
        
        enviar = st.form_submit_button("Enviar Idea")
        
        if enviar:
            if idea_texto:
                nueva_fila = {
                    "Fecha": datetime.date.today(),
                    "Colaborador": nombre if nombre else "Anónimo",
                    "Departamento": depto,
                    "Idea": idea_texto,
                    "Estado": "Pendiente"
                }
                st.session_state.db_ideas = pd.concat([st.session_state.db_ideas, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.success("¡Gracias! Tu idea ha sido registrada.")
            else:
                st.error("Por favor, describe tu idea antes de enviar.")

# --- MODO ADMINISTRADOR ---
elif modo == "Panel de Control (Admin)":
    st.title("📊 Panel de Gestión de Innovación")
    
    password = st.sidebar.text_input("Contraseña de Acceso", type="password")
    if password == "hotel2024":  # Ejemplo de seguridad simple
        
        if st.session_state.db_ideas.empty:
            st.info("Aún no se han registrado ideas.")
        else:
            # Estadísticas rápidas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Ideas por Departamento")
                conteo_depto = st.session_state.db_ideas["Departamento"].value_counts()
                st.bar_chart(conteo_depto)
            
            with col2:
                st.subheader("Resumen Estadístico")
                st.write(f"Total de ideas recibidas: {len(st.session_state.db_ideas)}")
                st.dataframe(st.session_state.db_ideas[["Fecha", "Departamento", "Estado"]])

            st.subheader("Detalle de todas las ideas")
            st.table(st.session_state.db_ideas)
            
            # Botón para descargar reporte
            csv = st.session_state.db_ideas.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Reporte Excel/CSV", data=csv, file_name="reporte_innovacion.csv", mime="text/csv")
    else:
        st.warning("Por favor, ingresa la contraseña de administrador en la barra lateral.")