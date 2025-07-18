# 🧩 DownloaderGUI

Um downloader de mídias com interface gráfica, desenvolvido em **Python**, que automatiza o uso das poderosas ferramentas de linha de comando `yt-dlp` e `gallery-dl`.  
O programa é totalmente **autossuficiente**, gerenciando (baixando e atualizando) suas próprias dependências para garantir que esteja sempre pronto para uso.

---

## 🚀 Funcionalidades Principais

- **Interface Gráfica Amigável**  
  Chega de terminais! Uma UI limpa e intuitiva para todas as suas necessidades de download.

- **Download em Lote**  
  Cole múltiplas URLs (uma por linha) e baixe tudo de uma só vez.

- **Autossuficiente e Portátil**  
  Não requer instalação prévia de `yt-dlp` ou `gallery-dl`. O programa baixa e atualiza essas ferramentas automaticamente na inicialização.

- **Seleção Avançada de Qualidade**
  - **Vídeo (MP4):** Baixe em resoluções que vão de 480p até 4K, com opções de 60fps.
  - **Áudio (MP3):** Extraia áudio de vídeos com diferentes níveis de qualidade (bitrate).

- **Temas Claro e Escuro**  
  Adapte a aparência do programa à sua preferência.

- **Ajuda Integrada**  
  Uma aba de FAQ responde às perguntas mais comuns diretamente no programa.

- **Construído para Windows**  
  Empacotado como um único executável `.exe` para facilitar a distribuição e o uso.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3  
- **Interface Gráfica:** Tkinter, [ttkbootstrap](https://ttkbootstrap.readthedocs.io)  
- **Dependências Gerenciadas:** `yt-dlp`, `gallery-dl`  
- **Empacotamento:** PyInstaller

---

## 🏁 Como Usar

### ✅ Opção 1: Baixar o Executável (Recomendado)

1. Vá para a seção de **[Releases](https://github.com/greisp-dev/DownloaderGUI/releases)** deste repositório.  
2. Baixe o arquivo `.exe` da **versão mais recente**.  
3. Execute o arquivo.  
   > Na primeira execução, pode demorar um pouco, pois o programa estará baixando as dependências.  
4. Pronto! O programa está pronto para uso.

> ⚠️ **Nota sobre Antivírus:**  
> Alguns antivírus (incluindo o Windows Defender) podem alertar sobre programas criados com PyInstaller. Isso é um **falso positivo**. O programa é seguro se você o baixou diretamente deste repositório.

---

### 💻 Opção 2: Executar a partir do Código-Fonte (Para Desenvolvedores)

Clone o repositório:

```bash
git clone https://github.com/greisp-dev/DownloaderGUI.git
cd DownloaderGUI
````
Instale a dependência principal:
```bash
pip install ttkbootstrap
````
Execute o script:
```bash
python downloader_gui.py
````
---

### ⚠️ Limitações
- 1 O programa não suporta o download de vídeos privados ou com restrição de idade que exigem login.

- 1.1  - Esta funcionalidade foi intencionalmente omitida para manter a simplicidade e a estabilidade.
---

### 🎯 Objetivo do Projeto

Este projeto foi desenvolvido como um exercício prático para aprofundar meus conhecimentos em Python, com foco em:

- Desenvolvimento de interfaces gráficas com Tkinter

- Gerenciamento de processos e threads

- Interação com ferramentas de linha de comando

- Distribuição de aplicações desktop com PyInstaller
---

### 🤝Contribuições
Sugestões, reports de bugs e contribuições são muito bem-vindos!
Sinta-se à vontade para abrir uma issue ou um pull request.
Vamos construir algo incrível juntos!
