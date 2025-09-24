import os
import json

class PromptTemplate:
    """
    Classe para gerar um template de prompt genérico para análise de dados de conversas.
    Esta versão foi modificada para remover todas as informações sensíveis e de saúde.
    """

    def __init__(self, conversation_data, expected_output_format_path, session_id):
        """
        Inicializa a classe com os dados da conversa.
        
        Args:
            conversation_data (str): Dados da conversa do usuário.
            expected_output_format_path (str): Caminho para o arquivo de formato de saída esperado.
            session_id (str): Um identificador único para a sessão ou usuário.
        """
        # Armazena os dados da conversa e o ID da sessão.
        self.conversation_data = conversation_data
        self.session_id = session_id

        # Lê o arquivo de formato de saída esperado.
        try:
            with open(expected_output_format_path, 'r', encoding='utf-8') as file:
                expected_output_format = file.read()
        except FileNotFoundError:
            print(f"[WARNING] Arquivo de formato esperado não encontrado em: {expected_output_format_path}. Usando um placeholder genérico.")
            expected_output_format = "<!-- O formato de saída deve ser definido aqui. -->"

        # Cria o template do prompt com base nos dados fornecidos.
        self.create_prompt_template(expected_output_format)

    def create_prompt_template(self, expected_output_format):
        """
        Gera o prompt com um contexto e instruções generalizadas.

        Args:
            expected_output_format (str): O formato HTML esperado para a saída do modelo.

        Returns:
            str: O prompt formatado e pronto para ser enviado ao modelo.
        """

        # O prompt é construído usando f-strings para injetar os dados dinâmicos.
        # As tags <context>, <instructions>, etc., ajudam o modelo a entender a estrutura da tarefa.
        self.prompt = f"""
        <context>
            You are an expert analyst. Your task is to analyze conversation data from one or more interactions
            and produce a comprehensive and well-structured summary.
        </context>

        <instructions>
            1. Analyze the provided conversation data thoroughly.
            2. Produce ONE comprehensive summary of the conversation.
            3. The output format MUST be valid HTML and the summary must be enclosed in <html></html> tags.
            4. Include a professional assessment based on the conversation patterns and content.
            5. Focus on key topics, user sentiment, and potential action items.
            6. Use a proper HTML structure with headers (e.g., <h2>) and lists. Analysis in each section should ideally be in bullet points using <ul> and <li> tags.
            7. Be thorough but concise in your analysis.
            8. Include the following sections in this exact order:
               - Session Information: A summary of the session details.
               - Key Topics Discussed: Main subjects identified in the conversation.
               - Overall Sentiment: The general sentiment (e.g., Positive, Neutral, Negative) detected.
               - Action Items / Follow-ups: Any clear tasks or follow-ups mentioned.
            9. Create a separate section for data visualization with a placeholder:
               - Section "Data Visualization" with placeholder: {{{{VISUALIZATION_PLACEHOLDER_1}}}}
            10. Do NOT include any <img> tags or image URLs in your response. The placeholder will be replaced later.
            11. Maintain a professional and objective tone.
            12. The HTML title MUST be exactly: <head><title>Conversation Summary</title></head>
            13. Add a final section at the end titled "Conversation References".
            14. In the "Conversation References" section, create a well-formatted HTML table with the header "File Key".
        </instructions>

        <expected_output_format>
            {expected_output_format}
        </expected_output_format>
        
        <session_identifier>
            {self.session_id}
        </session_identifier>

        <conversation_data>
            {self.conversation_data}
        </conversation_data>
        """

        return self.prompt
    
    def get_prompt_text(self):
        """
        Retorna o texto do prompt formatado.

        Returns:
            str: O prompt completo como uma string.
        """
        return self.prompt
