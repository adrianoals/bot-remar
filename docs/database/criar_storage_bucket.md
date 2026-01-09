# Como Criar o Bucket `whatsapp_media` no Supabase Storage

Este guia explica como criar o bucket de Storage para armazenar as fotos dos itens doados.

## 📋 Método 1: Via Dashboard do Supabase (Recomendado)

### Passo a Passo

1. **Acesse o Dashboard do Supabase**
   - Vá para [https://app.supabase.com](https://app.supabase.com)
   - Faça login na sua conta
   - Selecione o projeto correto

2. **Navegue até Storage**
   - No menu lateral esquerdo, clique em **"Storage"**
   - Você verá a lista de buckets existentes

3. **Criar Novo Bucket**
   - Clique no botão **"New bucket"** ou **"Create a new bucket"**
   - Preencha os seguintes dados:
     - **Name**: `whatsapp_media`
     - **Public bucket**: ✅ **SIM** (marcar como público)
       - Isso permite acesso público às URLs das imagens
     - **File size limit**: `10485760` (10 MB) ou ajuste conforme necessário
     - **Allowed MIME types**: 
       - Opção 1: Deixe vazio para aceitar qualquer tipo
       - Opção 2: Selecione apenas tipos de imagem:
         - `image/jpeg`
         - `image/png`
         - `image/jpg`
         - `image/webp`
         - `image/gif`

4. **Salvar**
   - Clique em **"Create bucket"** ou **"Save"**

5. **Configurar Políticas de Acesso (Opcional mas Recomendado)**

   Após criar o bucket, você precisa configurar as políticas de acesso:

   - Clique no bucket `whatsapp_media`
   - Vá para a aba **"Policies"** ou **"Policies & RLS"**
   - Clique em **"New Policy"** ou use o editor de políticas

   **Política para Leitura Pública (SELECT):**
   ```sql
   -- Permitir leitura pública de todos os arquivos
   CREATE POLICY "Public Access"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'whatsapp_media');
   ```

   **Política para Upload (INSERT) - Apenas autenticados:**
   ```sql
   -- Permitir upload apenas com autenticação (service_role key)
   CREATE POLICY "Authenticated users can upload"
   ON storage.objects FOR INSERT
   WITH CHECK (
     bucket_id = 'whatsapp_media' 
     AND auth.role() = 'authenticated'
   );
   ```

   **Política para Deletar (DELETE) - Apenas autenticados:**
   ```sql
   -- Permitir deleção apenas com autenticação
   CREATE POLICY "Authenticated users can delete"
   ON storage.objects FOR DELETE
   USING (
     bucket_id = 'whatsapp_media' 
     AND auth.role() = 'authenticated'
   );
   ```

   **OU use a política mais simples (se você usar service_role key na aplicação):**
   ```sql
   -- Política que permite tudo para service_role
   CREATE POLICY "Service role full access"
   ON storage.objects FOR ALL
   USING (bucket_id = 'whatsapp_media')
   WITH CHECK (bucket_id = 'whatsapp_media');
   ```

---

## 📋 Método 2: Via SQL Editor (Alternativo)

Se você preferir criar via SQL, pode usar o SQL Editor do Supabase:

1. **Acesse o SQL Editor**
   - No Dashboard, clique em **"SQL Editor"** no menu lateral
   - Clique em **"New query"**

2. **Execute o seguinte SQL:**

```sql
-- Criar o bucket whatsapp_media
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'whatsapp_media',
    'whatsapp_media',
    true,  -- Bucket público
    10485760,  -- 10MB em bytes (ajuste conforme necessário)
    ARRAY['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'image/gif']  -- Tipos permitidos
)
ON CONFLICT (id) DO NOTHING;

-- Criar política para leitura pública
CREATE POLICY IF NOT EXISTS "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'whatsapp_media');

-- Criar política para upload (apenas autenticados)
CREATE POLICY IF NOT EXISTS "Authenticated users can upload"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'whatsapp_media' 
    AND auth.role() = 'authenticated'
);

-- Criar política para deleção (apenas autenticados)
CREATE POLICY IF NOT EXISTS "Authenticated users can delete"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'whatsapp_media' 
    AND auth.role() = 'authenticated'
);
```

**Nota:** Este método pode não funcionar em todos os projetos Supabase, dependendo das permissões. Se der erro, use o Método 1 (Dashboard).

---

## 📋 Método 3: Via API REST (Programático)

Se você quiser criar via código, pode usar a API REST do Supabase:

### Exemplo em Python

```python
import requests

# Configurações
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "sua-service-role-key"

# Headers
headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

# Criar bucket
bucket_data = {
    "id": "whatsapp_media",
    "name": "whatsapp_media",
    "public": True,
    "file_size_limit": 10485760,  # 10MB
    "allowed_mime_types": [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/webp",
        "image/gif"
    ]
}

response = requests.post(
    f"{SUPABASE_URL}/storage/v1/bucket",
    headers=headers,
    json=bucket_data
)

if response.status_code == 200:
    print("Bucket criado com sucesso!")
else:
    print(f"Erro: {response.status_code} - {response.text}")
```

### Exemplo em JavaScript/TypeScript

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://seu-projeto.supabase.co'
const supabaseServiceKey = 'sua-service-role-key'

const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
})

