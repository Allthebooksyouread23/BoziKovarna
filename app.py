import streamlit as st
import numpy as np
from scipy.optimize import minimize

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Boží Kovárna")

# Styl pro černé pozadí a lepší vzhled (Streamlit má tmavý režim v základu, ale můžeme ho vynutit)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("Boží Kovárna")
st.write("Vyber barvu a zjisti poměr")

# --- LOGIKA VÝPOČTU ---
LIQUIDS = {
    "Modrá": np.array([128, 238, 246]) / 255.0,
    "Zelená": np.array([7, 139, 25]) / 255.0,
    "Griotka": np.array([121, 29, 28]) / 255.0
}

def rgb_to_cmyk(rgb):
    r, g, b = rgb
    k = 1 - max(r, g, b)
    if k == 1: return np.array([0, 0, 0, 1])
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return np.array([c, m, y, k])

def calculate_ratio(target_hex):
    target_rgb = np.array([int(target_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]) / 255.0
    target_cmyk = rgb_to_cmyk(target_rgb)
    liquid_cmyks = [rgb_to_cmyk(val) for val in LIQUIDS.values()]

    def objective(weights):
        mixed_cmyk = sum(w * c for w, c in zip(weights, liquid_cmyks))
        return np.linalg.norm(mixed_cmyk - target_cmyk)

    res = minimize(objective, [0.33, 0.33, 0.33], bounds=[(0, 1)]*3, constraints={'type': 'eq', 'fun': lambda w: np.sum(w)-1})
    return res.x

# --- UI PRVKY ---
target_color = st.color_picker("Zvol cílovou barvu", "#00f900")

if target_color:
    w = calculate_ratio(target_color)
    
    # Výpočet poměru a:b:c
    valid_weights = w[w > 0.01]
    base = min(valid_weights) if len(valid_weights) > 0 else 1
    ratio = [round(val / base, 2) for val in w]

    st.divider()
    st.subheader("Potřebný poměr (a : b : c)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Modrá", f"{ratio[0]}")
    col2.metric("Zelená", f"{ratio[1]}")
    col3.metric("Griotka", f"{ratio[2]}")

    st.info(f"Procentuálně: {w[0]*100:.1f}% Modrá | {w[1]*100:.1f}% Zelená | {w[2]*100:.1f}% Griotka")