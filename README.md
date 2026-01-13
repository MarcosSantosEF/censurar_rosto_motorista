# 🎥 Censura Automática de Rostos em Vídeo com Identificação

Sistema em **Python** para **censura automática de rostos humanos em vídeos**, utilizando **MediaPipe Face Mesh**, com **pixelização estável**, **rastreamento inteligente**, e **inserção de logo + identificação textual** no canto superior direito do vídeo.

Indicado para **LGPD**, auditorias, transporte, monitoramento, compliance e registros oficiais.

---

## ✨ Funcionalidades

- 🔍 Detecção precisa de múltiplos rostos  
- 🎭 Pixelização estável (sem flicker)  
- 🧠 Rastreamento por IOU + persistência temporal (TTL)  
- 🖼️ Inserção de logo (PNG com transparência)  
- 📝 Identificação automática com nome e CPF  
- ⚡ Exibição de FPS real e tempo estimado (ETA)  
- 🎬 Compatível com vídeos longos e alta resolução  

---

## 🧠 Tecnologias Utilizadas

- Python 3.10+  
- OpenCV  
- MediaPipe  
- NumPy  

---

## ⚙️ Configurações Principais

Edite no início do arquivo `main.py`:

## python
INPUT_VIDEO = "input.mp4"
OUTPUT_VIDEO = "output.mp4"
LOGO_PATH = "logo.png"

NOME_MOTORISTA = "Marcos Martins dos Santos"
CPF_MOTORISTA  = "000.000.000-00"

## 🔧 Parâmetros Técnicos
Parâmetro	Descrição
PIXEL_SIZE	Intensidade da pixelização
EXPAND	Margem extra ao redor do rosto
FACE_TTL	Quantidade de frames que o rosto persiste
IOU_THRESHOLD	Sensibilidade do rastreamento
logo_scale	Tamanho do logo relativo ao vídeo

## 📦 Instalação
Recomendado usar ambiente virtual:

bash
Copiar código
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
Instale as dependências:

bash
Copiar código
pip install opencv-python mediapipe numpy

## ▶️ Como Executar
Coloque o vídeo de entrada como input.mp4

Adicione o arquivo logo.png

Ajuste nome e CPF no código

Execute:

bash
Copiar código
python main.py

## 📊 Acompanhamento em Tempo Real
Durante o processamento, o terminal exibirá:

yaml
Copiar código
Frame 1250/9400 | 32.4 FPS | ETA 03:12
Frames processados

FPS real

Tempo estimado restante

## 🛡️ LGPD e Conformidade
## ✔️ Censura automática de dados biométricos

## ✔️ Identificação do destinatário no vídeo

## ✔️ Adequado para ambientes corporativos e oficiais

## 🧪 Observações Técnicas
Suporta múltiplos rostos simultaneamente

Evita flickering usando IOU + TTL

Logo suporta PNG com canal alpha

Texto quebra automaticamente para não sair da tela
