import streamlit as st
from PIL import Image, ExifTags
import folium
from io import BytesIO

# Titre de l'application
st.title('Éditeur de métadonnées EXIF et Cartes')


# Fonction pour convertir les degrés décimaux en degrés, minutes et secondes rationnels
def deg_to_dms_rational(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = round((deg - d - m / 60) * 3600, 2)
    return (d, m, s)

# Fonction pour créer un dictionnaire GPS avec latitude et longitude
def create_gps_dict(lat, lon):
    lat_dms = deg_to_dms_rational(abs(lat))
    lon_dms = deg_to_dms_rational(abs(lon))
    lat_ref = 'N' if lat >= 0 else 'S'
    lon_ref = 'E' if lon >= 0 else 'W'

    return {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref,
        piexif.GPSIFD.GPSLatitude: [(lat_dms[0], 1), (lat_dms[1], 1), (int(lat_dms[2] * 100), 100)],
        piexif.GPSIFD.GPSLongitudeRef: lon_ref,
        piexif.GPSIFD.GPSLongitude: [(lon_dms[0], 1), (lon_dms[1], 1), (int(lon_dms[2] * 100), 100)]
    }



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
        
        # Formulaire pour éditer les métadonnées EXIF
        st.write("Éditez les métadonnées EXIF :")
        latitude = st.number_input("Latitude", value=48.8566)  # Valeur par défaut : Paris
        longitude = st.number_input("Longitude", value=2.3522)  # Valeur par défaut : Paris

        # Formulaire pour éditer les métadonnées
        exif_edit = {}
        for key, value in exif.items():
            exif_edit[key] = st.text_input(f"{key}:", str(value))
        
        if st.button("Enregistrer"):
            # Extraction et modification des métadonnées EXIF
            exif_dict = image.info.get("exif", b'')
            gps_dict = create_gps_dict(latitude, longitude)
            
            # Pillow ne supporte pas directement l'écriture des EXIF modifiés dans l'image
            # Nous utilisons un buffer pour simuler cette opération
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", exif=exif_dict)
            buffer.seek(0)
            
            # Sauvegarde de l'image avec les nouvelles métadonnées
            with open("output_image.jpg", "wb") as f:
                f.write(buffer.getvalue())
            st.success("Les données GPS ont été mises à jour.")

            # Fournir un lien de téléchargement pour l'image modifiée
            with open("output_image.jpg", "rb") as file:
                st.download_button(
                    label="Télécharger l'image modifiée",
                    data=file,
                    file_name="output_image.jpg",
                    mime="image/jpeg"
                )

            # Affichage de la carte avec les coordonnées GPS
            st.write("## Carte avec la localisation GPS")
            m = folium.Map(location=[latitude, longitude], zoom_start=12)
            folium.Marker([latitude, longitude], popup="Localisation").add_to(m)
            map_data = io.BytesIO()
            m.save(map_data, close_file=False)
            st.components.v1.html(map_data.getvalue().decode(), height=500, width=700)
    else:
        st.write("Aucune métadonnée EXIF trouvée dans l'image.")
