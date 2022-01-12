import streamlit as st
from model import generate_song
import random


giphs_list = [
    "https://media.giphy.com/media/l3q2N0PSZcpi2OBAA/giphy.gif",
    "https://media.giphy.com/media/3kHupjDzMt4oE/giphy.gif",
    "https://media.giphy.com/media/OQsCVVd3o35K0/giphy.gif",
    "https://media.giphy.com/media/dASc6rD8EOXEQ/giphy.gif",
    "https://media.giphy.com/media/ZZKzWoezbKNkG7X8Pz/giphy.gif",
    "https://media.giphy.com/media/fuE6c10kmibDixILeC/giphy.gif",
    "https://media.giphy.com/media/xxPcjpZQq3axi/giphy.gif",
    "https://media.giphy.com/media/rn0Ir1Vm5ulSU/giphy.gif",
    "https://media.giphy.com/media/enO93p3ZGu3ni/giphy.gif",
    "https://media.giphy.com/media/EbLuFZeMoOz28/giphy.gif",
    "https://media.giphy.com/media/vXepo8LDD0mDqXniD2/giphy.gif",
    "https://media.giphy.com/media/l09Qq4IsMgn6anwR8a/giphy.gif",
    "https://media.giphy.com/media/Xw6yFn7frR3Y4/giphy.gif",
    "https://media.giphy.com/media/1t7qraEBCxfcA/giphy.gif",
    "https://media.giphy.com/media/IOu5W1hJwOG3e/giphy.gif"
]


def generate_and_display_song():
    print("I clicked", verses, chorus_lines)
    song = generate_song(verses=verses, chorus_lines=chorus_lines)
    print(song)
    return song


st.title("Lil' Biebs")

st.write("Generate new Justin Bieber's song")
verses = st.number_input("How many verses should the song have?", min_value=2, max_value=5)
chorus_lines = st.number_input("How many lines should the chorus have?", min_value=1, max_value=8)

if st.button("Generate"):
    song = generate_and_display_song()
    st.markdown(f"![Alt Text]({giphs_list[random.randint(0, len(giphs_list))]})")
    st.title(song.split("\n")[0])
    st.text(song)







