from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os

choix = input("Entrez un chiffre : ")

if choix == '1':
    tts = gTTS(text="Bonjour", lang='fr')
    tts.save("bonjour.mp3")
    song = AudioSegment.from_mp3("bonjour.mp3")
    play(song)  # Utilisation de pydub pour jouer le son
    os.remove("bonjour.mp3")

elif choix == '2':
    tts = gTTS(text="ça va ?", lang='fr')
    tts.save("ça_va.mp3")
    song = AudioSegment.from_mp3("ça_va.mp3")
    play(song)  # Utilisation de pydub pour jouer le son
    os.remove("ça_va.mp3")

elif choix == '3':
    tts = gTTS(text="je", lang='fr')
    tts.save("je.mp3")
    song = AudioSegment.from_mp3("je.mp3")
    play(song)  # Utilisation de pydub pour jouer le son
    os.remove("je.mp3")

elif choix == '4':
    tts = gTTS(text="appelle", lang='fr')
    tts.save("appelle.mp3")
    song = AudioSegment.from_mp3("appelle.mp3")
    play(song)  # Utilisation de pydub pour jouer le son
    os.remove("appelle.mp3")

elif choix == '5':
    tts = gTTS(text="Isis", lang='fr')
    tts.save("Isis.mp3")
    song = AudioSegment.from_mp3("Isis.mp3")
    play(song)  # Utilisation de pydub pour jouer le son
    os.remove("Isis.mp3")

else:
    print("Aucun son à jouer pour ce chiffre.")
