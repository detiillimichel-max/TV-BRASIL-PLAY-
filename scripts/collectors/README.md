# Collectors

Cada fonte terá seu próprio módulo Python nesta pasta.

## Contrato de segurança

- O coletor transforma metadados em registros compatíveis com `config/catalog-item.schema.json`.
- Nenhum coletor pode marcar conteúdo como aprovado apenas por vir de uma API pública.
- Direitos não comprovados devem permanecer como `review_required`.
- Chamadas de rede só serão habilitadas depois da integração obrigatória com o motor central de limites (40% da quota do provedor).
- Segredos nunca entram no código, nos arquivos JSON de entrada ou nos artefatos públicos.
- O coletor não baixa nem re-hospeda arquivos de mídia.

## NASA Image and Video Library

`nasa.py` é, nesta etapa, somente um mapeador de respostas da NASA NAIL API. Não realiza chamadas HTTP. Os registros ficam em revisão jurídica/editorial até a verificação individual dos direitos.
