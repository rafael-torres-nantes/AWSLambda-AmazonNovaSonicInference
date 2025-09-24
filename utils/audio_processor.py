import base64
import json
import wave
import io

from utils.file_converter import FileConverter

class AudioProcessor:
    """
    Classe utilitária para processar dados de áudio para o Lambda.
    Encapsula a lógica de preparação da entrada e formatação da saída.
    """

    def prepare_input_audio(self, event_body: dict) -> bytes:
        """
        Extrai, converte (se necessário) e prepara os bytes de áudio de entrada.

        Esta função inteligentemente lida com duas formas de entrada:
        1. Um caminho de arquivo local ('audio_filepath'), ideal para testes.
        2. Uma string base64 ('audio_base64'), ideal para invocações de API.

        Args:
            event_body (dict): O corpo do evento Lambda contendo os dados do áudio.

        Returns:
            bytes: Os dados brutos do áudio (PCM), prontos para serem enviados ao serviço Sonic.
        
        Raises:
            ValueError: Se nenhum dado de áudio válido for encontrado no evento.
        """
        print("[DEBUG][PROCESSOR] Iniciando preparação do áudio de entrada.")
        
        audio_base64 = event_body.get('audio_base64')
        audio_filepath = event_body.get('audio_filepath')

        # Se o caminho do arquivo for fornecido (para testes), converte-o para base64.
        if audio_filepath and not audio_base64:
            print(f"[DEBUG][PROCESSOR] Caminho do arquivo fornecido: {audio_filepath}. Convertendo...")
            converter = FileConverter()
            audio_base64 = converter.to_base64(audio_filepath)
        
        if not audio_base64:
            raise ValueError("Nenhum áudio fornecido. É necessário 'audio_base64' ou 'audio_filepath'.")

        # Decodifica a string base64 para bytes.
        print("[DEBUG][PROCESSOR] Decodificando áudio Base64 para memória...")
        decoded_wav_bytes = base64.b64decode(audio_base64)
        
        # Usa a biblioteca 'wave' para ler os bytes e extrair apenas os dados de áudio (PCM).
        # Isso é crucial para remover o cabeçalho do arquivo .wav antes de enviá-lo ao modelo.
        with wave.open(io.BytesIO(decoded_wav_bytes), 'rb') as wav_file:
            audio_data_bytes = wav_file.readframes(wav_file.getnframes())
            print(f"[DEBUG][PROCESSOR] {len(audio_data_bytes)} bytes de dados de áudio extraídos em memória.")

        return audio_data_bytes

    def prepare_success_response(self, output_filepath: str, transcription: str) -> dict:
        """
        Lê o arquivo de áudio de saída, codifica-o em Base64 e monta o corpo da resposta de sucesso.

        Args:
            output_filepath (str): O caminho para o arquivo .wav gerado pelo serviço Sonic.
            transcription (str): A transcrição em texto da resposta do modelo.

        Returns:
            dict: Um dicionário formatado para ser o corpo da resposta do API Gateway.
        """
        print(f"[DEBUG][PROCESSOR] Lendo o arquivo de resposta de: {output_filepath}")
        
        # Lê o arquivo de áudio de saída e o converte para base64 para o retorno da API.
        with open(output_filepath, 'rb') as audio_file:
            response_audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # Monta o corpo da resposta.
        response_body = {
            'message': 'Áudio processado com sucesso em memória.',
            'response_audio_base64': response_audio_base64,
            'transcription': transcription,
            'output_filepath': output_filepath
        }
        
        # Monta a resposta final no padrão do API Gateway.
        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps(response_body)
        }