# AWS Lambda - Assistente Virtual com Amazon Nova Sonic

## 👨‍💻 Projeto desenvolvido por: 
[Rafael Torres Nantes](https://github.com/rafael-torres-nantes)

## Índice

* 📚 Contextualização do projeto
* 🛠️ Tecnologias/Ferramentas utilizadas
* 🖥️ Funcionamento do sistema
   * 🧩 Parte 1 - Lambda Handler
   * 🎨 Parte 2 - Serviços e Utilitários
* 🔀 Arquitetura da aplicação
* 📁 Estrutura do projeto
* 📌 Como executar o projeto
* 🕵️ Dificuldades Encontradas

## 📚 Contextualização do projeto

Este projeto implementa um **assistente virtual inteligente** utilizando **AWS Lambda** e **Amazon Nova Sonic** para realizar interações de áudio em tempo real via streaming bidirecional. O sistema foi projetado para capturar áudio do usuário através do microfone, processá-lo utilizando modelos de IA generativa da AWS Bedrock, e retornar respostas sintetizadas em áudio, criando uma experiência conversacional natural e fluida.

A solução também inclui capacidades de análise de conversas através do **Amazon Nova Pro**, permitindo sumarização e extração de insights de diálogos gravados.

## 🛠️ Tecnologias/Ferramentas utilizadas

[<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/Visual_Studio_Code-007ACC?logo=visual-studio-code&logoColor=white">](https://code.visualstudio.com/)
[<img src="https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/lambda/)
[<img src="https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/bedrock/)
[<img src="https://img.shields.io/badge/Amazon-Nova_Sonic-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/bedrock/nova/)
[<img src="https://img.shields.io/badge/PyAudio-005C84?logo=python&logoColor=white">](https://pypi.org/project/PyAudio/)
[<img src="https://img.shields.io/badge/AsyncIO-3776AB?logo=python&logoColor=white">](https://docs.python.org/3/library/asyncio.html)
[<img src="https://img.shields.io/badge/Dotenv-ECD53F?logo=python&logoColor=white">](https://pypi.org/project/python-dotenv/)
[<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white">](https://github.com/)

## 🖥️ Funcionamento do sistema

### 🧩 Parte 1 - Lambda Handler

O ponto de entrada da aplicação é o arquivo lambda_function.py, que implementa o handler principal do AWS Lambda. Este componente é responsável por:

* **Inicialização da Sessão**: Configura e inicia uma sessão de streaming bidirecional com o Amazon Nova Sonic através do `AmazonNovaSonicService`.
* **Gerenciamento de Tarefas Assíncronas**: Utiliza `asyncio` com `nest_asyncio` para coordenar múltiplas tarefas concorrentes, incluindo captura e reprodução de áudio.
* **Processamento de Eventos**: Recebe parâmetros como `system_prompt` e `voice_id` do evento Lambda e os utiliza para personalizar a interação.
* **Tratamento de Erros**: Implementa try-catch robusto para capturar e reportar erros durante o processamento.

### 🎨 Parte 2 - Serviços e Utilitários

#### Serviços Bedrock

O arquivo bedrock_sonic_service.py contém a classe **`AmazonNovaSonicService`**, que encapsula toda a lógica de comunicação com o modelo Amazon Nova Sonic:

* **Streaming Bidirecional**: Gerencia fluxos de entrada e saída de áudio em tempo real usando `InvokeModelWithBidirectionalStreamOperationInput`.
* **Configuração de Sessão**: Envia eventos estruturados como `sessionStart`, `promptStart`, `contentStart` e `contentEnd` para controlar o ciclo de vida da conversa.
* **Processamento de Áudio**: 
  - Captura áudio do microfone a 16kHz (taxa otimizada para entrada)
  - Reproduz respostas a 24kHz (taxa de saída do modelo)
  - Utiliza codificação Base64 para transmissão de dados binários
* **Gerenciamento de Respostas**: Processa eventos de saída incluindo transcrições (`textOutput`) e áudio sintetizado (`audioOutput`).

#### Utilitários de Áudio

A pasta utils contém três classes especializadas:

1. **`AudioRecorder`**: 
   - Grava áudio do microfone usando PyAudio
   - Configuração otimizada: mono, 16kHz, 16 bits
   - Salvamento em formato WAV compatível com Nova Sonic
   - Implementação assíncrona com detecção de tecla Enter para parar

2. **`AudioProcessor`**:
   - **`prepare_input_audio()`**: Processa entrada de áudio de múltiplas fontes (arquivo local ou Base64)
   - Extrai dados PCM brutos removendo cabeçalhos WAV
   - **`prepare_success_response()`**: Formata respostas JSON compatíveis com API Gateway

3. **`FileConverter`**:
   - Converte arquivos de áudio para string Base64
   - Validação de existência de arquivo
   - Tratamento robusto de erros com logging detalhado

#### Modelos e Templates

* **amazon_nova_pro.py**: Classe para interação com Amazon Nova Pro, suportando:
  - Múltiplos formatos de entrada (texto, CSV, JSON, imagens)
  - Configuração de parâmetros de inferência (`max_new_tokens`)
  - Codificação automática de conteúdo multimídia em Base64

* **prompt_template.py**: Gerador de prompts estruturados para análise de conversas, com suporte a:
  - Formatação HTML para saídas
  - Placeholders para visualizações
  - Seções organizadas (informações de sessão, tópicos, sentimento, ações)

## 🔀 Arquitetura da aplicação

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Lambda                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          lambda_function.py (Handler)                 │  │
│  │  - Inicializa serviço Nova Sonic                      │  │
│  │  - Gerencia loop de eventos assíncrono                │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│  ┌────────────────▼──────────────────────────────────────┐  │
│  │     AmazonNovaSonicService (Streaming)                │  │
│  │  - Sessão bidirecional com Bedrock                    │  │
│  │  - Captura de áudio (16kHz mono)                      │  │
│  │  - Reprodução de áudio (24kHz mono)                   │  │
│  │  - Processamento de transcrições                      │  │
│  └────────────────┬──────────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────────┘
                    │
        ┌───────────▼──────────────┐
        │   AWS Bedrock Runtime    │
        │  ┌────────────────────┐  │
        │  │ Amazon Nova Sonic  │  │
        │  │  (STT + TTS + LLM) │  │
        │  └────────────────────┘  │
        │  ┌────────────────────┐  │
        │  │ Amazon Nova Pro    │  │
        │  │  (Análise de Conv.)│  │
        │  └────────────────────┘  │
        └──────────────────────────┘

┌─────────────────────────────────────────────┐
│          Utilitários Locais                 │
│  ┌──────────────────────────────────────┐   │
│  │ AudioRecorder - Captura microfone    │   │
│  │ AudioProcessor - Prep. dados         │   │
│  │ FileConverter - Base64 encoding      │   │
│  │ PromptTemplate - Geração de prompts  │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

O sistema utiliza uma arquitetura **event-driven** baseada em streaming assíncrono, onde:

1. O Lambda recebe eventos de entrada
2. Estabelece conexão bidirecional com Bedrock
3. Captura e envia áudio em chunks continuamente
4. Processa respostas em tempo real (texto + áudio)
5. Reproduz áudio sintetizado ao usuário

## 📁 Estrutura do projeto

```
.
├── lambda_function.py          # Handler principal do Lambda
├── .env                         # Variáveis de ambiente (credenciais AWS)
├── .env.example                 # Template de configuração
├── .gitignore                   # Arquivos ignorados pelo Git
├── models/
│   └── amazon_nova_pro.py       # Cliente para Amazon Nova Pro
├── services/
│   └── bedrock_sonic_service.py # Serviço de streaming bidirecional
├── template/
│   └── prompt_template.py       # Gerador de prompts estruturados
├── utils/
│   ├── audio_processor.py       # Processamento de dados de áudio
│   ├── audio_recorder.py        # Gravação via microfone
│   └── file_converter.py        # Conversão Base64
└── readme.md                    # Documentação do projeto
```

## 📌 Como executar o projeto

Para executar o projeto localmente, siga as instruções abaixo:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rafael-torres-nantes/AWSLambda-AmazonNovaSonicInference.git
   cd AWSLambda-AmazonNovaSonicInference
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Dependências principais:**
   - `pyaudio` - Captura e reprodução de áudio
   - `python-dotenv` - Gerenciamento de variáveis de ambiente
   - `nest_asyncio` - Suporte a loops de eventos aninhados
   - `aws-sdk-bedrock-runtime` - SDK para Bedrock

3. **Configure as variáveis de ambiente:**
   
   Renomeie .env.example para .env e preencha com suas credenciais AWS:
   
   ```bash
   AWS_ACCESS_KEY_ID="sua_access_key"
   AWS_SECRET_ACCESS_KEY="sua_secret_key"
   AWS_REGION="us-east-1"
   AMAZON_NOVA_SONIC_MODEL_ID="amazon.nova-sonic-v1:0"
   OUTPUT_DIR="./tmp/"
   ```

4. **Teste o serviço localmente:**
   
   Execute o arquivo principal:
   ```bash
   python lambda_function.py
   ```
   
   Ou teste componentes individuais:
   ```bash
   # Testar gravação de áudio
   python utils/audio_recorder.py
   
   # Testar conversão Base64
   python utils/file_converter.py
   
   # Testar streaming com Nova Sonic
   python services/bedrock_sonic_service.py
   ```

5. **Deploy no AWS Lambda:**
   
   ```bash
   # Crie um pacote de deployment
   zip -r lambda-package.zip . -x "*.git*" "*.env" "tmp/*"
   
   # Faça upload via AWS CLI ou Console
   aws lambda update-function-code \
     --function-name nova-sonic-assistant \
     --zip-file fileb://lambda-package.zip
   ```

## 🕵️ Dificuldades Encontradas

Durante o desenvolvimento do projeto, algumas dificuldades foram enfrentadas:

- **Streaming Bidirecional Assíncrono**: Implementar o fluxo de comunicação simultânea (envio e recebimento) com baixa latência exigiu domínio avançado de `asyncio` e gerenciamento cuidadoso de tasks concorrentes. A sincronização entre captura, processamento e reprodução foi um desafio crítico.

- **Compatibilidade de Formatos de Áudio**: Garantir que as taxas de amostragem (16kHz entrada vs 24kHz saída), canais (mono), e encodings (PCM, Base64) fossem corretamente convertidos entre PyAudio, arquivos WAV e a API do Bedrock exigiu múltiplos ajustes e validações.

- **Gerenciamento de Credenciais AWS**: Configurar corretamente as permissões IAM para acesso ao Bedrock Runtime, especialmente para modelos em preview como o Nova Sonic, e garantir que as credenciais fossem carregadas de forma segura tanto localmente quanto no Lambda.

- **Latência e Buffer de Áudio**: Otimizar o tamanho dos chunks de áudio (1024 bytes) e o intervalo de envio (`await asyncio.sleep(0.01)`) para minimizar latência perceptível sem sobrecarregar a API foi um processo iterativo de fine-tuning.

- **Tratamento de Eventos do Bedrock**: Parsear e interpretar corretamente os eventos estruturados retornados pelo modelo (`contentStart`, `textOutput`, `audioOutput`, `sessionEnd`) exigiu análise detalhada da documentação da API e debugging extensivo.

- **Ambiente Lambda vs Local**: Adaptar o código para funcionar tanto em ambiente de desenvolvimento local (com microfone físico) quanto no Lambda (com entrada Base64) requereu abstrações flexíveis no `AudioProcessor`.