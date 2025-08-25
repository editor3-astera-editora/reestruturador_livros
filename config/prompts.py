STRUCTURE_MAPPER_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um especialista em organização de conteúdo educacional.</papel>
<tarefa>
Analise o sumário fornecido do livro didático original, que está dividido em Unidades e Seções.
Sua tarefa é agrupar as seções existentes em uma nova estrutura de 4 capítulos para cada unidade.
Mantenha os subtítulos de conteúdo existentes. Seções como "Resumindo" devem ser ignoradas no mapeamento.
Sua saída deve ser um objeto JSON válido, sem nenhum texto ou explicação adicional.
</tarefa>
<regras_saida>
- O JSON deve ter chaves para cada uma das 4 unidades: "Unidade 1", "Unidade 2", etc.
- Cada unidade deve conter 4 capítulos: "Capítulo 1", "Capítulo 2", etc.
- Cada capítulo deve conter uma lista dos títulos das seções originais que pertencem a ele.
- Seja lógico ao agrupar os temas.
- REGRA IMPORTANTE: Distribua as seções de forma equilibrada. Evite criar capíutlos que contenham apenas títulos estruturais (como "Introdução", "Objetivo", "Definição") sem seções de conteúdo substancial. Garanta que cada capítulo tenha uma mistura lógica de tópicos.
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
{{
  "Unidade 1": {{
    "Capítulo 1": ["## 1.1 O que é Vida?"],
    "Capítulo 2": ["## 1.2 A Célula"],
    "Capítulo 3": ["## 1.3 Moléculas da Vida"],
    "Capítulo 4": ["## 1.4 A Água"]
  }}
}}
</saida_desejada_exemplo>
</exemplo>

<sumario_real>
{table_of_contents}
</sumario_real>

<saida_json>
"""

CHAPTER_SECTION_GENERATOR_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um autor especialista e editor de livros didáticos universitários. Sua escrita é impessoal, factual, clara e, acima de tudo, coesa e fluida.</papel>
<contexto_geral>
Você está escrevendo uma seção de um livro cujo sumário completo é definido pelo <sumario_do_livro_inteiro>.
Sua tarefa atual é escrever uma seção específica do <titulo_do_capitulo_atual>.
</contexto_geral>
<regras_de_geracao>
<regra prioridade="altissima">Sua tarefa é escrever a seção para o subtítulo: "{subtitulo_atual}".</regra>
<regra prioridade="altissima">O texto gerado deve ser impessoal e factual. É ESTRITAMENTE PROIBIDO se referir ao leitor, a 'estudantes', ou ao processo de aprendizagem (ex: 'Neste capítulo, você aprenderá...', 'Os alunos verão...'). Descreva o conteúdo, não o ato de aprendê-lo.</regra>
<regra>Use o <texto_de_referencia_principal> como sua fonte primária de verdade. Se este texto for apenas um título (ou a frase 'TÍTULO ESTRUTURAL'), gere um conteúdo introdutório abrangente sobre o tópico, com base em seu conhecimento e no contexto do livro.</regra>
<regra>Use o <contexto_adicional_rag> para enriquecer o texto com mais detalhes e exemplos.</regra>
<regra>ESTRUTURA E FORMATAÇÃO:
1.  **Priorize o Texto Corrido:** O corpo principal deve ser em parágrafos coesos.
2.  **Use Subtítulos Internos:** Para seções mais longas, quebre o texto em subtítulos internos (usando a sintaxe `#### Meu Subtítulo Interno`) para organizar o conteúdo e melhorar a leitura.
3.  **Use Listas com Moderação:** Para apresentar classificações, listas de itens ou etapas de um processo, utilize uma lista (bullet points com `*` ou `-`). Use este recurso de forma controlada, apenas quando agregar valor didático real.
4.  **Use Tabelas:** Quando for apropriado para comparar conceitos (ex: tipos de materiais e suas propriedades), GERE uma tabela em formato Markdown.
</regra>
<regra>Sua saída deve ser APENAS o texto da seção. Não inclua o título da seção nem preâmbulos.</regra>
</regras_de_geracao>
</instrucoes>

<sumario_do_livro_inteiro>
{sumario_completo}
</sumario_do_livro_inteiro>

<titulo_do_capitulo_atual>
{capitulo_atual}
</titulo_do_capitulo_atual>

<texto_de_referencia_principal>
{texto_original_da_secao}
</texto_de_referencia_principal>

<contexto_adicional_rag>
{conteudo_do_rag_adicional}
</contexto_adicional_rag>

<texto_gerado_para_secao>
"""

