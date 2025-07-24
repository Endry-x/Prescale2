import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# -----------------------------------------------------------
st.set_page_config(page_title="Mappa completa colore Rosso", layout="wide")
st.title("Mappa dell’intensità del canale **Rosso** su TUTTI i pixel")

# ---------- Upload immagine ---------------------------------
uploaded = st.file_uploader("Carica un'immagine", ["png", "jpg", "jpeg"])
if uploaded is None:
    st.info("Carica un’immagine per iniziare.")
    st.stop()

img = Image.open(uploaded).convert("RGB")
arr = np.asarray(img)
h, w, _ = arr.shape
st.write(f"Dimensioni immagine: **{w} × {h} px**")

# ---------- Estrazione canale R -----------------------------
red = arr[:, :, 0]                      # matrice (h, w) uint8

# ---------- Coordinate con origine in basso -----------------
ys, xs = np.indices((h, w))
ys_bottom = (h - 1) - ys               # y = 0 in basso

# ---------- DataFrame & download ----------------------------
df = pd.DataFrame({
    "x": xs.flatten(),
    "y": ys_bottom.flatten(),
    "R": red.flatten()
})
st.dataframe(df.head(10_000), use_container_width=True)

csv = df.to_csv(index=False).encode()
st.download_button("📥 Scarica CSV completo", csv,
                   file_name="intensita_rosso_completa.csv",
                   mime="text/csv")

# ---------- Heat-map 2-D ------------------------------------
st.subheader("Heat-map intensità rosso")
fig, ax = plt.subplots()
im = ax.imshow(red[::-1], cmap="Reds", extent=[0, w, 0, h],
               origin="lower", aspect='auto')
ax.set_xlabel("x [px]")
ax.set_ylabel("y [px] (origine in basso)")
fig.colorbar(im, ax=ax, label="Valore R (0-255)")
st.pyplot(fig)

