import base64
import os

class FileConverter:
    """
    Classe utilitária para conversões de arquivos, como codificação para Base64.
    """

    def to_base64(self, file_path: str) -> str:
        """
        Converte um arquivo de áudio (ou qualquer arquivo) para uma string Base64.

        Args:
            file_path (str): O caminho completo para o arquivo a ser convertido.

        Returns:
            str: A representação do arquivo em string Base64.
        
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado no caminho especificado.
            Exception: Para outros erros de leitura de arquivo.
        """
        print(f"[DEBUG][CONVERTER] Tentando converter o arquivo: {file_path}")
        
        if not os.path.exists(file_path):
            error_message = f"Arquivo não encontrado em '{file_path}'"
            print(f"[ERROR][CONVERTER] {error_message}")
            raise FileNotFoundError(error_message)

        try:
            # Abre o arquivo em modo de leitura binária ('rb')
            with open(file_path, 'rb') as file:
                # Lê todo o conteúdo binário do arquivo
                binary_content = file.read()
                
                # Codifica o conteúdo binário para Base64
                base64_bytes = base64.b64encode(binary_content)
                
                # Decodifica os bytes Base64 para uma string UTF-8
                base64_string = base64_bytes.decode('utf-8')
            
            print(f"[DEBUG][CONVERTER] Arquivo convertido para Base64 com sucesso. Tamanho da string: {len(base64_string)} caracteres.")
            return base64_string
            
        except Exception as e:
            error_message = f"Falha ao ler ou converter o arquivo '{file_path}': {e}"
            print(f"[ERROR][CONVERTER] {error_message}")
            raise

# --- Bloco de Teste ---
if __name__ == "__main__":
    print("--- Testando o FileConverter ---")
    
    # Crie um arquivo de teste simples para garantir que o teste funcione
    test_dir = '{OUTPUT_DIR}'
    os.makedirs(test_dir, exist_ok=True)
    test_file_path = os.path.join(test_dir, 'converter_test.txt')
    with open(test_file_path, 'w') as f:
        f.write("Este é um teste!")

    converter = FileConverter()
    
    try:
        # Teste com um arquivo que existe
        b64_content = converter.to_base64(test_file_path)
        print(f"✅ [SUCCESS] Conteúdo em Base64: {b64_content}")
        
        # Teste com um arquivo que não existe
        print("\n--- Testando cenário de erro ---")
        converter.to_base64("caminho/para/arquivo/inexistente.wav")
        
    except FileNotFoundError as e:
        print(f"✅ [SUCCESS] Capturou o erro esperado de arquivo não encontrado: {e}")

    except Exception as e:
        print(f"❌ [FAIL] Um erro inesperado ocorreu: {e}")

    # finally:
    #     # Limpa o arquivo de teste
    #     os.remove(test_file_path)
