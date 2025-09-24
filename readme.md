# Amazon Nova Sonic - Speech to Speech

## 👨‍💻 Projeto desenvolvido por:

[Rafael Torres Nantes](https://github.com/rafael-torres-nantes)

## Índice

  * [📚 Contextualização do projeto](https://www.google.com/search?q=%23-contextualiza%C3%A7%C3%A3o-do-projeto)
  * [🛠️ Tecnologias/Ferramentas utilizadas](https://www.google.com/search?q=%23%EF%B8%8F-tecnologiasferramentas-utilizadas)
  * [🖥️ Funcionamento do sistema](https://www.google.com/search?q=%23%EF%B8%8F-funcionamento-do-sistema)
  * [🔀 Arquitetura da aplicação](https://www.google.com/search?q=%23-arquitetura-da-aplica%C3%A7%C3%A3o)
  * [📁 Estrutura do projeto](https://www.google.com/search?q=%23-estrutura-do-projeto)
  * [📌 Como executar o projeto](https://www.google.com/search?q=%23-como-executar-o-projeto)
  * [🕵️ Dificuldades Encontradas](https://www.google.com/search?q=%23%EF%B8%8F-dificuldades-encontradas)

## 📚 Contextualização do projeto

O projeto tem como objetivo criar um **assistente virtual inteligente** capaz de manter conversas fluidas e em tempo real através de áudio. A solução utiliza o **Amazon Nova Sonic**, um modelo de IA generativa da AWS especializado em interações `speech-to-speech` (fala-para-fala), sobre a plataforma **AWS Bedrock**.

O sistema foi projetado para operar dentro de um ambiente serverless (AWS Lambda), recebendo um arquivo de áudio do usuário, processando a fala para entender a intenção, gerando uma resposta textual e, finalmente, convertendo essa resposta de volta para um áudio com som natural, tudo em uma única execução.

## 🛠️ Tecnologias/Ferramentas utilizadas

[\<img src="https://img.shields.io/badge/Python-3776AB?logo=python\&logoColor=white"\>](https://www.python.org/)
[\<img src="https://img.shields.io/badge/Visual\_Studio\_Code-007ACC?logo=visual-studio-code\&logoColor=white"\>](https://code.visualstudio.com/)
[\<img src="https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws\&logoColor=white"\>](https://aws.amazon.com/bedrock/)
[\<img src="https://img.shields.io/badge/AWS-Lambda-FF9900?logo=aws-lambda\&logoColor=white"\>](https://aws.amazon.com/lambda/)
[\<img src="https://img.shields.io/badge/Boto3-0073BB?logo=amazonaws\&logoColor=white"\>](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[\<img src="https://img.shields.io/badge/PyAudio-005C84?logo=python\&logoColor=white"\>](https://pypi.org/project/PyAudio/)
[\<img src="https://img.shields.io/badge/GitHub-181717?logo=github\&logoColor=white"\>](https://github.com/)

## 🖥️ Funcionamento do sistema

O sistema é encapsulado em uma única **AWS Lambda Function**, que orquestra a interação com o modelo Amazon Nova Sonic. O fluxo de execução é totalmente processado em memória para maior eficiência, sem a necessidade de salvar arquivos de entrada intermediários.

  * **Ponto de Entrada (`lambda_function.py`):** Este arquivo contém o `lambda_handler`, que serve como o ponto de entrada principal. Ele é responsável por:

    1.  Receber a requisição, que contém o áudio do usuário codificado em Base64.
    2.  Utilizar classes utilitárias para preparar o áudio.
    3.  Instanciar e invocar o serviço do Amazon Nova Sonic.
    4.  Formatar a resposta final (áudio em Base64 e transcrição) e retorná-la.

  * **Serviço Principal (`services/bedrock_sonic_service.py`):** A classe `AmazonNovaSonicService` abstrai toda a complexidade da comunicação com a API de streaming bidirecional do Bedrock. Suas responsabilidades incluem:

    1.  Estabelecer e configurar a sessão de streaming.
    2.  Enviar o áudio do usuário em chunks para o modelo.
    3.  Receber e processar os eventos de resposta (texto e áudio).
    4.  Salvar o áudio de resposta em um arquivo temporário.

  * **Utilitários (`utils/`):** A pasta `utils` contém classes auxiliares com responsabilidades únicas, mantendo o código limpo e modular:

      * `audio_recorder.py`: Grava áudio do microfone para facilitar testes locais.
      * `file_converter.py`: Converte arquivos para o formato Base64.
      * `audio_processor.py`: Centraliza a lógica de preparação do áudio de entrada e formatação da resposta para o Lambda.

## 🔀 Arquitetura da aplicação

A aplicação opera em uma arquitetura serverless, centrada na **AWS Lambda**. O fluxo é o seguinte:

1.  Um evento (ex: uma chamada de API Gateway) aciona a função Lambda, enviando o áudio do usuário.
2.  A Lambda decodifica o áudio e o passa para o `AmazonNovaSonicService`.
3.  O serviço estabelece uma conexão de streaming com o **Amazon Nova Sonic** via AWS Bedrock.
4.  O áudio de entrada é transmitido em chunks para o modelo.
5.  O modelo processa a fala, gera uma resposta e a transmite de volta em chunks de áudio e eventos de texto.
6.  O serviço captura a resposta, salva o áudio de saída em um arquivo `.wav` e coleta a transcrição.
7.  A Lambda codifica o áudio de resposta em Base64 e o retorna, juntamente com a transcrição, no corpo da resposta.

## 📁 Estrutura do projeto

A estrutura do projeto foi organizada para promover a modularidade e a clareza:

```
.
├── services/
│   └── bedrock_sonic_service.py # Lógica de comunicação com o Amazon Nova Sonic
├── utils/
│   ├── audio_processor.py       # Prepara áudio de entrada e formata a saída
│   ├── audio_recorder.py        # Grava áudio para testes locais
│   └── file_converter.py        # Converte arquivos para Base64
├── tmp/
│   └── ...                      # Diretório para arquivos de áudio temporários
├── lambda_function.py           # Ponto de entrada da aplicação (handler)
├── requirements.txt             # Dependências do Python
└── README.md
```

## 📌 Como executar o projeto

Para executar o projeto localmente para fins de teste, siga as instruções abaixo:

1.  **Clone o repositório:**

    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    ```

2.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

    *Observação: A instalação do `PyAudio` pode exigir dependências adicionais dependendo do seu sistema operacional.*

3.  **Configure suas credenciais AWS:**
    Certifique-se de que suas credenciais da AWS estejam configuradas no ambiente, pois o `boto3` irá procurá-las.

4.  **Grave um áudio de teste (opcional):**
    Use o gravador para criar um arquivo `.wav` para usar no teste.

    ```bash
    python -m utils.audio_recorder
    ```

5.  **Execute a função Lambda localmente:**
    Abra o arquivo `lambda_function.py`, atualize a variável `test_audio_file` com o caminho para o seu áudio de teste e execute o script:

    ```bash
    python lambda_function.py
    ```

    A saída da execução, incluindo a transcrição e o caminho do áudio de resposta, será exibida no terminal.

## 🕵️ Dificuldades Encontradas

Durante o desenvolvimento do projeto, alguns desafios foram enfrentados:

  - **API de Streaming Bidirecional:** A API do Amazon Nova Sonic é assíncrona e baseada em eventos, o que exigiu uma implementação cuidadosa com `asyncio` para gerenciar o fluxo de dados sem bloquear a execução ou perder eventos.
  - **Formato dos Eventos:** A API é muito rigorosa quanto à estrutura dos eventos JSON de configuração. Pequenas omissões ou erros nos payloads causavam falhas genéricas, exigindo uma depuração minuciosa e comparação com a documentação oficial.
  - **Compatibilidade com AWS Lambda:** Adaptar um serviço de streaming persistente para o modelo de execução curto e sem estado do Lambda foi um desafio de arquitetura, resolvido processando o ciclo de vida completo do stream em uma única invocação.