// Criar bucket
const { data, error } = await supabase.storage.createBucket('whatsapp_media', {
  public: true,
  fileSizeLimit: 10485760, // 10MB
  allowedMimeTypes: [
    'image/jpeg',
    'image/png',
    'image/jpg',
    'image/webp',
    'image/gif'
  ]
})

if (error) {
  console.error('Erro ao criar bucket:', error)
} else {
  console.log('Bucket criado com sucesso!', data)
}
```

---

## ✅ Verificação

Após criar o bucket, verifique se está funcionando:

1. **No Dashboard:**
   - Vá em **Storage**
   - Você deve ver o bucket `whatsapp_media` na lista

2. **Teste de Upload:**
   - Clique no bucket
   - Tente fazer upload de uma imagem de teste
   - Verifique se a URL pública está funcionando

3. **URL de Acesso:**
   - A URL pública seguirá o formato:
   ```
   https://[seu-projeto].supabase.co/storage/v1/object/public/whatsapp_media/[nome-do-arquivo]
   ```

---

## 🔒 Configurações de Segurança Recomendadas

### Opção 1: Bucket Público (Recomendado para este caso)

- ✅ **Public bucket**: `true`
- ✅ **Política de leitura**: Pública (qualquer um pode ver)
- ✅ **Política de upload**: Apenas autenticados (service_role key)
- ✅ **Política de deleção**: Apenas autenticados (service_role key)

**Vantagens:**
- URLs simples e diretas
- Não precisa de autenticação para visualizar imagens
- Ideal para fotos de doações que serão compartilhadas

### Opção 2: Bucket Privado (Mais Seguro)

- ❌ **Public bucket**: `false`
- ✅ **Política de leitura**: Apenas autenticados
- ✅ **Política de upload**: Apenas autenticados
- ✅ **Política de deleção**: Apenas autenticados

**Vantagens:**
- Mais seguro
- Controle total sobre quem acessa

**Desvantagens:**
- URLs precisam de token de autenticação
- Mais complexo para implementar

---

## 📝 Notas Importantes

1. **Service Role Key**: Para uploads via aplicação, você precisará usar a `service_role` key (não a `anon` key), pois ela tem permissões completas.

2. **Tamanho de Arquivo**: O limite padrão do Supabase é 50MB, mas você pode ajustar. Para fotos de WhatsApp, 10MB geralmente é suficiente.

3. **MIME Types**: Se você deixar vazio, aceitará qualquer tipo de arquivo. É recomendado especificar apenas tipos de imagem para segurança.

4. **CORS**: Se você precisar acessar as imagens de um frontend, pode ser necessário configurar CORS no Supabase.

---

## 🚨 Troubleshooting

### Erro: "Bucket already exists"
- O bucket já existe. Você pode ignorar ou deletar e recriar.

### Erro: "Permission denied"
- Verifique se está usando a `service_role` key (não a `anon` key).
- Verifique as políticas de acesso do bucket.

### Erro: "File size too large"
- Ajuste o `file_size_limit` do bucket.
- Verifique o tamanho do arquivo que está tentando fazer upload.

### URLs não funcionam
- Verifique se o bucket está marcado como público.
- Verifique se a política de leitura está configurada corretamente.
- Verifique se o nome do arquivo está correto na URL.

---

## 📚 Referências

- [Documentação do Supabase Storage](https://supabase.com/docs/guides/storage)
- [Políticas de Storage](https://supabase.com/docs/guides/storage/security/access-control)
- [API de Storage](https://supabase.com/docs/reference/javascript/storage-createbucket)
