# 🎵 Delphi

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

Um aplicativo desktop moderno e modular para baixar músicas do YouTube em alta qualidade, gerenciar playlists e reproduzir áudio com suporte a atalhos globais e capas de álbuns. Desenvolvido com Python e CustomTkinter.

## ✨ Funcionalidades

- **📥 Download de Áudio:** Baixa músicas do YouTube diretamente no formato `.mka` com metadados e capa (thumbnail) embutidos.
- **🎧 Player Integrado:** Reprodução fluida usando a engine do VLC (Play, Pause, Seek, Volume).
- **📂 Gerenciador de Biblioteca:**
  - Criação e gestão de Playlists personalizadas.
  - Modos de reprodução: Sequencial e Aleatório (Shuffle).
  - Cache de imagens para performance otimizada na rolagem da lista.
- **⌨️ Atalhos Globais (Hotkeys):**
  - Controle o player mesmo com a janela minimizada ou em segundo plano.
  - Suporte para teclas multimídia, combinações de teclado (ex: `Ctrl+Alt+P`) e **botões laterais do mouse**.
  - Sistema de detecção automática de teclas na configuração.
- **🎨 Interface Moderna:** GUI escura baseada em `CustomTkinter` com suporte a barra de progresso de download.

## 🛠️ Tecnologias Utilizadas

O projeto segue uma arquitetura modular (MVC simplificado):

- **Interface:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Engine de Áudio:** [python-vlc](https://github.com/oaubert/python-vlc) (LibVLC)
- **Downloads:** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Manipulação de Metadados/Imagem:** `mutagen`, `Pillow`, `ffmpeg`
- **Inputs Globais:** `keyboard`, `mouse`

## ⚙️ Pré-requisitos

Para rodar este projeto, você precisará ter instalado no seu sistema:

1.  **Python 3.10+**
2.  **FFmpeg:** Essencial para o download e conversão de áudio. Deve estar adicionado ao PATH do sistema.
3.  **VLC Media Player:** O software precisa das DLLs do VLC instaladas no computador para reproduzir áudio.

## 🚀 Como Rodar

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Sukeru14/Delphi.git](https://github.com/Sukeru14/Delphi.git)
    cd Delphi
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação:**
    ```bash
    python main.py
    ```

## 📦 Como Compilar (.exe)

Para gerar um executável independente para Windows, utilize o **PyInstaller**. 

Certifique-se de que o arquivo `ffmpeg.exe` e `ffprobe.exe` estejam acessíveis.

Execute o comando na raiz do projeto:

```bash
pyinstaller --noconsole --onedir --name="Delphi" main.py
```

Após compilar, copie os executáveis do FFmpeg para dentro da pasta dist/Delphi/ gerada.