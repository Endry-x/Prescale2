import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

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

# ---------- Soglia filtro -------------------------------------------
threshold = st.slider("Soglia minima R da visualizzare", 0, 255, 0)
st.write(f"Mostro solo i pixel con **R ≥ {threshold}** nei grafici.")

# ---------- Estrazione canale R -------------------------------------
red = arr[:, :, 0]

# ---------- Coordinate (origine basso-sinistra) ---------------------
ys, xs = np.indices((h, w))
ys_bottom = (h - 1) - ys

# ---------- DataFrame & download (completo) -------------------------
df = pd.DataFrame({
    "x": xs.flatten(),
    "y": ys_bottom.flatten(),
    "R": red.flatten()
})
st.dataframe(df.head(10_000), use_container_width=True)
csv = df.to_csv(index=False).encode()
st.download_button("📥 Scarica CSV completo",
                   csv, "intensita_rosso_completa.csv", "text/csv")

# ---------- Heat-map 2-D filtrata -----------------------------------
red_masked = red.astype(float)
red_masked[red_masked < threshold] = np.nan   # valori sotto soglia -> NaN -> bianchi

cmap = plt.cm.gray.copy()
cmap.set_bad(color="white")                   # pixel NaN bianchi

fig2d, ax2d = plt.subplots()
im = ax2d.imshow(
    red_masked[::-1],
    cmap=cmap, vmin=threshold, vmax=255,
    extent=[0, w, 0, h], origin="lower", aspect="auto"
)
ax2d.set_xlabel("x [px]")
ax2d.set_ylabel("y [px] (origine in basso)")
fig2d.colorbar(im, ax=ax2d, label="Valore R (≥ soglia)")

# ---------- Layout affiancato --------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.image(img, caption="Immagine originale", use_column_width=True)
with col2:
    st.pyplot(fig2d)

# ---------- Grafico 3-D filtrato -----------------------------------
with st.expander("Mostra grafico 3-D (x, y, R)"):
    df_filtered = df[df["R"] >= threshold]
    max_points = 20_000
    if len(df_filtered) == 0:
        st.warning("Nessun pixel supera la soglia selezionata.")
    else:
        if len(df_filtered) > max_points:
            df_sample = df_filtered.sample(max_points, random_state=0)
            st.write(f"Tracciati {max_points} punti su {len(df_filtered)} "
                     f"(campionamento casuale).")
        else:
            df_sample = df_filtered

        fig3d = plt.figure(figsize=(6, 6))
        ax3d = fig3d.add_subplot(111, projection='3d')
        ax3d.scatter(
            df_sample["x"], df_sample["y"], df_sample["R"],
            c=df_sample["R"], cmap="Reds", s=4
        )
        ax3d.set_xlabel("x [px]")
        ax3d.set_ylabel("y [px] (origine in basso)")
        ax3d.set_zlabel("Valore R")
        ax3d.set_title(f"Intensità rosso ≥ {threshold}")
        st.pyplot(fig3d)
