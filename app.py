import os
import uuid
import subprocess
from flask import Flask, render_template, request, send_file
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"

def baixar_audio(url):
    nome = f"audio_{uuid.uuid4().hex[:8]}.mp3"
    path = os.path.join(DOWNLOAD_DIR, nome)
    comando = ["yt-dlp", "-x", "--audio-format", "mp3", "-o", path, url]
    subprocess.run(comando)
    return path

def baixar_video(url, full_hd=False):
    nome = f"video_{uuid.uuid4().hex[:8]}.mp4"
    path = os.path.join(DOWNLOAD_DIR, nome)
    formato = "bv*[height<=1080]+ba" if full_hd else "bestvideo+bestaudio"
    comando = ["yt-dlp", "-f", formato, "--merge-output-format", "mp4", "-o", path, url]
    subprocess.run(comando)
    return path

def baixar_transcricao(url):
    video_id = url.split("v=")[-1][:11]
    nome = f"transcricao_{uuid.uuid4().hex[:8]}.txt"
    path = os.path.join(DOWNLOAD_DIR, nome)
    try:
        transcricao = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        with open(path, "w", encoding="utf-8") as f:
            for item in transcricao:
                f.write(f"{item['text']}
")
        return path
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        acao = request.form["action"]

        if acao == "mp3":
            path = baixar_audio(url)
            return send_file(path, as_attachment=True)

        elif acao == "hd":
            path = baixar_video(url, full_hd=True)
            return send_file(path, as_attachment=True)

        elif acao == "max":
            path = baixar_video(url, full_hd=False)
            return send_file(path, as_attachment=True)

        elif acao == "transcript":
            path = baixar_transcricao(url)
            if path:
                return send_file(path, as_attachment=True)
            else:
                return "❌ Este vídeo não possui transcrição disponível."

    return render_template("index.html")

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    app.run(debug=True)