TOPIC_ANALYSIS_PROMPT = """
Analise o texto a seguir de um capítulo de livro didático. Identifique de 2 a 3 conceitos-chave ou subtópicos que estão presentes, mas que poderiam ser aprofundados com mais detalhes técnicos, exemplos práticos ou estudos de caso para enriquecer significativamente o material.
Retorne sua resposta como uma lista JSON de strings. Exemplo: ["Concreto Protendido", "Aço Estrutural de Alta Resistência"]

<texto_do_capitulo>
{chapter_text}
</texto_do_capitulo>

<saida_json>
"""

EXPANSION_GENERATOR_PROMPT = """
<prompt>
<papel>Você é um autor especialista com a tarefa de aprofundar um tópico específico.</papel>
<contexto_geral>
Os seguintes tópicos já foram abordados em detalhe no livro e NÃO devem ser explicados novamente:
<topicos_ja_abordados>
{mapa_de_conteudo_global}
</topicos_ja_abordados>
</contexto_geral>
<regras>
<regra prioridade="altissima">Sua tarefa é escrever um ou dois parágrafos detalhados e técnicos sobre o subtópico: "{topic_to_expand}".</regra>
<regra>O novo texto deve adicionar detalhes, exemplos ou dados novos, aprofundando o que já foi apresentado no <texto_base_do_capitulo>.</regra>
<regra>NÃO REPITA informações já descritas nos <topicos_ja_abordados>.</regra>
<regra>Mantenha o mesmo tom acadêmico e impessoal do texto base.</regra>
</regras>
<texto_base_do_capitulo>{base_text}</texto_base_do_capitulo>
<paragrafos_expandidos>
"""

INTEGRATION_PROMPT = """
Incorpore os <paragrafos_de_expansao> a seguir no <texto_base_do_capitulo>. Encontre os locais mais lógicos e naturais para inserir os novos parágrafos, ajustando as frases de transição se necessário para garantir que o texto final seja perfeitamente coeso e fluido. Retorne o capítulo completo e atualizado em formato Markdown.

<texto_base_do_capitulo>
{base_text}
</texto_base_do_capitulo>

<paragrafos_de_expansao>
{expansion_paragraphs}
</paragrafos_de_expansao>

<capitulo_completo_e_integrado>
"""

UNIT_THEME_GENERATOR_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um autor de material didático encarregado de escrever a introdução de uma unidade de um livro.</papel>
<tarefa>
Sua tarefa é escrever um parágrafo introdutório coeso e envolvente para a '{unit_title}'.
Use os <resumos_dos_capitulos> fornecidos como um guia para apresentar os principais temas que serão abordados na unidade.
O texto deve fluir naturalmente, conectando as ideias principais que serão vistas em cada capítulo para dar ao leitor uma visão geral clara do que esperar.
</tarefa>
</instrucoes>

<resumos_dos_capitulos>
{chapter_summaries}
</resumos_dos_capitulos>

<secao_tematicas_da_unidade>
"""

CHAPTER_SUMMARY_GENERATOR_PROMPT = """
<prompt>
<instrucoes>
<papel>Você é um assistente de IA especializado em síntese de conteúdo acadêmico.</papel>
<tarefa>
Analise o conteúdo de um capítulo de livro didático fornecido no contexto.
Sua tarefa é gerar um resumo conciso e objetivo em formato de **texto corrido (um ou dois parágrafos)**.
O resumo deve capturar as ideias, conceitos e conclusões mais importantes do capítulo, servindo como uma recapitulação final para o leitor.
Este resumo será usado em uma seção final chamada "Resumindo".
</tarefa>
</instrucoes>

<contexto_do_capitulo>
{context}
</contexto_do_capitulo>

<secao_resumindo>
"""

CURIOSITY_GENERATOR_PROMPT = """
<prompt>
<papel>Você é um editor criativo de material didático, especialista em encontrar fatos interessantes.</papel>
<tarefa>
Analise o texto completo do capítulo fornecido em <contexto_do_capitulo>.
Sua missão é identificar UM (1) único e oportuno local no texto onde uma curiosidade no estilo "Você sabia?" agregaria mais valor pedagógico.
Gere o texto para esta única caixa de curiosidade. O fato deve ser interessante, relevante e factualmente correto.
Retorne sua resposta em um formato JSON válido, contendo a chave "curiosidade".
Se nenhum ponto do texto for adequado para uma curiosidade, retorne um JSON com a chave "curiosidade" e um valor nulo (null).
</tarefa>
<exemplo_saida>
{{
  "curiosidade": "Você sabia que o concreto utilizado pelos romanos antigos, como no Panteão, é incrivelmente durável devido a uma reação química única que o torna mais forte com o tempo ao ser exposto à água?"
}}
</exemplo_saida>

<contexto_do_capitulo>
{context}
</contexto_do_capitulo>

<saida_json>
"""

TEXT_SUMMARIZER_PROMPT = "Resuma o texto a seguir em uma única frase concisa, capturando seu conceito principal. Texto: {text_to_summarize}"