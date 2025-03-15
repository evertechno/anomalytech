import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64
import random

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Code to Song - AI Composer")
st.write("Enter your code and let the AI turn it into a song!")

code = st.text_area("Enter your code:", "function hello() { console.log('Hello, World!'); }")

if st.button("Compose Song"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Convert the logic of this code into a song, including lyrics and a description of the melody: {code}"
        response = model.generate_content(prompt)
        song_text = response.text

        st.write("AI Generated Song:")
        st.write(song_text)

        # Extract Lyrics and Melody Description (crude split)
        try:
            lyrics = song_text.split("Lyrics:")[1].split("Melody:")[0].strip()
            melody_description = song_text.split("Melody:")[1].strip()
        except IndexError:
            lyrics = song_text # if parsing fails, use the whole text.
            melody_description = "No melody description was generated."

        st.write("Lyrics:")
        st.write(lyrics)
        st.write("Melody Description:")
        st.write(melody_description)

        # Text-to-Speech using gTTS
        tts = gTTS(lyrics, lang="en")
        tts.save("song.mp3")

        # Display audio player in Streamlit
        with open("song.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio controls autoplay="false">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
