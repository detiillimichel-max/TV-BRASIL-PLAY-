# Entrada dos coletores

Esta pasta recebe arquivos JSON gerados pelos coletores do TV-BRASIL-PLAY.

## Regras

- Um arquivo por fonte e execução, por exemplo `nasa-library-2026-11-04.json`.
- O arquivo deve conter um objeto com a propriedade `items`, que é uma lista de registros.
- Não inserir chaves, tokens ou outros segredos nos arquivos.
- Não considerar um conteúdo autorizado apenas porque a API o disponibilizou.
- Usar `rights_status: "review_required"` quando a licença e os direitos não estiverem comprovados.
- Somente `verified`, `public_domain` ou `partner_authorized` podem seguir para o catálogo aprovado, após evidência verificável.
- Não colocar vídeos de terceiros ou links de reprodução protegidos sem autorização.

O normalizador lê automaticamente os arquivos `*.json` desta pasta. Arquivos de documentação não são processados.
