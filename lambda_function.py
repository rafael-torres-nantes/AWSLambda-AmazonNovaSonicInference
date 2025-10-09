import os
import json
import uuid
import asyncio
import nest_asyncio

# Importa as classes de serviço e os novos utilitários
from services.bedrock_sonic_service import AmazonNovaSonicService
from utils.audio_processor import AudioProcessor

from dotenv import load_dotenv
load_dotenv()

# Define o diretório de saída para os arquivos de áudio gerados
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/tmp')

# Aplica o nest_asyncio para lidar com loops de eventos existentes
nest_asyncio.apply()

def lambda_handler(event, context):
    """
    Lambda handler atualizado para streaming bidirecional.
    """
    print('*********** Start Sonic Lambda with Streaming ***************')
    print(f'[DEBUG] Event: {event}')

    try:
        # 2 - Inicializa o serviço Amazon Nova Sonic Service
        sonic_service = AmazonNovaSonicService()
        loop = asyncio.get_event_loop()

        # 3 - Inicia a sessão de streaming e as tarefas de reprodução e captura
        loop.run_until_complete(sonic_service.start_session())
        playback_task = loop.create_task(sonic_service.play_audio())
        capture_task = loop.create_task(sonic_service.capture_audio())

        # 4 - Aguarda o término das tarefas de reprodução e captura
        loop.run_until_complete(asyncio.gather(playback_task, capture_task))

        # 5 - Finaliza a sessão e obtém o áudio gerado
        loop.run_until_complete(sonic_service.end_session())

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Streaming concluído com sucesso.'})
        }

    except Exception as e:
        print(f'[ERROR] {e}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e), 'message': 'Erro ao processar o streaming.'})
        }

# --- Bloco de Teste Local ---
if __name__ == "__main__":
    print("\n--- Iniciando Teste Local do Lambda Handler ---")

    mock_event = {
        "system_prompt": "Please respond in English with a single, direct sentence.",
        "voice_id": "matthew"
    }
    response = lambda_handler(event=mock_event, context={})

    print("\n--- Resposta do Lambda Handler ---")
    body_content = json.loads(response.get('body', '{}'))
    if 'response_audio_base64' in body_content:
        body_content['response_audio_base64'] = body_content['response_audio_base64'][:80] + '...[truncado]'

    print(f"Status Code: {response['statusCode']}")
    print("Body:", json.dumps(body_content, indent=2, ensure_ascii=False))
    print("\n--- Fim do Teste Local ---")