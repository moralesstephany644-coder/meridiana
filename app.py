import streamlit as st
from modelos import ELIPSOIDES, obtener_parametros
from calculos import geograficas_a_utm, utm_a_geograficas, gms_a_decimal

st.set_page_config(page_title="MERIDIANA | Transformador geodésico", page_icon="M", layout="wide")

# Diseño alternativo: interfaz clara, flujo por etapas y resultados en panel inferior.
st.markdown("""
<style>
:root { color-scheme: light; }
.stApp { background: #F7F3F4; color: #493443; }
.block-container { max-width: 1440px; padding-top: 1.25rem; padding-bottom: 2.5rem; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #EFE5EA; }
.hero { background: #56384B; border-radius: 18px; padding: 1.35rem 1.7rem; color: #fff; margin-bottom: 1.1rem; border: 1px solid #6E5063; position: relative; overflow: hidden; }
.hero-kicker { color: #E9D8E1; letter-spacing: .17em; font-size: .72rem; text-transform: uppercase; }
.hero-name { font-family: Georgia, serif; font-size: 2.25rem; font-weight: 700; letter-spacing: .12em; margin: .18rem 0; }
.hero-desc { color: #F1E6EC; font-size: .95rem; }
.hero-mark { float: right; color: #D7B5C5; font-size: 3.2rem; opacity: .7; margin-right: .3rem; }
.section-head { color: #75465C; text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; font-weight: 700; margin: .45rem 0 .8rem; }
.card-title { color: #493443; font-weight: 700; font-size: 1.05rem; margin-bottom: .7rem; }
.note { background: #F1E6EB; border-left: 3px solid #B77C91; border-radius: 7px; padding: .8rem 1rem; color: #634456; }
.result-banner { background: #75465C; border-radius: 12px; padding: .85rem 1.15rem; color: white; margin-bottom: .65rem; border: 1px solid #8C6379; }
.result-banner small { color: #E8D4DC; text-transform: uppercase; letter-spacing: .12em; }
.stSelectbox label, .stNumberInput label, .stRadio label, .stCheckbox label { color: #634456 !important; }
div.stButton > button { background: #A96785; color: white; border: 0; border-radius: 9px; min-height: 2.8rem; font-weight: 700; }
div.stButton > button:hover { background: #8D526E; color: white; border: 0; }
hr { border-color: #DCCBD4; }
.result-list { border: 1px solid #E1CFD8; border-radius: 14px; background: #FFFCFD; padding: .3rem 1rem; }
.result-row { display: grid; grid-template-columns: 42px minmax(170px, 1fr) minmax(250px, 1.35fr); align-items: center; gap: .8rem; padding: .75rem .15rem; border-bottom: 1px solid #E8D9E0; }
.result-row:last-child { border-bottom: none; }
.result-symbol { background: #F2E4EB; color: #85566D; border-radius: 9px; width: 38px; height: 34px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
.result-label { color: #634456; font-size: .92rem; }
.result-value { color: #56384B; font-family: Georgia, serif; font-size: 1.45rem; font-weight: 600; overflow-wrap: anywhere; }
.atlas-note { color: #967F8D; font-size: .76rem; letter-spacing: .05em; border-top: 1px solid #E1CFD8; margin-top: .7rem; padding-top: .6rem; }
@media (max-width: 750px) { .result-row { grid-template-columns: 36px 1fr; } .result-value { grid-column: 2; font-size: 1.15rem; } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="hero-mark">⌖</div>
  <div class="hero-kicker">Cartografía 2 · Proyección UTM</div>
  <div class="hero-name">MERIDIANA</div>
  <div class="hero-desc">Transformación de coordenadas geográficas y UTM</div>
</div>
""", unsafe_allow_html=True)

# Modelo geodésico en una tarjeta de configuración horizontal
st.markdown('<div class="section-head">01 · Modelo de referencia</div>', unsafe_allow_html=True)
with st.container(border=True):
    c_ell, c_params = st.columns([1, 2.2], vertical_alignment="center")
    with c_ell:
        nombres = list(ELIPSOIDES.keys())
        default_idx = nombres.index("WGS84") if "WGS84" in nombres else 0
        elipsoide = st.selectbox("Elipsoide", nombres, index=default_idx)
    par = obtener_parametros(elipsoide)
    with c_params:
        st.markdown(f"**{elipsoide}**")
        st.caption(f"Semieje mayor a = {par['a']:,.3f} m  ·  Semieje menor b = {par['b']:,.3f} m")
        st.caption(f"e² = {par['e2']:.12f}  |  e'² = {par['e_prime2']:.12f}")

st.markdown('<div class="section-head">02 · Tipo de transformación</div>', unsafe_allow_html=True)
modo = st.radio("Dirección", ["Geográficas → UTM", "UTM → Geográficas"], horizontal=True, label_visibility="collapsed")

