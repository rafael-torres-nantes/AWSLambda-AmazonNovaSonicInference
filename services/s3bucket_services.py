import os
import boto3
import base64
from datetime import datetime
from typing import Optional, Dict, Union
from botocore.exceptions import ClientError
from botocore.client import Config

class S3BucketClass: 
    def __init__(self, region_name: str = 'us-east-2', tmp_dir: str = '/tmp/'):
        
        # Configuração explícita para a região com retry strategy
        s3_config = Config(
            signature_version='s3v4',
            region_name=region_name,
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            },
            # Define timeout mais longo para uploads
            connect_timeout=60,
            read_timeout=60
        )
        
        # Criação do cliente S3 com configuração otimizada
        self.s3_client = boto3.client(
            's3', 
            region_name=region_name, 
            config=s3_config
        )
        
        # Armazena a região para uso posterior
        self.region_name = region_name
        
        # Define o caminho de download para os arquivos baixados do S3
        self.download_path = tmp_dir
        
        # Cria o diretório de download se não existir
        os.makedirs(self.download_path, exist_ok=True)
        
        print(f"[DEBUG] S3BucketClass initialized for region: {region_name}")
    
    def upload_file(self, file_path: str, bucket_name: str = None, bucket: str = None, key: str = None) -> Dict:
        """
        Função para fazer upload de um arquivo para o bucket S3

        Args:
            file_path (str): Caminho do arquivo a ser enviado
            bucket_name (str): Nome do bucket S3 (usado para compatibilidade)
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo no bucket (opcional, será gerado se não fornecido)
            
        Returns:
            Dict: Dicionário com informações detalhadas do upload
        """
        # Determine bucket name (support both parameter names for backward compatibility)
        bucket_name = bucket_name or bucket
        if not bucket_name:
            return {
                'success': False,
                'error': 'Bucket name is required',
                'bucket_name': '',
                's3_key': ''
            }
        
        # If key is not provided, generate one from filename
        if key is None:
            key = os.path.basename(file_path)
        
        try:
            print(f"[DEBUG] Starting upload to bucket: {bucket_name}, key: {key}, region: {self.region_name}")
            
            # Upload do arquivo para o bucket S3 (sem ACL público para usar presigned URLs)
            self.s3_client.upload_file(
                file_path, 
                bucket_name, 
                key,
                ExtraArgs={
                    'ContentType': self._get_content_type(file_path),
                    # Adiciona metadados para melhor controle
                    'Metadata': {
                        'uploaded_by': 'ai-assistant',
                        'upload_timestamp': datetime.utcnow().isoformat(),
                        'region': self.region_name
                    }
                }
            )
            print(f"[DEBUG] Upload successful for key: {key}")
            
            # Read file for base64 encoding
            with open(file_path, 'rb') as file:
                file_content = file.read()
                base64_content = base64.b64encode(file_content).decode('utf-8')
            
            # Get file size
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            # Determine content type based on file extension
            content_type = self._get_content_type(file_path)
            
            # Construir URL S3 baseada na região
            s3_url = self._construct_s3_url(bucket_name, key)
            
            return {
                'success': True,
                'bucket_name': bucket_name,
                's3_key': key,
                's3_url': s3_url,  # Este será substituído pelo presigned URL
                'upload_timestamp': datetime.utcnow().isoformat() + 'Z',
                'base64_content': base64_content,
                'content_type': content_type,
                'file_size_bytes': file_size,
                'file_size_mb': file_size_mb,
                'region': self.region_name
            }
        
        except ClientError as e:
            print(f"[DEBUG] AWS ClientError ao fazer upload do arquivo para o S3: {e}")
            return {
                'success': False,
                'error': f"AWS Error: {str(e)}",
                'bucket_name': bucket_name,
                's3_key': key,
                'region': self.region_name
            }
        except Exception as e:
            print(f"[DEBUG] Erro geral ao fazer upload do arquivo para o S3: {e}")
            return {
                'success': False,
                'error': f"General Error: {str(e)}",
                'bucket_name': bucket_name,
                's3_key': key,
                'region': self.region_name
            }
    
    def _construct_s3_url(self, bucket_name: str, key: str) -> str:
        """
        Constrói a URL S3 baseada na região configurada
        
        Args:
            bucket_name (str): Nome do bucket
            key (str): Chave do objeto
            
        Returns:
            str: URL S3 formatada corretamente
        """
        if self.region_name == 'us-east-1':
            return f"https://{bucket_name}.s3.amazonaws.com/{key}"
        else:
            return f"https://{bucket_name}.s3.{self.region_name}.amazonaws.com/{key}"
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Determina o content type baseado na extensão do arquivo
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            str: Content type do arquivo
        """
        extension = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/mp4',
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def generate_presigned_url(self, bucket: str, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Gerar uma URL pré-assinada para um objeto no bucket S3
        
        Args:
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo
            expiration (int): Tempo de expiração em segundos (default: 1 hora)
            
        Returns:
            str: URL pré-assinada ou None se houver erro
        """
        try:
            print(f"[DEBUG] Gerando presigned URL para bucket: {bucket}, key: {key}, região: {self.region_name}")
            
            # Verificar se o objeto existe antes de gerar a URL
            try:
                self.s3_client.head_object(Bucket=bucket, Key=key)
                print(f"[DEBUG] Objeto confirmado no S3: {key}")
            
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    print(f"[DEBUG] ERRO: Objeto não encontrado no S3: {key}")
                    return None
                else:
                    print(f"[DEBUG] Erro ao verificar objeto: {e}")
                    return None
            
            # Gerar URL pré-assinada com configurações explícitas
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': key
                },
                ExpiresIn=expiration,
                HttpMethod='GET'
            )
            
            print(f"[DEBUG] Presigned URL gerada com sucesso")
            print(f"[DEBUG] URL: {presigned_url[:100]}...")
            
            return presigned_url
        
        except ClientError as e:
            print(f"[DEBUG] AWS ClientError generating presigned URL: {e}")
            print(f"[DEBUG] Error Code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
            print(f"[DEBUG] Error Message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
            return None
        except Exception as e:
            print(f"[DEBUG] Erro geral generating presigned URL: {e}")
            return None
    
    def download_file(self, bucket: str, key: str, filename : str = None) -> bool:
        """
        Download de um arquivo do bucket S3 para o caminho especificado

        Args:
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo no bucket
            filename (str): Nome do arquivo local para salvar o download
        """

        if not filename:
            # Caminho do arquivo para download
            file_path = os.path.join(self.download_path, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if filename:
            # Caminho do arquivo para download
            file_path = os.path.join(self.download_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            # Download do arquivo do bucket S3
            self.s3_client.download_file(bucket, key, file_path)
            return file_path
        
        except ClientError as e:
            print(f"[DEBUG] Erro ao fazer download do arquivo do S3: {e}")
            raise e
              
    def delete_object(self, bucket: str, key: str) -> bool:
        """
        Deleta um objeto do bucket S3 especificado por chave

        Args:
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo no bucket
        """
        try:
            # Deleta o objeto do bucket S3 especificado
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        
        except ClientError as e:
            print(f"[DEBUG] Erro ao deletar objeto do S3: {e}")
            raise e
    
    def get_object(self, bucket: str, key: str) -> Optional[dict]:
        """
        Obter um objeto do bucket S3 especificado por chave

        Args:
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response
        
        except ClientError as e:
            print(f"[DEBUG] Erro ao obter objeto do S3: {e}")
            raise

    def create_presigned_post(self, bucket, object_name,
                            fields=None, conditions=None, expiration=3600):
        """
        Função para gerar uma URL pré-assinada para upload de um arquivo para o bucket S3
        
        Args:
            object_name (str): Nome do arquivo
            fields (dict): Campos de formulário para incluir na URL
            conditions (list): Condições de formulário para incluir na URL
            expiration (int): Tempo de expiração da URL em segundos
        
        Returns:
            dict: Dicionário contendo a URL pré-assinada e os campos de formulário necessários
        """

        # Generate a presigned S3 POST URL
        try:
            response = self.s3_client.generate_presigned_post(bucket,
                                                        object_name,
                                                        Fields=fields,
                                                        Conditions=conditions,
                                                        ExpiresIn=expiration)
        except ClientError as e:
            print(f"[DEBUG] Error generating presigned POST URL: {e}")

        # The response contains the presigned URL and required fields
        return response
    
    def upload_dir(self, bucket: str, key: str, dir_path: str):
        """
        Função para fazer upload de um diretório para o bucket S3

        Args:
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo no bucket
            dir_path (str): Caminho do diretório a ser enviado
        """
        try:
            # Upload do diretório para o bucket S3
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    key_path = os.path.join(key, file)
                    self.s3_client.upload_file(file_path, bucket, key_path)
            return True
        
        except ClientError as e:
            print(f"[DEBUG] Erro ao fazer upload do diretório para o S3: {e}")
            raise e 
    
    def download_all_files(self, bucket: str, prefix: str = '', sufix: str = '') -> list:
        """
        Realiza o download de todos os arquivos de um bucket S3, opcionalmente
        filtrando por um prefixo e/ou sufixo específico
        
        Args:
            bucket (str): Nome do bucket S3
            prefix (str, optional): Prefixo para filtrar os objetos. Defaults to ''.
            sufix (str, optional): Sufixo para filtrar os objetos. Defaults to ''.
        
        Returns:
            list: Lista com os caminhos locais dos arquivos baixados
        """
        downloaded_files = []
        
        try:
            # Lista todos os objetos no bucket com o prefixo especificado
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
            
            for page in page_iterator:
                if 'Contents' not in page:
                    print(f"[DEBUG] Nenhum arquivo encontrado no bucket {bucket} com prefixo {prefix}")
                    return downloaded_files
                    
                for obj in page['Contents']:
                    key = obj['Key']
                    # Ignora "pastas" (objetos que terminam com /)
                    if key.endswith('/'):
                        continue
                    
                    # Verifica se o arquivo termina com o sufixo especificado (se fornecido)
                    if sufix and not key.endswith(sufix):
                        continue
                        
                    # Cria diretórios locais se necessário                   
                    local_filepath = os.path.join(self.download_path, key)
                    os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
                    
                    # print(f"[DEBUG] Baixando {key} para {local_filepath}")
                    self.s3_client.download_file(bucket, key, local_filepath)
                    downloaded_files.append(local_filepath)
                    
            return downloaded_files
            
        except ClientError as e:
            print(f"[DEBUG] Erro ao fazer download de todos os arquivos do S3: {e}")
            raise e
        
    
    def list_files(self, bucket: str, prefix: str = '', sufix: str = '') -> list:
        """
        Lista todos os arquivos de um diretório no bucket S3, opcionalmente
        filtrando por um prefixo específico

        Args:
            bucket (str): Nome do bucket S3
            prefix (str, optional): Prefixo para filtrar os objetos. Defaults to ''.
            sufix (str, optional): Sufixo para filtrar os objetos. Defaults to ''.

        Returns:
            list: Lista com os nomes dos arquivos no bucket
        """
        files = []

        try:
            # Lista todos os objetos no bucket com o prefixo especificado
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

            for page in page_iterator:
                if 'Contents' not in page:
                    print(f"[DEBUG] Nenhum arquivo encontrado no bucket {bucket} com prefixo {prefix}")
                    return files
                
                for obj in page['Contents']:
                    key = obj['Key']
                    # Ignora "pastas" (objetos que terminam com /)
                    if key.endswith('/'):
                        continue

                    # Verifica se o arquivo termina com o sufixo especificado (se fornecido)
                    if sufix and not key.endswith(sufix):
                        continue
                    
                    files.append(key)

            return files

        except ClientError as e:
            print(f"[DEBUG] Erro ao listar arquivos do S3: {e}")
            raise e
        

    def get_file_size(self, bucket: str, key: str) -> float:
        """
        Obter o tamanho de um arquivo no bucket S3 em MB

        Args:
            bucket (str): Nome do bucket S3
            key (str): Nome do arquivo no bucket
            
        Returns:
            float: Tamanho do arquivo em MB
        """
        try:
            # Obter metadados do objeto para extrair o tamanho
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            size_bytes = response['ContentLength']
            
            # Converter bytes para MB (1 MB = 1024 * 1024 bytes)
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
        
        except ClientError as e:
            print(f"[DEBUG] Erro ao obter tamanho do arquivo do S3: {e}")
            raise e