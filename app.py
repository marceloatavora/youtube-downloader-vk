from flask import Flask, render_template, request, send_file
import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from tempfile import NamedTemporaryFile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_type = request.form['format']

    try:
        ydl_opts = {}

        if format_type == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'audio.%(ext)s'
            }

        elif format_type == 'video':
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': 'video.mp4',
                'merge_output_format': 'mp4'
            }

        elif format_type == 'transcript':
            video_id = url.split("v=")[-1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            file = NamedTemporaryFile(delete=False, mode='w+', suffix=".txt")
            for item in transcript:
                file.write(f"{item['text']}\n")
            file.close()
            return send_file(file.name, as_attachment=True, download_name="transcript.txt")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        filename = 'audio.mp3' if format_type == 'mp3' else 'video.mp4'
        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Erro ao processar o download: {str(e)}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
