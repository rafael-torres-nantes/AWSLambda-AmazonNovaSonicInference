# AWS Lambda - Assistente Virtual com Amazon Nova Sonic

## 👨‍💻 Projeto desenvolvido por: 
[Rafael Torres Nantes](https://github.com/rafael-torres-nantes)

## Índice

* 📚 Contextualização do projeto
* 🛠️ Tecnologias/Ferramentas utilizadas
* 🖥️ Funcionamento do sistema
   * 🧩 Parte 1 - Backend
   * 🎨 Parte 2 - Serviços AWS
* 🔀 Arquitetura da aplicação
* 📁 Estrutura do projeto
* 📌 Como executar o projeto
* 🕵️ Dificuldades Encontradas

## 📚 Contextualização do projeto

Este projeto tem como objetivo criar um assistente virtual utilizando **AWS Lambda** e **Amazon Nova Sonic** para realizar interações de áudio em tempo real. A aplicação permite capturar áudio do usuário, processá-lo e gerar respostas em áudio utilizando modelos de IA generativa da AWS.

## 🛠️ Tecnologias/Ferramentas utilizadas

[<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/Visual_Studio_Code-007ACC?logo=visual-studio-code&logoColor=white">](https://code.visualstudio.com/)
[<img src="https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/lambda/)
[<img src="https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/bedrock/)
[<img src="https://img.shields.io/badge/PyAudio-005C84?logo=python&logoColor=white">](https://pypi.org/project/PyAudio/)
[<img src="https://img.shields.io/badge/Dotenv-181717?logo=python&logoColor=white">](https://pypi.org/project/python-dotenv/)
[<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white">](https://github.com/)

## 🖥️ Funcionamento do sistema

### 🧩 Parte 1 - Backend

O backend foi desenvolvido em **Python** e utiliza **AWS Lambda** para processar eventos de áudio. Ele é responsável por capturar o áudio do usuário, enviar os dados para o modelo **Amazon Nova Sonic** e retornar as respostas geradas.

* **Lambda Handler**: O arquivo lambda_function.py contém a lógica principal para inicializar o serviço, capturar e reproduzir áudio.
* **Processamento de Áudio**: A classe `AudioProcessor` realiza a decodificação e preparação dos dados de áudio.
* **Conversão de Arquivos**: A classe `FileConverter` permite converter arquivos para Base64.

### 🎨 Parte 2 - Serviços AWS

A integração com os serviços da AWS é feita através da classe `AmazonNovaSonicService`, que gerencia a comunicação com o modelo **Amazon Nova Sonic**. As principais funcionalidades incluem:

* **Streaming Bidirecional**: Captura e reprodução de áudio em tempo real.
* **Configuração de Sessões**: Inicialização e encerramento de sessões com o modelo.
* **Geração de Respostas**: Processamento de prompts e geração de áudio de saída.

## 🔀 Arquitetura da aplicação

A aplicação segue uma arquitetura modular, onde cada componente é responsável por uma funcionalidade específica. O **AWS Lambda** atua como o ponto central, enquanto os serviços da AWS Bedrock e o processamento local de áudio complementam o fluxo.

## 📁 Estrutura do projeto

A estrutura do projeto é organizada da seguinte maneira:

```
.
├── lambda_function.py
├── .env
├── .env.example
├── .gitignore
├── models/
│   └── amazon_nova_pro.py
├── services/
│   └── bedrock_sonic_service.py
├── template/
│   └── prompt_template.py
├── utils/
│   ├── audio_processor.py
│   ├── audio_recorder.py
│   └── file_converter.py
└── README.md
```

## 📌 Como executar o projeto

Para executar o projeto localmente, siga as instruções abaixo:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rafael-torres-nantes/aws-lambda-nova-sonic.git
   ```

2. **Instale as dependências:**
   Certifique-se de que o `Python` e o `pip` estão instalados.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Renomeie o arquivo .env.example para .env e insira suas credenciais da AWS.

4. **Execute o Lambda localmente:**
   Utilize o AWS SAM CLI ou outra ferramenta para testar o Lambda localmente.

5. **Teste o sistema:**
   Execute o arquivo lambda_function.py para iniciar o processamento de áudio.

## 🕵️ Dificuldades Encontradas

Durante o desenvolvimento, algumas dificuldades foram enfrentadas:

- **Streaming de Áudio**: Implementar o streaming bidirecional com baixa latência foi um desafio técnico significativo.
- **Integração com AWS Bedrock**: Configurar corretamente as permissões e credenciais para acessar os serviços da AWS exigiu atenção especial.
- **Processamento de Áudio**: Garantir a compatibilidade entre diferentes formatos de áudio e taxas de amostragem foi um ponto crítico.