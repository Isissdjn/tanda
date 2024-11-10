import os
import sqlite3pip freeze

from flask import Flask, render_template, request, jsonify, send_from_directory, g
import speech_recognition as sr
import threading

app = Flask(__name__)

# Chemin du dossier contenant les vidéos
VIDEO_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Lsf')

# Chemin de la base de données
DATABASE = 'emails.db'

# Initialisation du moteur de reconnaissance vocale
recognizer = sr.Recognizer()

# Variable pour savoir si l'enregistrement est en cours
is_recording = False
audio_data = []  # Stocker les segments d'audio collectés

# Fonction pour obtenir la connexion à la base de données
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Ferme la connexion à la base de données à la fin du contexte de l'application
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialiser la table des emails dans la base de données
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        db.commit()

init_db()  # Initialiser la base de données au démarrage de l'application

def normalize_text_with_accents(text):
    """Nettoie et normalise le texte pour comparaison (conserve les accents, met en minuscule et retire les espaces superflus)"""
    text = text.lower().strip()
    return text

def get_video_titles():
    """Retourne la liste des titres des vidéos dans le dossier sans extension"""
    video_titles = []
    for file in os.listdir(VIDEO_FOLDER):
        if file.endswith('.webm'):
            video_titles.append(os.path.splitext(file)[0])  # Retirer l'extension
    return video_titles

def generate_ngrams(words, n):
    """Génère des n-grams (groupes de mots) à partir d'une liste de mots"""
    return [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]

def check_words_in_videos(phrase):
    """Vérifie si des groupes de mots dans la phrase correspondent aux titres des vidéos"""
    video_titles = get_video_titles()
    matched_videos = []

    normalized_titles = [normalize_text_with_accents(title) for title in video_titles]
    words = normalize_text_with_accents(phrase).split()

    for n in range(1, len(words) + 1):
        ngrams = generate_ngrams(words, n)
        for ngram in ngrams:
            if ngram in normalized_titles:
                matched_videos.append(ngram)

    return matched_videos

def play_video(video_name):
    video_name_with_extension = video_name + '.webm'
    video_path = os.path.join(VIDEO_FOLDER, video_name_with_extension)

    if not os.path.exists(video_path):
        return f"La vidéo {video_name_with_extension} n'existe pas"

    return f'/videos/{video_name_with_extension}'

def record_audio():
    global is_recording, audio_data
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Enregistrement commencé...")
        while is_recording:
            try:
                audio_segment = recognizer.listen(source, phrase_time_limit=10)
                audio_data.append(audio_segment)
            except Exception as e:
                print(f"Erreur pendant l'enregistrement: {str(e)}")
        print("Enregistrement arrêté.")
        process_audio()

def process_audio():
    global audio_data
    if not audio_data:
        return []
    try:
        combined_audio = sr.AudioData(b''.join([segment.get_raw_data() for segment in audio_data]),
                                      audio_data[0].sample_rate, audio_data[0].sample_width)
        print("Reconnaissance en cours...")
        text = recognizer.recognize_google(combined_audio, language="fr-FR")
        matched_videos = check_words_in_videos(text)
        return matched_videos
    except sr.UnknownValueError:
        return []
    except sr.RequestError:
        return []

@app.route('/')
def index():
    return render_template('first.html')

@app.route('/translate')
def translate():
    return render_template('translate.html')

@app.route('/connect')
def connect():
    return render_template('connect.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/start_recording', methods=['POST'])
def start_recording_route():
    global is_recording
    is_recording = True
    threading.Thread(target=record_audio).start()
    return jsonify({"status": "Enregistrement commencé."})

@app.route('/stop_recording', methods=['POST'])
def stop_recording_route():
    global is_recording
    is_recording = False
    videos = process_audio()
    return jsonify({"status": "Enregistrement arrêté.", "videos": videos})

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

@app.route('/play_video', methods=['POST'])
def play_video_route():
    video_name = request.json['video_name']
    video_path = play_video(video_name)
    return jsonify({"video_path": video_path})

@app.route('/submit_email', methods=['POST'])
def submit_email():
    email = request.form['email']
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO emails (email) VALUES (?)', (email,))
        db.commit()
        return jsonify({"status": "Email enregistré avec succès."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "Cet email est déjà enregistré."})

@app.route('/submit_text', methods=['POST'])
def submit_text():
    text = request.form['text']
    matched_videos = check_words_in_videos(text)
    return jsonify({"videos": matched_videos})

if __name__ == '__main__':
    app.run(debug=True)

