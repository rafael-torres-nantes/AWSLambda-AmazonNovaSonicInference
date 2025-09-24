import os
import json
import uuid
import asyncio

# Importa as classes de serviço e os novos utilitários
from services.bedrock_sonic_service import AmazonNovaSonicService
from utils.audio_processor import AudioProcessor

from dotenv import load_dotenv
load_dotenv()

# Define o diretório de saída para os arquivos de áudio gerados
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/tmp')

def lambda_handler(event, context):
    """
    Lambda handler para processar um áudio em memória usando o Amazon Nova Sonic.
    Este handler foi refatorado para máxima legibilidade e modularidade.
    """
    # 1 - Log inicial e inspeção do evento
    print('*********** Start Sonic Lambda ***************')
    print(f'[DEBUG] Event: {event}')
    
    try:
        # 2 - Preparação do Áudio de Entrada
        audio_processor = AudioProcessor()
        
        # 3 - Extração do corpo do evento
        body = json.loads(event['body']) if 'body' in event and isinstance(event['body'], str) else event

        # 4 - Preparação dos bytes de áudio
        print("[DEBUG] Preparando o áudio de entrada...")
        audio_data_bytes = audio_processor.prepare_input_audio(body)
        
        # 5 - Extração de parâmetros opcionais
        system_prompt = body.get('system_prompt', 'You are a friendly and helpful assistant.')
        voice_id = body.get('voice_id', 'matthew')

        # 6 - Geração de um caminho único para o arquivo de saída
        request_id = str(uuid.uuid4())
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_audio_path = os.path.join(OUTPUT_DIR, f'output_{request_id}.wav')
        
        # 7 - Processamento do Áudio com o Serviço Sonic
        sonic_service = AmazonNovaSonicService()
        print("[DEBUG] Iniciando o processamento do áudio a partir de bytes...")
        
        # 8 - Chamada assíncrona para processar o áudio
        transcription = asyncio.run(sonic_service.process_audio_from_bytes(
            audio_bytes=audio_data_bytes,
            output_file_path=output_audio_path,
            system_prompt=system_prompt,
            voice_id=voice_id
        ))
        
        print(f"[DEBUG] Processamento concluído. Transcrição: '{transcription}'")

        # 9 - Preparação da Resposta de Sucesso
        print(f"[INFO] Arquivo de saída mantido em: {output_audio_path}")
        return audio_processor.prepare_success_response(output_audio_path, transcription)

    except Exception as e:
        print(f'[ERROR] {e}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e), 'message': 'Erro ao processar o áudio.'})
        }

# --- Bloco de Teste Local ---
if __name__ == "__main__":
    print("\n--- Iniciando Teste Local do Lambda Handler ---")
    
    test_audio_file = "./tmp/recording_1758752613.wav" # <-- SEU ARQUIVO .WAV
    
    if not os.path.exists(test_audio_file):
        print(f"\n[ATENÇÃO] O arquivo de teste '{test_audio_file}' não foi encontrado.")
    else:
        mock_event = {
            "audio_filepath": test_audio_file,
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