st.markdown('<div class="section-head">03 · Captura de coordenadas</div>', unsafe_allow_html=True)
input_col, guide_col = st.columns([1.6, 1], gap="large")
with input_col:
    with st.container(border=True):
        if modo == "Geográficas → UTM":
            st.markdown('<div class="card-title">Coordenadas geográficas</div>', unsafe_allow_html=True)
            formato = st.radio("Formato de entrada", ["Decimal", "Grados · minutos · segundos"], horizontal=True, key="format_meridiana")
            if formato == "Decimal":
                a, b = st.columns(2)
                lat = a.number_input("Latitud (°)", min_value=-90.0, max_value=90.0, value=19.0, format="%.10f")
                lon = b.number_input("Longitud (°)", min_value=-180.0, max_value=180.0, value=-98.0, format="%.10f")
            else:
                a, b = st.columns(2)
                with a:
                    st.markdown("**Latitud**")
                    lat_g = st.number_input("Grados latitud", 0, 90, 19, key="mlatg")
                    lat_m = st.number_input("Minutos latitud", 0, 59, 0, key="mlatm")
                    lat_s = st.number_input("Segundos latitud", 0.0, 59.999999, 0.0, key="mlats")
                    lat_h = st.selectbox("Hemisferio latitud", ["N", "S"], key="mlath")
                with b:
                    st.markdown("**Longitud**")
                    lon_g = st.number_input("Grados longitud", 0, 180, 98, key="mlong")
                    lon_m = st.number_input("Minutos longitud", 0, 59, 0, key="mlonm")
                    lon_s = st.number_input("Segundos longitud", 0.0, 59.999999, 0.0, key="mlons")
                    lon_h = st.selectbox("Hemisferio longitud", ["W", "E"], key="mlonh")
                lat = gms_a_decimal(lat_g, lat_m, lat_s, lat_h)
                lon = gms_a_decimal(lon_g, lon_m, lon_s, lon_h)
            manual_zone = st.toggle("Fijar huso UTM manualmente", value=False)
            zona = st.number_input("Zona UTM seleccionada", min_value=1, max_value=60, value=14, disabled=not manual_zone) if manual_zone else None
            st.caption("Por defecto, MERIDIANA determina el huso a partir de la longitud.")
            if st.button("Calcular coordenadas UTM", use_container_width=True, type="primary"):
                try:
                    res = geograficas_a_utm(lat, lon, elipsoide, zona=zona)
                    st.session_state["meridiana_res"] = res
                    st.session_state["meridiana_mode"] = modo
                    st.session_state["meridiana_ellipsoid"] = elipsoide
                except Exception as ex:
                    st.error(f"No se pudo calcular: {ex}")
        else:
            st.markdown('<div class="card-title">Coordenadas UTM</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            este = c1.number_input("Este (X) · metros", value=605254.1318, format="%.4f")
            norte = c2.number_input("Norte (Y) · metros", value=2101126.5127, format="%.4f")
            c3, c4 = st.columns(2)
            zona = c3.number_input("Zona UTM", 1, 60, 14)
            hemisferio = c4.selectbox("Hemisferio", ["N", "S"])
            st.caption("Indica el huso y hemisferio que corresponden a las coordenadas UTM.")
            if st.button("Calcular coordenadas geográficas", use_container_width=True, type="primary"):
                try:
                    res = utm_a_geograficas(este, norte, int(zona), hemisferio, elipsoide)
                    st.session_state["meridiana_res"] = res
                    st.session_state["meridiana_mode"] = modo
                    st.session_state["meridiana_ellipsoid"] = elipsoide
                except Exception as ex:
                    st.error(f"No se pudo calcular: {ex}")
with guide_col:
    st.markdown('<div class="card-title">Referencia de la operación</div>', unsafe_allow_html=True)
    if modo == "Geográficas → UTM":
        st.markdown('<div class="note"><b>Entrada</b><br>Latitud y longitud sobre el elipsoide seleccionado.<br><br><b>Salida</b><br>Este, Norte, zona UTM y parámetros de proyección.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="note"><b>Entrada</b><br>Este, Norte, zona y hemisferio.<br><br><b>Salida</b><br>Latitud y longitud en grados decimales y GMS.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Parámetros de proyección**")
    st.write("• Sistema UTM")
    st.write("• 60 zonas de 6°")
    st.write("• Meridiano central")
    st.write("• Factor de escala puntual")
    st.write("• Convergencia de meridianos")

# Resultados con presentación de registro cartográfico
if "meridiana_res" in st.session_state and st.session_state.get("meridiana_mode") == modo:
    res = st.session_state["meridiana_res"]
    st.markdown('<div class="section-head">04 · Resultados</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-banner"><small>TRANSFORMACIÓN COMPLETADA · {st.session_state.get("meridiana_ellipsoid", elipsoide)}</small><br><b>Ficha de registro cartográfico</b></div>', unsafe_allow_html=True)

    if modo == "Geográficas → UTM":
        rows = [
            ("E", "Este (X)", f"{res['este']:,.4f} m"),
            ("N", "Norte (Y)", f"{res['norte']:,.4f} m"),
            ("⌗", "Zona UTM", str(res["zona"])),
            ("◎", "Hemisferio", str(res["hemisferio"])),
            ("↔", "Meridiano central", f"{res['meridiano_central']}°"),
            ("k", "Factor de escala", f"{res['k_utm']:.10f}"),
            ("∠", "Convergencia de meridianos", str(res["convergencia_gms"])),
        ]
    else:
        rows = [
            ("φ", "Latitud decimal", f"{res['latitud_decimal']:.10f}°"),
            ("λ", "Longitud decimal", f"{res['longitud_decimal']:.10f}°"),
            (("φ"), "Latitud GMS", str(res["latitud_gms"])),
            ("λ", "Longitud GMS", str(res["longitud_gms"])),
            ("⌗", "Zona UTM", str(res["zona"])),
            ("◎", "Hemisferio", str(res["hemisferio"])),
            ("↔", "Meridiano central", f"{res['meridiano_central']}°"),
            ("k", "Factor de escala", f"{res['k_utm']:.10f}"),
            ("∠", "Convergencia de meridianos", str(res["convergencia_gms"])),
        ]
    html = '<div class="result-list">'
    for symbol, label, value in rows:
        html += f'<div class="result-row"><div class="result-symbol">{symbol}</div><div class="result-label">{label}</div><div class="result-value">{value}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<div class="atlas-note">MERIDIANA · Registro de transformación · Cartografía 2</div>', unsafe_allow_html=True)
    with st.expander("Consultar salida numérica completa"):
        st.json(res)

