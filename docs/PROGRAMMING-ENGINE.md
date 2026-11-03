# Motor de programação e catálogos

## Objetivo

A programação oficial é gerada pelo GitHub Actions, independentemente de usuários conectados. O aplicativo consulta arquivos publicados; ele não inicia coletas nas APIs de origem.

## Arquivos iniciais

- `config/programming.yml`: templates semanais, fuso `America/Sao_Paulo`, horários e seletores de conteúdo.
- `config/catalog-policy.yml`: regras de normalização, deduplicação e revisão de direitos.
- `scripts/build_schedule.py`: gera a grade contínua dos próximos sete dias e valida lacunas/sobreposições.
- `scripts/normalize_catalog.py`: normaliza arquivos JSON em `data/incoming/`, separa aprovados de itens para revisão.
- `.github/workflows/build-programming.yml`: execução agendada diária às 00:15 de São Paulo e execução manual; publica artefato de diagnóstico por sete dias.

## Regras da grade

- Segunda a sexta usam o template `weekdays`.
- Sábado usa `saturday`.
- Domingo usa `sunday`.
- Cada template precisa cobrir exatamente 00:00–24:00, sem lacunas nem sobreposições.
- Cada bloco contém horário local e UTC, categoria, seletor e modo de reprodução contínua.
- A grade é calculada para sete dias, sem depender de abertura do PWA.

## Regras do catálogo

O catálogo comum usa IDs `fonte:id` e campos normalizados para título, criador, categoria, tipo de mídia, URLs, duração, licença e estado de direitos.

Nenhum item recebe autorização de reprodução por simplesmente existir em uma API. O estado padrão é `review_required`. Apenas itens com direitos validados (`verified`, `public_domain` ou `partner_authorized`) podem entrar no catálogo aprovado. Os demais ficam no arquivo de revisão.

## Segurança de coleta

Os conectores de provedores ainda não estão habilitados. Antes de ativá-los:
1. Confirmar cotas oficiais ou limites internos conservadores por fonte.
2. Configurar o limitador central com Redis e credenciais de administração.
3. Fazer cada requisição do GitHub Actions reservar consumo no limitador antes de chamar o provedor.
4. Validar termos, licença e disponibilidade do conteúdo.
5. Publicar snapshots no Vercel Blob usando token privado em GitHub Actions Secrets.

As variáveis Jamendo e Audius já estão cadastradas no Vercel, mas isso não ativa coleta por si só.

## Estado atual

Esta etapa implementa a configuração semanal, o gerador da grade, o normalizador e o workflow agendado. O workflow, nesta primeira versão, guarda os resultados como artefato do GitHub Actions. A publicação no Blob e a coleta real das APIs ficam bloqueadas até configurar os segredos e limites necessários; não há alegação de catálogo preenchido nem de transmissão ativa.
