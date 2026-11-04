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


## NASA NAIL — executor protegido

- `nasa.py` transforma metadados sem rede.
- `collect_nasa.py` é o executor; bloqueia por padrão e exige `--allow-network`.
- Mesmo com a opção explícita, precisa reservar a chamada no motor central usando a fonte `nasa-image-library`.
- A fonte permanece desativada e sem quota até configuração formal. Portanto, não há coleta real neste estágio.
- Não incluir o executor em workflows agendados antes de Redis, segredos e quota interna aprovada.
