# amor

Aplicação Flask para publicar fotos usando o Storage do Supabase. As fotos são listadas diretamente do bucket do Supabase, então continuam aparecendo depois de deploys ou reinícios do Render.

## Variáveis de ambiente

Configure estas variáveis no Render antes de usar o upload:

- `SUPABASE_URL`: URL do projeto Supabase no formato `https://SEU_PROJECT_REF.supabase.co`.
  - Também é aceito informar apenas o `SEU_PROJECT_REF`; a aplicação completa a URL automaticamente.
- `SUPABASE_KEY`: chave do Supabase com permissão para enviar arquivos ao Storage.
- `SUPABASE_BUCKET`: nome do bucket do Storage. O padrão é `fotos`.
- `SECRET_KEY`: chave secreta do Flask para sessão.

Se aparecer o erro `Name or service not known`, normalmente a `SUPABASE_URL` está com o host errado ou incompleto. Copie a URL em **Project Settings > API > Project URL** no painel do Supabase e redeploy a aplicação.


## Persistência das fotos

O Render pode recriar o filesystem local em deploys e updates. Por isso, a aplicação não depende mais do SQLite local para descobrir quais fotos exibir: a página inicial e o painel administrativo consultam diretamente o bucket configurado em `SUPABASE_BUCKET`.
