# Estrutura de Tabelas do Sistema ChatRemar

Este documento detalha todas as tabelas utilizadas no sistema de chatbot da Associação Remar do Brasil, baseado na análise do workflow n8n em produção.

## 📊 Visão Geral

O sistema utiliza **2 tabelas principais** no Supabase PostgreSQL:

1. **`conversas`** - Gerencia estados e dados temporários das conversas
2. **`doacoes`** - Armazena dados completos das doações de itens

Além disso, o sistema utiliza:
- **Supabase Storage** - Para armazenamento de fotos das doações
- **Função RPC** - `get_ultima_doacao` para buscar a última doação de um usuário

---

## 📋 Tabela: `conversas`

### Propósito
Gerencia o estado atual da conversa de cada usuário e armazena dados temporários necessários para o fluxo do chatbot.

### Campos

| Campo | Tipo | Descrição | Obrigatório | Exemplo |
|-------|------|-----------|-------------|---------|
| `wa_id` | `text` ou `varchar` | WhatsApp ID do usuário (número de telefone sem formatação, com +). Usado como chave primária ou índice único. | ✅ Sim | `+5511999999999` |
| `estado` | `text` ou `varchar` | Estado atual da conversa no fluxo do chatbot. | ✅ Sim | `inicio`, `doacao`, `doacao_item_1`, etc. |
| `data` | `date` | Data da última interação (formato: YYYY-MM-DD). | ❌ Não | `2024-01-15` |
| `horario` | `time` ou `text` | Horário da última interação (formato: HH:MM:SS). | ❌ Não | `14:30:00` |
| `criado_em` | `timestamp` | Data e hora de criação do registro (formato ISO 8601). | ❌ Não | `2024-01-15T14:30:00` |

### Estados Possíveis (`estado`)

O campo `estado` pode conter os seguintes valores:

- **Estados Iniciais:**
  - `inicio` / `inicio0` - Estado inicial do chatbot

- **Estados de Doação:**
  - `doacao` - Menu de tipo de doação
  - `doacao_item_1` - Seleção de categoria do item
  - `doacao_item_2` - Estado/condição do item
  - `doacao_item_3` - Solicitação de nome completo
  - `doacao_item_4` - Confirmação de nome
  - `doacao_item_5` - Solicitação de endereço
  - `doacao_item_6` - Confirmação de endereço
  - `doacao_item_7` - Solicitação de WhatsApp
  - `doacao_item_8` - Confirmação de WhatsApp
  - `doacao_item_9` - Email, horário preferencial e fotos

- **Estados de Serviços:**
  - `acolhimento` - Fluxo de acolhimento
  - `lojas` - Fluxo de lojas solidárias
  - `servico` - Fluxo de serviços gerais
  - `fretes` - Fluxo de fretes e mudanças

### Operações Realizadas

1. **GET** - Buscar estado atual do usuário
   - Filtro: `wa_id = ?`
   - Retorna: Registro completo com estado atual

2. **INSERT** - Criar novo registro de conversa
   - Campos: `wa_id`, `estado`, `data`, `horario`, `criado_em`
   - Usado quando: Usuário inicia conversa pela primeira vez

3. **UPDATE** - Atualizar estado da conversa
   - Filtro: `wa_id = ?`
   - Campos atualizados: `estado`, `data`, `horario`
   - Usado quando: Transição de estado no fluxo

### Índices Recomendados

```sql
-- Índice único para busca rápida por wa_id
CREATE UNIQUE INDEX idx_conversas_wa_id ON conversas(wa_id);

-- Índice para busca por estado (se necessário para relatórios)
CREATE INDEX idx_conversas_estado ON conversas(estado);
```

### Exemplo de Registro

```json
{
  "wa_id": "+5511999999999",
  "estado": "doacao_item_3",
  "data": "2024-01-15",
  "horario": "14:30:00",
  "criado_em": "2024-01-15T14:30:00"
}
```

---

## 📋 Tabela: `doacoes`

### Propósito
Armazena dados completos das doações de itens realizadas pelos usuários, incluindo informações pessoais, detalhes do item e preferências de retirada.

### Campos

