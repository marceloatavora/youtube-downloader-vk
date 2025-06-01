from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import tempfile
import yt_dlp
import time
import traceback

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Usar diretório temporário do sistema
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

def get_ydl_opts_base():
    """Configurações base do yt-dlp otimizadas para Render"""
    return {
        'outtmpl': os.path.join(TEMP_DIR, 'youtube_%(title)s_%(id)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': False,  # Mudado para False para debug
        'no_warnings': False,
        'extractaudio': False,
        'writeinfojson': False,
        'writethumbnail': False,
        'writesubtitles': False,
        # Configurações específicas para contornar problemas do Render
        'cookiefile': None,
        'no_check_certificate': True,
        'prefer_insecure': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        # Headers adicionais para evitar bloqueios
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
        }
    }

def download_audio(video_url):
    """Download apenas do áudio em MP3"""
    try:
        ydl_opts = get_ydl_opts_base()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extrair informações do vídeo primeiro
                print(f"Extraindo informações de: {video_url}")
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'audio')
                video_id = info.get('id', 'unknown')
                
                print(f"Título: {title}, ID: {video_id}")
                
                # Fazer download
                print("Iniciando download...")
                ydl.download([video_url])
                
                # Encontrar o arquivo baixado
                print("Procurando arquivo baixado...")
                for filename in os.listdir(TEMP_DIR):
                    if filename.startswith('youtube_') and filename.endswith('.mp3') and video_id in filename:
                        filepath = os.path.join(TEMP_DIR, filename)
                        print(f"Arquivo encontrado: {filepath}")
                        return filepath, f'{title}.mp3'
                
                print("Arquivo não encontrado após download")
                return None, None
                
            except yt_dlp.utils.DownloadError as e:
                print(f"Erro específico do yt-dlp: {e}")
                # Tentar com configurações mais permissivas
                if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                    return None, "bot_detection"
                return None, None
                
    except Exception as e:
        print(f"Erro geral no download de áudio: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

def download_video(video_url):
    """Download do vídeo em qualidade menor para economizar recursos"""
    try:
        ydl_opts = get_ydl_opts_base()
        ydl_opts.update({
            # Formato mais compatível e menor
            'format': 'best[height<=720]/best[height<=480]/best',
            'merge_output_format': 'mp4',
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Extraindo informações de: {video_url}")
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'video')
                video_id = info.get('id', 'unknown')
                
                print(f"Título: {title}, ID: {video_id}")
                
                print("Iniciando download...")
                ydl.download([video_url])
                
                print("Procurando arquivo baixado...")
                for filename in os.listdir(TEMP_DIR):
                    if filename.startswith('youtube_') and filename.endswith('.mp4') and video_id in filename:
                        filepath = os.path.join(TEMP_DIR, filename)
                        print(f"Arquivo encontrado: {filepath}")
                        return filepath, f'{title}.mp4'
                
                print("Arquivo não encontrado após download")
                return None, None
                
            except yt_dlp.utils.DownloadError as e:
                print(f"Erro específico do yt-dlp: {e}")
                if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                    return None, "bot_detection"
                return None, None
                
    except Exception as e:
        print(f"Erro geral no download de vídeo: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None, None

def download_transcript(video_url):
    """Download da transcrição do vídeo"""
    try:
        ydl_opts = get_ydl_opts_base()
        ydl_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['pt', 'pt-BR', 'en'],
            'skip_download': True,
            'subtitlesformat': 'vtt',
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Extraindo informações de: {video_url}")
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'transcript')
                video_id = info.get('id', 'unknown')
                
                # Verificar se há legendas disponíveis
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                if not subtitles and not automatic_captions:
                    print("Nenhuma legenda disponível")
                    return None, "no_subtitles"
                
                print("Fazendo download das legendas...")
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
                
            except yt_dlp.utils.DownloadError as e:
                print(f"Erro específico do yt-dlp: {e}")
                if "Sign in to confirm" in str(e) or "bot" in str(e).lower():
                    return None, "bot_detection"
                return None, None
                
    except Exception as e:
        print(f"Erro geral no download de transcrição: {e}")
        print(f"Traceback: {traceback.format_exc()}")
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
        
        print(f"Recebida solicitação: {download_type} para URL: {video_url}")
        
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
        error_type = None
        
        if download_type == "audio":
            filepath, result = download_audio(video_url)
            filename = result if filepath else None
            error_type = result if not filepath else None
            mimetype = 'audio/mpeg'
        elif download_type == "video":
            filepath, result = download_video(video_url)
            filename = result if filepath else None
            error_type = result if not filepath else None
            mimetype = 'video/mp4'
        elif download_type == "transcript":
            filepath, result = download_transcript(video_url)
            filename = result if filepath else None
            error_type = result if not filepath else None
            mimetype = 'text/plain'
        
        # Tratamento específico de erros
        if error_type == "bot_detection":
            flash('❌ YouTube detectou atividade suspeita. Tente novamente em alguns minutos ou use uma URL diferente.', 'error')
            return redirect(url_for('index'))
        elif error_type == "no_subtitles":
            flash('❌ Este vídeo não possui transcrição/legendas disponíveis.', 'error')
            return redirect(url_for('index'))
        elif not filepath or not os.path.exists(filepath) or not filename:
            flash('❌ Erro: Não foi possível processar o download. Verifique se a URL está correta e tente novamente.', 'error')
            return redirect(url_for('index'))
        
        print(f"Enviando arquivo: {filepath}")
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
            
    except Exception as e:
        print(f"Erro geral no download: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'❌ Erro durante o download: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    flash('❌ Ocorreu um erro interno. Tente novamente.', 'error')
    return render_template('index.html'), 500

if __name__ == "__main__":
    # Para desenvolvimento local - o Render usa o gunicorn
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)