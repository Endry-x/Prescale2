import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# ---------- Config pagina -------------------------------------------
st.set_page_config(page_title="Mappa completa Rosso", layout="wide")
st.title("Mappa dell’intensità del canale **Rosso** su tutti i pixel")

# ---------- Upload --------------------------------------------------
uploaded = st.file_uploader("Carica un'immagine", ["png", "jpg", "jpeg"])
if uploaded is None:
    st.info("Carica un’immagine per iniziare.")
    st.stop()

img = Image.open(uploaded).convert("RGB")
arr = np.asarray(img)
h, w, _ = arr.shape
st.write(f"Dimensioni immagine: **{w} × {h} px**")

# ---------- Estrazione canale R -------------------------------------
red = arr[:, :, 0]                 # matrice uint8 (0-255)

# ---------- Coordinate (origine basso-sinistra) ----------------------
ys, xs = np.indices((h, w))
ys_bottom = (h - 1) - ys           # y = 0 in basso

# ---------- DataFrame & CSV -----------------------------------------
df = pd.DataFrame({
    "x": xs.flatten(),
    "y": ys_bottom.flatten(),
    "R": red.flatten()
})
st.dataframe(df.head(10_000), use_container_width=True)

csv = df.to_csv(index=False).encode()
st.download_button("📥 Scarica CSV completo",
                   csv, "intensita_rosso_completa.csv", "text/csv")

# ---------- Heat-map in scala di grigi ------------------------------
fig, ax = plt.subplots()
im = ax.imshow(
    red[::-1],           # flip verticale → origine in basso
    cmap="gray",         # scala di grigi: 0 nero, 255 bianco
    vmin=0, vmax=255,    # range lineare completo
    extent=[0, w, 0, h],
    origin="lower",
    aspect="auto",
)
ax.set_xlabel("x [px]")
ax.set_ylabel("y [px] (origine in basso)")
fig.colorbar(im, ax=ax, label="Valore R (0–255)")

# ---------- Mostra originale + heat-map affiancate ------------------
col1, col2 = st.columns(2)
with col1:
    st.image(img, caption="Immagine originale", use_column_width=True)
with col2:
    st.pyplot(fig)