| Campo | Tipo | Descrição | Obrigatório | Valores Possíveis |
|-------|------|-----------|-------------|-------------------|
| `id` | `uuid` ou `serial` | Identificador único da doação (chave primária). | ✅ Sim | Auto-incremento ou UUID |
| `wa_id` | `text` ou `varchar` | WhatsApp ID do doador (número de telefone com +). | ✅ Sim | `+5511999999999` |
| `tipo_doacao` | `text` ou `varchar` | Categoria do item doado. | ✅ Sim | Ver valores abaixo |
| `estado_doacao` | `text` ou `varchar` | Condição/estado do item doado. | ✅ Sim | Ver valores abaixo |
| `nome_responsavel` | `text` ou `varchar` | Nome completo do responsável pela doação. | ✅ Sim | `João Silva` |
| `endereco_retirada` | `text` | Endereço completo para retirada do item. | ✅ Sim | `Rua Exemplo, 123, São Paulo - SP` |
| `telefone_whatsapp` | `text` ou `varchar` | Número de WhatsApp para contato (pode ser diferente do wa_id). | ✅ Sim | `+5511999999999` |
| `email` | `text` ou `varchar` | Email do responsável pela doação. | ❌ Não | `joao@example.com` |
| `horario_preferencial` | `text` ou `varchar` | Horário preferencial para retirada. | ❌ Não | `Manhã`, `Tarde`, `Noite` |
| `fotos` | `text` ou `jsonb` | URLs ou caminhos das fotos do item (armazenadas no Supabase Storage). | ❌ Não | Array de URLs ou JSON |
| `criado_em` | `timestamp` | Data e hora de criação do registro. | ❌ Não | `2024-01-15T14:30:00` |
| `atualizado_em` | `timestamp` | Data e hora da última atualização do registro. | ❌ Não | `2024-01-15T15:00:00` |

### Valores Possíveis

#### `tipo_doacao` (Categoria do Item)
- `Móveis`
- `Utensílios`
- `Eletroeletrônicos`
- `Roupas`
- `Itens variados`

#### `estado_doacao` (Condição do Item)
- `Novo`
- `Usado em bom estado`
- `Usado com marcas de uso`
- `Com defeito (ou misto: alguns bons, outros com defeito)`
- `Não sei dizer`

#### `horario_preferencial` (Horário de Retirada)
- `Manhã`
- `Tarde`
- `Noite`

### Operações Realizadas

1. **INSERT** - Criar nova doação
   - Campos iniciais: `wa_id`, `tipo_doacao`, `criado_em`, `atualizado_em`
   - Usado quando: Usuário inicia fluxo de doação de item

2. **UPDATE** - Atualizar dados da doação
   - Filtro: `id = ?`
   - Campos atualizados incrementalmente:
     - `estado_doacao` - Quando usuário informa condição do item
     - `nome_responsavel` - Quando usuário informa nome
     - `endereco_retirada` - Quando usuário informa endereço
     - `telefone_whatsapp` - Quando usuário informa telefone
     - `email` - Quando usuário informa email
     - `horario_preferencial` - Quando usuário informa horário
     - `fotos` - Quando usuário envia fotos
     - `atualizado_em` - Sempre que há atualização

### Fluxo de Preenchimento

A tabela `doacoes` é preenchida incrementalmente durante o fluxo de doação:

1. **Criação** (`doacao_item_1`): `wa_id`, `tipo_doacao`
2. **Estado** (`doacao_item_2`): `estado_doacao`
3. **Nome** (`doacao_item_3` → `doacao_item_4`): `nome_responsavel`
4. **Endereço** (`doacao_item_5` → `doacao_item_6`): `endereco_retirada`
5. **Telefone** (`doacao_item_7` → `doacao_item_8`): `telefone_whatsapp`
6. **Email** (`doacao_item_9`): `email`
7. **Horário** (`doacao_item_9`): `horario_preferencial`
8. **Fotos** (`doacao_item_9`): `fotos`

### Índices Recomendados

