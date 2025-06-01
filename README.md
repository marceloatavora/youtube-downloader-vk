# YouTube Downloader

Uma aplicação web simples para baixar vídeos, áudios e transcrições do YouTube, desenvolvida com Flask e yt-dlp.

## Funcionalidades

- 🎵 **Download de Áudio**: Extrai e converte para MP3 com qualidade 192kbps
- 🎥 **Download de Vídeo**: Baixa em Full HD (1080p) no formato MP4
- 📝 **Download de Transcrição**: Extrai legendas automáticas ou manuais em formato de texto

## Estrutura do Projeto

```
youtube-downloader/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── render.yaml           # Configuração do Render
├── .gitignore           # Arquivos ignorados pelo Git
├── README.md            # Esta documentação
└── templates/
    └── index.html       # Template HTML da interface
```

## Instalação Local

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd youtube-downloader
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

5. Acesse `http://localhost:5000` no seu navegador.

## Deploy no Render

### Opção 1: Deploy Automático (Recomendado)

1. Faça push do código para um repositório GitHub
2. Conecte sua conta do Render ao GitHub
3. Crie um novo Web Service no Render
4. Selecione seu repositório
5. Use as configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Environment**: Python 3

### Opção 2: Deploy Manual

1. Crie um arquivo `render.yaml` (já incluído)
2. Use os comandos de build e start especificados no arquivo

### Configurações do Render

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Environment**: Python 3
- **Plan**: Free (suficiente para uso básico)

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **yt-dlp**: Biblioteca para download de vídeos do YouTube
- **Gunicorn**: Servidor WSGI para produção
- **HTML/CSS/JavaScript**: Interface do usuário

## Recursos Implementados

### Funcionalidades Principais
- Interface web responsiva e moderna
- Validação de URLs do YouTube
- Download de áudio em MP3 (192kbps)
- Download de vídeo em Full HD (MP4)
- Extração de transcrições/legendas
- Limpeza automática de arquivos temporários

### Segurança e Performance
- Validação de entrada de URLs
- Tratamento de erros robusto
- Limpeza automática de arquivos temporários
- Configuração para produção com Gunicorn

### Interface de Usuário
- Design moderno e responsivo
- Feedback visual durante o processamento
- Mensagens de erro e sucesso
- Compatível com dispositivos móveis

## Limitações

- **Render Free Tier**: 512MB RAM, 0.1 CPU cores
- **Tempo de processamento**: Vídeos grandes podem demorar mais
- **Armazenamento temporário**: Arquivos são limpos automaticamente após 1 hora
- **Uso responsável**: Respeite os direitos autorais do conteúdo baixado

## Troubleshooting

### Problemas Comuns

1. **Erro de timeout**: Vídeos muito longos podem exceder o limite de tempo
2. **Erro de memória**: Vídeos de alta qualidade podem usar muita RAM
3. **URL inválida**: Verifique se a URL é do YouTube e está correta

### Logs de Debug

Para ver logs detalhados no Render:
1. Acesse o dashboard do Render
2. Vá para seu serviço
3. Clique na aba "Logs"

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto é de código aberto. Use com responsabilidade e respeite os direitos autorais.

## Aviso Legal

⚠️ **Importante**: Este software é apenas para uso educacional e pessoal. Certifique-se de ter permissão para baixar o conteúdo e respeite os termos de serviço do YouTube e direitos autorais dos criadores de conteúdo.