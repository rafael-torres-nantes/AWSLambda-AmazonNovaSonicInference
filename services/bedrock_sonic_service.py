import os
import asyncio
import base64
import json
import uuid
import wave
from dotenv import load_dotenv

from aws_sdk_bedrock_runtime.client import BedrockRuntimeClient
from aws_sdk_bedrock_runtime.config import Config, HTTPAuthSchemeResolver, SigV4AuthScheme
from aws_sdk_bedrock_runtime.models import InvokeModelWithBidirectionalStreamInputChunk, BidirectionalInputPayloadPart, InvokeModelWithBidirectionalStreamOperationInput
from smithy_aws_core.credentials_resolvers.environment import EnvironmentCredentialsResolver

load_dotenv()

class AmazonNovaSonicService:
    """
    Classe de serviço otimizada para gerenciar a interação com o Amazon Nova Sonic.
    Esta versão aceita dados de áudio diretamente em memória (bytes).
    """
    def __init__(self, model_id='amazon.nova-sonic-v1:0', region='us-east-1'):
        self.model_id = model_id
        self.region = region
        self.client = None
        self.stream_response = None
        self.is_active = False
        self.audio_output_queue = asyncio.Queue()
        self.transcription = ""
        self.prompt_name = str(uuid.uuid4())
        self.audio_content_name = str(uuid.uuid4())
        
        self.chunks_sent = 0
        self.chunks_received = 0
        self.chunks_written = 0
        
        print(f"[DEBUG][SONIC_SERVICE] Serviço inicializado para o modelo: {self.model_id} na região {self.region}")

    # ... (os métodos _initialize_client, _send_event, e _start_and_configure_session permanecem os mesmos) ...
    def _initialize_client(self):
        if self.client: return
        print("[DEBUG][SONIC_SERVICE] Inicializando cliente Bedrock para streaming...")
        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=EnvironmentCredentialsResolver(),
            http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
            http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()}
        )
        self.client = BedrockRuntimeClient(config=config)

    async def _send_event(self, event_data: dict):
        try:
            event_json = json.dumps(event_data)
            chunk = InvokeModelWithBidirectionalStreamInputChunk(
                value=BidirectionalInputPayloadPart(bytes_=event_json.encode('utf-8'))
            )
            await self.stream_response.input_stream.send(chunk)
        except Exception as e:
            print(f"[ERROR][SONIC_SERVICE] Falha ao enviar evento: {e}")
            raise

    async def _start_and_configure_session(self, system_prompt: str, voice_id: str):
        self._initialize_client()
        self.stream_response = await self.client.invoke_model_with_bidirectional_stream(
            InvokeModelWithBidirectionalStreamOperationInput(model_id=self.model_id)
        )
        self.is_active = True
        print("[DEBUG][SONIC_SERVICE] Sessão de streaming estabelecida.")

        session_start_event = {"event": {"sessionStart": {"inferenceConfiguration": {"maxTokens": 1024, "temperature": 0.7}}}}
        await self._send_event(session_start_event)

        prompt_start_event = {
            "event": {"promptStart": {"promptName": self.prompt_name,
                "audioOutputConfiguration": {
                    "mediaType": "audio/lpcm", "sampleRateHertz": 24000,
                    "sampleSizeBits": 16, "channelCount": 1,
                    "voiceId": voice_id, "encoding": "base64", "audioType": "SPEECH"
                }}}}
        await self._send_event(prompt_start_event)
        
        system_prompt_content_name = str(uuid.uuid4())
        await self._send_event({"event": {"contentStart": {"promptName": self.prompt_name, "contentName": system_prompt_content_name, "type": "TEXT", "role": "SYSTEM", "textInputConfiguration": {"mediaType": "text/plain"}}}})
        await self._send_event({"event": {"textInput": {"promptName": self.prompt_name, "contentName": system_prompt_content_name, "content": system_prompt}}})
        await self._send_event({"event": {"contentEnd": {"promptName": self.prompt_name, "contentName": system_prompt_content_name}}})
        
        print(f"[DEBUG][SONIC_SERVICE] Sessão configurada com prompt: '{system_prompt}' e voz: '{voice_id}'")


    async def _stream_audio_from_bytes(self, audio_bytes: bytes):
        """
        Divide um objeto de bytes de áudio em pedaços (chunks), codifica em base64
        e os envia em sequência através do stream para o modelo.

        Args:
            audio_bytes (bytes): Os dados brutos do áudio (sem cabeçalho WAV).
        
        Returns:
            None
        """
        print(f"[DEBUG][SONIC_SERVICE] Iniciando streaming a partir de {len(audio_bytes)} bytes em memória.")
        
        audio_start_event = {
            "event": {"contentStart": {"promptName": self.prompt_name, "contentName": self.audio_content_name, "type": "AUDIO", "role": "USER", "interactive": True,
                "audioInputConfiguration": {
                    "mediaType": "audio/lpcm", "sampleRateHertz": 16000,
                    "sampleSizeBits": 16, "channelCount": 1,
                    "audioType": "SPEECH", "encoding": "base64"
                }}}}
        await self._send_event(audio_start_event)
        
        chunk_size = 1024 * 2
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            encoded_chunk = base64.b64encode(chunk).decode('utf-8')
            await self._send_event({"event": {"audioInput": {"promptName": self.prompt_name, "contentName": self.audio_content_name, "content": encoded_chunk}}})
            self.chunks_sent += 1
            await asyncio.sleep(0.05)
        
        await self._send_event({"event": {"contentEnd": {"promptName": self.prompt_name, "contentName": self.audio_content_name}}})
        print(f"[DEBUG][SONIC_SERVICE] Streaming a partir de bytes finalizado. Total de chunks enviados: {self.chunks_sent}")


    async def _process_responses(self):
        # ... (sem alterações) ...
        print("[DEBUG][SONIC_SERVICE] Processador de respostas iniciado.")
        try:
            while self.is_active:
                output = await self.stream_response.await_output()
                result = await output[1].receive()
                if result.value and result.value.bytes_:
                    json_data = json.loads(result.value.bytes_.decode('utf-8'))
                    event = json_data.get('event', {})
                    if 'textOutput' in event:
                        self.transcription += event['textOutput']['content']
                    elif 'audioOutput' in event:
                        audio_bytes = base64.b64decode(event['audioOutput']['content'])
                        await self.audio_output_queue.put(audio_bytes)
                        self.chunks_received += 1
                    elif 'completionEnd' in event:
                        print("[DEBUG][SONIC_RESPONSE] Evento 'completionEnd' recebido. Finalizando.")
                        self.is_active = False
        except Exception as e:
            if "stream has been closed" not in str(e) and "cancellation" not in str(e).lower():
                print(f"[ERROR][SONIC_SERVICE] Erro ao processar respostas: {e}")
            self.is_active = False
        finally:
            await self.audio_output_queue.put(None)
            print(f"[DEBUG][SONIC_SERVICE] Processador de respostas finalizado. Total de chunks de áudio recebidos: {self.chunks_received}")

    async def _save_response_audio_to_file(self, output_file_path: str):
        # ... (sem alterações) ...
        print(f"[DEBUG][SONIC_SERVICE] Aguardando áudio para salvar em: {output_file_path}")
        with wave.open(output_file_path, 'wb') as output_wav:
            output_wav.setnchannels(1)
            output_wav.setsampwidth(2)
            output_wav.setframerate(24000)
            while True:
                audio_chunk = await self.audio_output_queue.get()
                if audio_chunk is None: break
                output_wav.writeframes(audio_chunk)
                self.chunks_written += 1
        file_size = os.path.getsize(output_file_path)
        print(f"✅ [SUCCESS] Áudio de resposta salvo. Chunks escritos: {self.chunks_written}. Tamanho do arquivo: {file_size / 1024:.2f} KB")

    async def _end_session(self):
        # ... (sem alterações) ...
        if not self.stream_response: return
        print("[DEBUG][SONIC_SERVICE] Encerrando sessão...")
        try:
            await self._send_event({"event": {"promptEnd": {"promptName": self.prompt_name}}})
            await self._send_event({"event": {"sessionEnd": {}}})
            await self.stream_response.input_stream.close()
            print("[DEBUG][SONIC_SERVICE] Sessão encerrada.")
        except Exception as e:
            print(f"[WARNING] Erro menor ao encerrar a sessão (pode ser normal se já fechada pelo servidor): {e}")

    async def process_audio_from_bytes(self, audio_bytes: bytes, output_file_path: str, system_prompt: str, voice_id: str = "matthew"):
        """
        Método público que orquestra o processo a partir de dados de áudio em memória.

        Args:
            audio_bytes (bytes): Os dados do áudio de entrada (sem cabeçalho).
            output_file_path (str): Caminho para salvar o arquivo .wav de saída.
            system_prompt (str): A instrução de comportamento para o assistente.
            voice_id (str): O ID da voz para a resposta.
            
        Returns:
            str: A transcrição em texto da resposta do assistente.
        """
        try:
            await self._start_and_configure_session(system_prompt, voice_id)
            
            response_task = asyncio.create_task(self._process_responses())
            save_audio_task = asyncio.create_task(self._save_response_audio_to_file(output_file_path))
            
            # Chama o novo método que transmite a partir de bytes
            await self._stream_audio_from_bytes(audio_bytes)

            await response_task
            await save_audio_task
            
            return self.transcription.strip()
        finally:
            self.is_active = False
            await self._end_session()