import json
import boto3

class BedrockInferenceService:
    def __init__(self, model_id, request_body):
        """
        Inicializa o serviço AWS Bedrock.

        Cria uma sessão do Boto3 e um cliente para o serviço Bedrock, com a região configurada como 'us-east-1'.
        """

        # Inicializa o cliente do Bedrock Runtime
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

        # Define o ID do modelo Bedrock
        self.model_id = model_id
        print(f'[DEBUG][BEDROCK] O modelo Bedrock selecionado: {self.model_id}')

        # Define o corpo da requisição
        self.request_body = request_body
        
    # --------------------------------------------------------------------
    # Função que invoca o modelo e retorna a resposta gerada
    # --------------------------------------------------------------------
    def invoke_model(self):
        """
        Invoca os modelos Bedrock com o corpo da requisição gerado.
        Realiza a inferência do modelo de NLP e retorna o texto gerado.

        Returns:
            str: O texto gerado pelo modelo Bedrock.
        """

        try: 
            # Invoca o modelo Bedrock com o corpo da requisição gerado
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id, 
                contentType='application/json',
                accept='application/json',
                body=json.dumps(self.request_body)
            )

            print(response)

            # Lê o corpo da resposta e extrai o texto gerado pelo modelo
            response_body = json.loads(response.get('body').read())

            # Caso seja um modelo da Anthropic, o texto gerado pode estar em diferentes formatos
            if response_body.get('content', None):
                response_text = response_body.get('content')[0]['text']

            # Caso seja um modelo da Amazon, o texto gerado pode estar em um formato diferente
            if response_body.get('output', None):
                response_text = response_body['output']['message']['content'][0]['text']

            return response_text  # Retorna o texto gerado
    
        except Exception as e:
            print(f'[ERROR] Ocorreu um erro ao invocar o modelo: {e}')
            raise e