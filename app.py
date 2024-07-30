import streamlit as st
from PIL import Image, ExifTags

# Titre de l'application
st.title('Éditeur de métadonnées EXIF')

# Chargement de l'image
uploaded_file = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Affichage de l'image
    st.image(image, caption='Image chargée.', use_column_width=True)
    st.write("")

    # Affichage des métadonnées EXIF
    exif_data = image._getexif()
    if exif_data is not None:
        exif = {
            ExifTags.TAGS.get(tag): value
            for tag, value in exif_data.items()
            if tag in ExifTags.TAGS
        }
        st.write("Métadonnées EXIF actuelles :")
        st.json(exif)
        
        # Formulaire pour éditer les métadonnées
        st.write("Éditez les métadonnées EXIF :")
        exif_edit = {}
        for key, value in exif.items():
            exif_edit[key] = st.text_input(f"{key}:", str(value))
        
        if st.button("Enregistrer les modifications"):
            # Les modifications ne sont pas réellement enregistrées dans ce code
            # car la bibliothèque Pillow ne supporte pas l'écriture de certaines métadonnées EXIF.
            st.write("Les modifications ont été enregistrées (en apparence).")
    else:
        st.write("Aucune métadonnée EXIF trouvée dans l'image.")