```sql
-- Índice primário (geralmente já existe)
-- PRIMARY KEY (id)

-- Índice para busca por wa_id
CREATE INDEX idx_doacoes_wa_id ON doacoes(wa_id);

-- Índice para busca por tipo_doacao (se necessário para relatórios)
CREATE INDEX idx_doacoes_tipo ON doacoes(tipo_doacao);

-- Índice para busca por data de criação (se necessário para relatórios)
CREATE INDEX idx_doacoes_criado_em ON doacoes(criado_em);
```

### Exemplo de Registro Completo

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "wa_id": "+5511999999999",
  "tipo_doacao": "Móveis",
  "estado_doacao": "Usado em bom estado",
  "nome_responsavel": "João Silva",
  "endereco_retirada": "Rua Exemplo, 123, Bairro Centro, São Paulo - SP, CEP 01234-567",
  "telefone_whatsapp": "+5511999999999",
  "email": "joao@example.com",
  "horario_preferencial": "Tarde",
  "fotos": [
    "https://xbmkmvwhvnrcysnyuygb.supabase.co/storage/v1/object/public/whatsapp_media/foto1.jpg",
    "https://xbmkmvwhvnrcysnyuygb.supabase.co/storage/v1/object/public/whatsapp_media/foto2.jpg"
  ],
  "criado_em": "2024-01-15T14:30:00",
  "atualizado_em": "2024-01-15T15:00:00"
}
```

---

## 🔗 Função RPC: `get_ultima_doacao`

### Propósito
Busca a última doação criada por um usuário específico, identificado pelo `wa_id`.

### Assinatura

```sql
CREATE OR REPLACE FUNCTION get_ultima_doacao(wa_id_param TEXT)
RETURNS TABLE (
  id UUID,  -- ou SERIAL, dependendo do tipo usado
  wa_id TEXT,
  tipo_doacao TEXT,
  estado_doacao TEXT,
  nome_responsavel TEXT,
  endereco_retirada TEXT,
  telefone_whatsapp TEXT,
  email TEXT,
  horario_preferencial TEXT,
  fotos TEXT,  -- ou JSONB
  criado_em TIMESTAMP,
  atualizado_em TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.id,
    d.wa_id,
    d.tipo_doacao,
    d.estado_doacao,
    d.nome_responsavel,
    d.endereco_retirada,
    d.telefone_whatsapp,
    d.email,
    d.horario_preferencial,
    d.fotos,
    d.criado_em,
    d.atualizado_em
  FROM doacoes d
  WHERE d.wa_id = wa_id_param
  ORDER BY d.criado_em DESC
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### Uso no n8n

A função é chamada via HTTP POST:

```
POST https://[SUPABASE_URL]/rest/v1/rpc/get_ultima_doacao
Headers:
  Content-Type: application/json
  apikey: [SUPABASE_KEY]
Body:
{
  "wa_id_param": "+5511999999999"
}
```

### Quando é Usada

A função é chamada em vários pontos do fluxo para recuperar a doação atual que está sendo preenchida:

- Após criar a doação inicial
- Antes de atualizar cada campo
- Para verificar se existe uma doação em andamento

---

## 📦 Supabase Storage

### Bucket: `whatsapp_media`

### Propósito
Armazena as fotos dos itens doados enviadas pelos usuários via WhatsApp.

### Estrutura

- **Bucket**: `whatsapp_media`
- **Formato de arquivo**: Qualquer formato de imagem (JPG, PNG, etc.)
- **Nomenclatura**: Definida pelo sistema (geralmente baseada em timestamp ou UUID)

### URL de Acesso

```
https://[SUPABASE_URL]/storage/v1/object/public/whatsapp_media/[nome_arquivo]
```

### Integração

As URLs das fotos são armazenadas no campo `fotos` da tabela `doacoes`, podendo ser:
- Um array de strings (URLs)
- Um campo JSONB com estrutura mais complexa
- Uma string separada por vírgulas

---

## 🔄 Relacionamentos

### Relacionamento entre Tabelas

```
conversas (wa_id) ──┐
                    │
                    ├──> (1:N) ──> doacoes (wa_id)
                    │
                    └──> Um usuário pode ter múltiplas doações
```

- **Cardinalidade**: 1 usuário (wa_id) : N doações
- **Chave de relacionamento**: `wa_id`
- **Tipo**: Relacionamento não formalizado (sem foreign key explícita)

### Fluxo de Dados

```
1. Usuário envia mensagem
   ↓
2. Sistema busca/atualiza `conversas` (estado atual)
   ↓
3. Se estado = doacao_item_*, sistema busca/atualiza `doacoes`
   ↓
4. Fotos são enviadas para Supabase Storage
   ↓
5. URLs das fotos são salvas em `doacoes.fotos`
```

---

## 📝 Scripts SQL de Criação

### Tabela `conversas`

```sql
CREATE TABLE IF NOT EXISTS conversas (
  wa_id VARCHAR(20) PRIMARY KEY,
  estado VARCHAR(50) NOT NULL,
  data DATE,
  horario TIME,
  criado_em TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_conversas_wa_id ON conversas(wa_id);
CREATE INDEX idx_conversas_estado ON conversas(estado);
```

### Tabela `doacoes`

```sql
CREATE TABLE IF NOT EXISTS doacoes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- ou SERIAL
  wa_id VARCHAR(20) NOT NULL,
  tipo_doacao VARCHAR(50) NOT NULL,
  estado_doacao VARCHAR(100),
  nome_responsavel VARCHAR(255),
  endereco_retirada TEXT,
  telefone_whatsapp VARCHAR(20),
  email VARCHAR(255),
  horario_preferencial VARCHAR(20),
  fotos TEXT,  -- ou JSONB para múltiplas fotos
  criado_em TIMESTAMP DEFAULT NOW(),
  atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_doacoes_wa_id ON doacoes(wa_id);
CREATE INDEX idx_doacoes_tipo ON doacoes(tipo_doacao);
CREATE INDEX idx_doacoes_criado_em ON doacoes(criado_em);
```

### Função RPC `get_ultima_doacao`

```sql
CREATE OR REPLACE FUNCTION get_ultima_doacao(wa_id_param TEXT)
RETURNS TABLE (
  id UUID,
  wa_id TEXT,
  tipo_doacao TEXT,
  estado_doacao TEXT,
  nome_responsavel TEXT,
  endereco_retirada TEXT,
  telefone_whatsapp TEXT,
  email TEXT,
  horario_preferencial TEXT,
  fotos TEXT,
  criado_em TIMESTAMP,
  atualizado_em TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.id,
    d.wa_id,
    d.tipo_doacao,
    d.estado_doacao,
    d.nome_responsavel,
    d.endereco_retirada,
    d.telefone_whatsapp,
    d.email,
    d.horario_preferencial,
    d.fotos,
    d.criado_em,
    d.atualizado_em
  FROM doacoes d
  WHERE d.wa_id = wa_id_param
  ORDER BY d.criado_em DESC
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

---

## 📊 Resumo das Operações

### Tabela `conversas`

| Operação | Frequência | Quando |
|----------|------------|--------|
| GET | Alta | A cada mensagem recebida |
| INSERT | Baixa | Primeira interação do usuário |
| UPDATE | Alta | A cada transição de estado |

### Tabela `doacoes`

| Operação | Frequência | Quando |
|----------|------------|--------|
| INSERT | Média | Início do fluxo de doação |
| UPDATE | Alta | A cada etapa do fluxo de doação |
| GET (via RPC) | Alta | Antes de cada atualização |

### Supabase Storage

| Operação | Frequência | Quando |
|----------|------------|--------|
| UPLOAD | Média | Quando usuário envia foto |
| GET (URL pública) | Baixa | Para visualização |

---

## ✅ Checklist de Implementação

- [ ] Criar tabela `conversas` com todos os campos
- [ ] Criar tabela `doacoes` com todos os campos
- [ ] Criar índices recomendados
- [ ] Criar função RPC `get_ultima_doacao`
- [ ] Criar bucket `whatsapp_media` no Supabase Storage
- [ ] Configurar políticas de acesso do Storage (público para leitura)
- [ ] Configurar Row Level Security (RLS) se necessário
- [ ] Testar todas as operações CRUD
- [ ] Validar tipos de dados e constraints

---

## 📚 Referências

- **Fonte**: Análise do workflow n8n em `docs/context/ChatRemar.json`
- **Banco de Dados**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Última Atualização**: Baseado na implementação atual do sistema
