import json
import os
import re

import requests
import streamlit as st
from PIL import Image

from components.sidebar import sidebar
from components.utils import keep_file_from_path

ACIDLABS_IMAGE = Image.open("assets/icons/acidlabs.png")

CHATBOT_HOST = os.environ.get("CHATBOT_HOST", "host.docker.internal")
CHATBOT_PORT = os.environ.get("CHATBOT_PORT", "5001")


def main():
    st.set_page_config(
        page_title="Dataverse Chatbot", page_icon=ACIDLABS_IMAGE, layout="wide"
    )
    st.title(f"Dataverse Chatbot 🤖")

    sidebar(ACIDLABS_IMAGE.resize((100, 100)), host=CHATBOT_HOST, port=CHATBOT_PORT)

    st.header("Chat with us!")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=ACIDLABS_IMAGE):
            message_placeholder = st.empty()

            response = requests.post(
                f"http://{CHATBOT_HOST}:{CHATBOT_PORT}/query",
                data=json.dumps({"text": st.session_state.messages[-1]["content"]}),
                stream=True,
            )

            if response.status_code == 200:
                content = response.content
                decoded_line = content.decode("utf-8")
                j = json.loads(decoded_line)
                response_str = j["response"]
                message_placeholder.markdown(response_str)
                with st.expander("Response origin"):
                    for node in j["nodes"]:
                        st.markdown(f"---")
                        information = re.sub(r"[^\w\s,.]", "", node[1])
                        st.caption(f'File "{keep_file_from_path(node[0])}" \n')
                        st.caption(
                            f"<small> {information} </small>", unsafe_allow_html=True
                        )

                st.session_state.messages.append(
                    {"role": "assistant", "content": response_str}
                )


if __name__ == "__main__":
    main()
