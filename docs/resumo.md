O arquivo 
docs/ChatRemar.json
 descreve um fluxo de trabalho automatizado (workflow) construído na ferramenta n8n. Trata-se de um chatbot para WhatsApp projetado para a Associação Remar do Brasil, focado no atendimento ao público para doações e serviços assistenciais.

Aqui está uma análise detalhada do que o projeto faz:

1. Arquitetura e Integrações
Orquestrador: O fluxo é totalmente gerenciado pelo n8n, utilizando nós para lógica condicional (Switch, If) e transformações (Set).
WhatsApp API: Utiliza a MegaAPI (httpRequest nodes) para receber mensagens (via Webhook), enviar textos/menus e baixar arquivos de mídia (áudio, imagem, documentos).
Banco de Dados: Integração profunda com o Supabase. O bot usa o banco para gerenciar o "estado" da conversa (inicio, doacao, acolhimento, etc.) de cada usuário (identificado pelo wa_id). Isso permite que o bot lembre em que etapa o usuário parou.
2. Lógica de Funcionamento
O bot opera como uma máquina de estados, onde a resposta depende tanto da mensagem recebida quanto do histórico da conversa salvo no banco de dados.

Triagem Inicial: Ao receber uma mensagem, o sistema verifica se é de um usuário (ignora grupos) e consulta o Supabase para ver o status atual daquele número.
Comandos de Admin: Existem verificações para comandos específicos como /chat e /nochat, provavelmente para permitir intervenção humana ou resetar o fluxo.
3. Funcionalidades Principais (Menus)
O bot oferece um menu principal numerado com as seguintes vertentes:

Doações: Um fluxo complexo de coleta de dados. O usuário seleciona o tipo de item (Móveis, Roupas, Eletros, etc.) e o bot segue um roteiro passo-a-passo pedindo Nome, Endereço, Telefone, e até envio de fotos (doacao_item_8, doacao_item_9). Tudo isso é salvo na tabela doacoes.
Acolhimento: Opção para quem busca ajuda/abrigo.
Lojas Solidárias & Serviços: Informações sobre lojas e contratação de serviços da associação.
Fretes e Mudanças: Outra modalidade de serviço oferecida.
4. Regionalização
O fluxo possui uma lógica de roteamento geográfico, segmentando o atendimento por estados:

São Paulo (SP)
Rio de Janeiro (RJ)
Espírito Santo (ES)
Minas Gerais (MG)
Paraná (PR)
Considerações Técnicas
Não é IA Generativa: O projeto não utiliza inteligência artificial como ChatGPT ou OpenAI. Ele é estritamente baseado em regras (árvore de decisão), onde o usuário navega digitando números (1, 2, 3) ou palavras-chave predefinidas.
Multimídia: O bot está preparado para lidar com diferentes tipos de mensagens, incluindo áudio, imagens e documentos, fazendo o download desses arquivos através da API.
Em resumo, é um sistema robusto de autoatendimento estruturado, focado na triagem e coleta organizada de informações de doadores e beneficiários da Remar Brasil.