from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import tempfile
import yt_dlp
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Usar diretório temporário do sistema em vez de pasta local
TEMP_DIR = tempfile.gettempdir()
MAX_FILE_AGE = 3600  # 1 hora em segundos

def cleanup_old_files():
    """Remove arquivos temporários antigos"""
    try:
        current_time = time.time()
        for filename in os.listdir(TEMP_DIR):
            if filename.startswith('youtube_'):
                filepath = os.path.join(TEMP_DIR, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getctime(filepath)
                    if file_age > MAX_FILE_AGE:
                        os.remove(filepath)
    except Exception as e:
        print(f"Erro na limpeza de arquivos: {e}")

def validate_youtube_url(url):
    """Valida se a URL é do YouTube"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)

def download_audio(video_url):
    """Download apenas do áudio em MP3"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(TEMP_DIR, 'youtube_%(title)s_%(id)s.%(ext)s'),
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'restrictfilenames': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrair informações do vídeo
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'audio')
            video_id = info.get('id', 'unknown')
            
            # Fazer download
            ydl.download([video_url])
            
            # Encontrar o arquivo baixado
            for filename in os.listdir(TEMP_DIR):
                if filename.startswith('youtube_') and filename.endswith('.mp3') and video_id in filename:
                    filepath = os.path.join(TEMP_DIR, filename)
                    return filepath, f'{title}.mp3'
        
        return None, None
    except Exception as e:
        print(f"Erro no download de áudio: {e}")
        return None, None

def download_video(video_url):
    """Download do vídeo em Full HD (MP4)"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(TEMP_DIR, 'youtube_%(title)s_%(id)s.%(ext)s'),
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            'merge_output_format': 'mp4',
            'restrictfilenames': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrair informações do vídeo
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'video')
            video_id = info.get('id', 'unknown')
            
            # Fazer download
            ydl.download([video_url])
            
            # Encontrar o arquivo baixado
            for filename in os.listdir(TEMP_DIR):
                if filename.startswith('youtube_') and filename.endswith('.mp4') and video_id in filename:
                    filepath = os.path.join(TEMP_DIR, filename)
                    return filepath, f'{title}.mp4'
        
        return None, None
    except Exception as e:
        print(f"Erro no download de vídeo: {e}")
        return None, None

def download_transcript(video_url):
    """Download da transcrição do vídeo"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(TEMP_DIR, 'youtube_%(title)s_%(id)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['pt', 'pt-BR', 'en'],
            'skip_download': True,
            'subtitlesformat': 'vtt',
            'restrictfilenames': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrair informações do vídeo
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'transcript')
            video_id = info.get('id', 'unknown')
            
            # Verificar se há legendas disponíveis
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            if not subtitles and not automatic_captions:
                return None, None
            
            # Fazer download das legendas
            ydl.download([video_url])
            
            # Procurar pelo arquivo de legenda baixado
            subtitle_file = None
            for filename in os.listdir(TEMP_DIR):
                if (filename.startswith('youtube_') and 
                    video_id in filename and 
                    filename.endswith(('.vtt', '.srt'))):
                    subtitle_file = os.path.join(TEMP_DIR, filename)
                    break
            
            if subtitle_file and os.path.exists(subtitle_file):
                # Converter VTT para texto simples
                txt_file = subtitle_file.replace('.vtt', '.txt').replace('.srt', '.txt')
                convert_subtitle_to_txt(subtitle_file, txt_file)
                
                if os.path.exists(txt_file):
                    return txt_file, f'{title}_transcript.txt'
        
        return None, None
    except Exception as e:
        print(f"Erro no download de transcrição: {e}")
        return None, None

def convert_subtitle_to_txt(subtitle_file, output_file):
    """Converte arquivo de legenda para texto simples"""
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover timestamps e formatação VTT/SRT
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Pular linhas vazias, timestamps e tags
            if (line and 
                not line.startswith('WEBVTT') and
                not line.startswith('NOTE') and
                not '-->' in line and
                not line.isdigit() and
                not line.startswith('<')):
                text_lines.append(line)
        
        # Salvar texto limpo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_lines))
            
    except Exception as e:
        print(f"Erro ao converter legenda: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    try:
        video_url = request.form.get("url", "").strip()
        download_type = request.form.get("download_type")
        
        if not video_url:
            flash('Por favor, insira uma URL válida.', 'error')
            return redirect(url_for('index'))
        
        if not validate_youtube_url(video_url):
            flash('Por favor, insira uma URL válida do YouTube.', 'error')
            return redirect(url_for('index'))
        
        if download_type not in ['audio', 'video', 'transcript']:
            flash('Tipo de download inválido.', 'error')
            return redirect(url_for('index'))
        
        # Limpar arquivos antigos antes de processar
        cleanup_old_files()
        
        filepath = None
        filename = None
        
        if download_type == "audio":
            filepath, filename = download_audio(video_url)
            mimetype = 'audio/mpeg'
        elif download_type == "video":
            filepath, filename = download_video(video_url)
            mimetype = 'video/mp4'
        elif download_type == "transcript":
            filepath, filename = download_transcript(video_url)
            mimetype = 'text/plain'
            if not filepath:
                flash('Este vídeo não possui transcrição/legendas disponíveis.', 'error')
                return redirect(url_for('index'))
        
        if filepath and os.path.exists(filepath) and filename:
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype=mimetype
            )
        else:
            flash('Erro: Não foi possível processar o download. Tente novamente.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Erro durante o download: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    flash('Ocorreu um erro interno. Tente novamente.', 'error')
    return render_template('index.html'), 500

if __name__ == "__main__":
    # Para desenvolvimento local - o Render usa o gunicorn
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)