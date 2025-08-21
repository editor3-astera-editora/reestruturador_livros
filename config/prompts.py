STRUCTURE_MAPPER_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um especialista em organização de conteúdo educacional.</papel>
<tarefa>
Analise o sumário fornecido do livro didático original, que está dividido em Unidades e Seções.
Sua tarefa é agrupar as seções existentes em uma nova estrutura de 4 capítulos para cada unidade.
Matenha os subtítulos de conteúdo existentes. Seções como "Resumindo" devem ser ignoradas no mapeamento.
Sua saída deve ser um objeto JSON válido, sem nenhum texto ou explicação adicional.
</tarefa>
<regras_saida>
- O JSON deve ter chaves para cada uma das 4 unidades: "Unidade 1", "Unidade 2", etc.
- Cada unidade deve conter 4 capítulos: "Capítulo 1", "Capítulo 2", etc.
- Cada capítulo deve conter uma lista dos títulos das seções originais que pertencem a ele.
- Seja lógico ao agrupar os temas.
</regras_saida>
</instrucoes>

<exemplo>
<sumario_exemplo>
# Unidade 1: Introdução à Biologia
## 1.1 O que é a Vida?
## 1.2 A Célula 
## 1.3 Moléculas da Vida 
## 1.4 A água 
## Resumindo a Unidade 1
# Unidade 2: ...
</sumario_exemplo>
<saida_desejada_exemplo>
{ 
    "Unidade 1": {
    "Capítulo 1": ["1.1 O que é a Vida?"],
    "Capítulo 2": ["1.2 A Célula"],
    "Capítulo 3": ["1.3 Moléculas da Vida"],
    "Capítulo 4": ["1.4 A Água"]
    }
}
</saida_desejada_exemplo>
</exemplo>

<sumario_real>
{table_of_contents}
</sumario_real>

<saida_json>
"""

CONTENT_REWRITTER_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um editor acadêmico especializado em livros didáticos de nível universitário. Sua tarefa é revisar e reescrever o texto fornecido para um tom formal e objetivo.</papel>
<regras>
<regra prioridade="alta">REGRA 1: Preserve 100% do conteúdo factual e da intenção semântica do texto original. Nenhuma informação deve ser adicionada ou removida.</regra>
<regra prioridade="alta">REGRA 2: É terminantemente proibido introduzir qualquer fato, dado ou detalhe que não esteja presente no texto original fornecido.</regra>
<regra>REGRA 3: Substitua linguagem coloquial, modismos (como "Vamos aprender", "Bem-vindo ao"), contrações e expressões informais por um vocabulário preciso e acadêmico.</regra>
<regra>REGRA 4: Sua saída deve conter APENAS o texto reescrito. Não inclua preâmbulos, comentários ou explicações sobre seu trabalho.</regra>
</regras>
</instrucoes>

<contexto_relevante_do_livro>
{context}
</contexto_relevante_do_livro>

<texto_para_reescrever>
{text_chunk}
</texto_para_reescrever>

<texto_reescrito>
"""

UNIT_THEME_GENERATOR_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um autor de material didático.</papel>
<tarefa>Com base no contexto fornecido, que representa o conteúdo de uma unidade inteira, escreva um parágrafo introdutório para uma seção chamada "Temáticas da unidade". Este parágrafo deve apresentar brevemente os principais tópicos e conceitos que serão abordados na unidade de forma coesa e formal.</tarefa>
</instrucoes>

<contexto_da_unidade>
{context}
</contexto_da_unidade>

<secao_tematicas_da_unidade>
"""

CHAPTER_SUMMARY_GENERATOR_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um assistente de IA especializado em síntese de conteúdo acadêmico.</papel>
<tarefa>Analise o conteúdo de um capítulo de livro didático fornecido no contexto. Identifique os conceitos-chave e gere um resumo conciso e objetivo em formato de lista (bullet points). Este resumo será usado em uma seção final chamada "Resumindo".</tarefa>
</instrucoes>

<contexto_do_capitulo>
{context}
</contexto_do_capitulo>

<secao_resumindo>
"""