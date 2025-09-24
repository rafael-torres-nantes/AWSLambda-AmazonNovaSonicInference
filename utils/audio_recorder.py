# utils/audio_recorder.py

import os
import pyaudio
import wave
import time
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class AudioRecorder:
    """
    Classe utilitária para gravar áudio do microfone e salvar em um arquivo .wav.
    """

    def __init__(self):
        """
        Inicializa o gravador de áudio com configurações padrão.
        Estas configurações são otimizadas para o Amazon Nova Sonic.
        """
        # Configurações do áudio
        self.format = pyaudio.paInt16  # Formato dos samples (16 bits)
        self.channels = 1  # Mono
        self.rate = 16000  # Taxa de amostragem em Hz (16kHz é ideal para o Sonic)
        self.chunk_size = 1024  # Tamanho do buffer de leitura
        
        # Diretório de saída para os arquivos gravados
        # Pega do .env ou usa './tmp/' como padrão
        self.output_dir = os.getenv('OUTPUT_DIR', './tmp/')
        
        # Garante que o diretório de saída exista
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"[DEBUG][RECORDER] Gravador de áudio inicializado.")
        print(f"[DEBUG][RECORDER] Áudios serão salvos em: {self.output_dir}")

    async def record(self) -> str:
        """
        Grava o áudio do microfone até que o usuário pressione Enter.

        Returns:
            str: O caminho completo para o arquivo de áudio .wav salvo.
        """
        # Inicializa o PyAudio
        p = pyaudio.PyAudio()

        # Abre o stream de áudio para gravação
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)

        print("\n🎤 [INFO] Gravando... Pressione a tecla Enter para parar.")

        frames = []
        is_recording = True

        # --- Loop de gravação ---
        # A gravação ocorre em um loop, lendo chunks de áudio do microfone.
        # A verificação da tecla Enter é feita em uma tarefa separada para não bloquear a gravação.
        
        # Função para aguardar o Enter do usuário de forma assíncrona
        async def wait_for_enter():
            nonlocal is_recording
            await asyncio.get_event_loop().run_in_executor(None, input)
            is_recording = False

        # Inicia a tarefa que espera pelo Enter
        enter_task = asyncio.create_task(wait_for_enter())

        while is_recording:
            try:
                # Lê um chunk de dados do microfone
                data = stream.read(self.chunk_size)
                frames.append(data)
                # Uma pequena pausa para permitir que outras tarefas (como a verificação do Enter) rodem
                await asyncio.sleep(0.01)
            except KeyboardInterrupt:
                # Permite parar com Ctrl+C também
                is_recording = False

        await enter_task

        print("🔴 [INFO] Gravação finalizada. Salvando arquivo...")

        # --- Finalização e salvamento ---
        # Para e fecha o stream de áudio
        stream.stop_stream()
        stream.close()
        # Encerra a instância do PyAudio
        p.terminate()

        # Gera um nome de arquivo único com timestamp
        timestamp = int(time.time())
        filename = f"recording_{timestamp}.wav"
        file_path = os.path.join(self.output_dir, filename)

        # Abre o arquivo .wav no modo de escrita binária
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            # Escreve todos os frames gravados no arquivo
            wf.writeframes(b''.join(frames))

        print(f"✅ [SUCCESS] Áudio salvo com sucesso em: {file_path}")

        return file_path

# --- Bloco de Teste ---
# Este bloco permite que você execute este arquivo diretamente para testar a gravação.
async def test_recorder():
    """
    Função para testar a classe AudioRecorder de forma independente.
    """
    recorder = AudioRecorder()
    try:
        saved_file = await recorder.record()
        print(f"\n[TEST RESULT] Arquivo de teste gerado: {saved_file}")
        # Verifica o tamanho do arquivo
        file_size = os.path.getsize(saved_file)
        print(f"[TEST RESULT] Tamanho do arquivo: {file_size / 1024:.2f} KB")
    except Exception as e:
        print(f"\n[TEST ERROR] Ocorreu um erro durante o teste: {e}")
        print("[TEST HINT] Verifique se você tem o 'PyAudio' instalado e as permissões de microfone.")

if __name__ == "__main__":
    # Executa a função de teste
    asyncio.run(test_recorder())