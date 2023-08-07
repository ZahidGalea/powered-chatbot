from datetime import datetime

import pytz
import requests
import streamlit as st
from components.faq import faq
from components.utils import keep_file_from_path


def utc_str_to_chile_str(utc_datetime_string):
    utc_datetime = datetime.strptime(utc_datetime_string, "%Y-%m-%d %H:%M:%S")

    # Hazlo consciente de la zona horaria UTC
    utc_datetime = pytz.utc.localize(utc_datetime)

    # Define la zona horaria de Chile
    chile_tz = pytz.timezone("Chile/Continental")

    # Conviértelo a la zona horaria de Chile
    chile_datetime = utc_datetime.astimezone(chile_tz)

    # Conviértelo a cadena
    chile_datetime_string = chile_datetime.strftime("%Y-%m-%d %H:%M:%S")

    return chile_datetime_string


def get_files_loaded(host, port):
    response = requests.get(f"http://{host}:{port}/files_loaded")
    if response.status_code == 200:
        return response.json()["files_loaded"]
    else:
        st.error("No se pudo obtener los datos desde el servidor")


def sidebar(acidlabs_image, host, port):
    with st.sidebar:
        st.image(image=acidlabs_image)
        st.markdown("---")
        st.markdown("# About")
        st.markdown("🤖 DataverseGPT allows you to ask questions about our team")
        st.markdown(
            """
			This tool is in work in progress.
			If you want to contact us with more information or any feedback, look for us in Slack
			@Naoto / @Zahid Galea
			"""
        )

        st.markdown("---")
        faq()

        st.markdown("---")
