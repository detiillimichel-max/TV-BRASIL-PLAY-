# Motor central de Rate Limit — TV-BRASIL-PLAY

**Política:** teto operacional de 40% da cota configurada para cada fonte, em cada janela (hora, dia e mês).

## O que foi implementado

- Registro central de fontes em `config/api-sources.json`.
- Motor compartilhado em `api/_lib/rate-limit.js`.
- Contadores persistentes e compartilhados via Upstash Redis REST.
- Endpoint protegido para reservar uma chamada: `POST /api/rate-limit/consume`.
- Endpoint de diagnóstico sem segredos: `GET /api/rate-limit/status`.
- Bloqueio seguro (fail-closed): sem Redis, sem quota configurada ou com fonte desativada, a chamada não deve seguir para o provedor.

## Fórmula

Para cada fonte e janela:

`limite_operacional = floor(cota_real_do_provedor × 0,40)`

Exemplo: se a cota oficial da fonte for 200 chamadas por hora, o motor permite no máximo 80 chamadas por hora. Os 60% restantes ficam reservados.

O limite precisa ser configurado com base na cota real da conta/plano. Quando o provedor não publica uma cota fixa, deve ser definido um teto interno conservador e identificado como tal; não se deve inventar uma cota oficial.

## Fontes registradas

O registro inicial inclui as APIs cujas variáveis foram identificadas no projeto e fontes públicas previstas: Pexels, Pixabay, Coverr, Vecteezy, Twitch, Vimeo, TMDB, NASA, NARA, DPLA, Wikimedia Commons, Internet Archive, NASA Image Library, Europeana e DVIDS. Jamendo e Audius aparecem apenas como referências externas: suas PWAs independentes não serão alteradas.

Os limites estão intencionalmente sem preenchimento e as fontes começam desativadas. Isso evita afirmar cotas desconhecidas ou fazer chamadas antes de validar os planos. Cada fonte só pode ser ativada depois de preencher suas cotas reais ou seus tetos internos aprovados.

## Variáveis necessárias na Vercel

Adicionar em **Project → Settings → Environment Variables**, somente para Production (e Preview se necessário):

- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `RATE_LIMIT_ADMIN_TOKEN`

As duas primeiras são fornecidas por uma instância Redis compatível com Upstash REST. A terceira deve ser um segredo aleatório forte, criado pelo proprietário. Nunca colocar esses valores no frontend, no GitHub público ou nesta documentação.

Para coletores GitHub Actions, adicionar os mesmos valores como GitHub Actions Secrets somente quando os coletores forem implementados e precisarem reservar chamadas pelo endpoint protegido.

## Como reservar uma chamada

Antes de chamar um provedor, o backend ou coletor deve reservar uma unidade:

`POST /api/rate-limit/consume`

Cabeçalho: `Authorization: Bearer <RATE_LIMIT_ADMIN_TOKEN>`

JSON: `{"source":"nasa"}`

Somente uma resposta `200` autoriza a chamada ao provedor. Respostas `409`, `429` ou `503` significam que a chamada externa deve ser bloqueada. Nunca ignorar erros do motor nem chamar o provedor como fallback.

## Importante sobre concorrência

Os contadores são persistidos no Redis compartilhado, não em memória da Function. O incremento é atômico; chamadas concorrentes que excedam o teto são recusadas antes de alcançar a API. O contador pode ultrapassar numericamente o teto por tentativas recusadas, mas essas tentativas não são encaminhadas ao provedor.

## Estado atual

O código do motor e o registro de fontes estão preparados, mas o bloqueio operacional só fica ativo depois de:
1. Criar/conectar o Redis compatível.
2. Configurar as três variáveis secretas na Vercel.
3. Preencher cotas reais/tetos internos no registro e ativar as fontes.
4. Integrar cada cliente de API para reservar uma chamada antes de acessar o provedor.
5. Integrar os coletores GitHub Actions ao endpoint protegido.

A criação destes arquivos não significa que as APIs existentes já estejam interceptadas. Até a integração de cada conector, não se deve considerar o teto de 40% garantido para ele.


## Integração do coletor NASA NAIL

O coletor foi dividido em duas partes:

- `scripts/collectors/nasa.py`: mapeador puro de metadados; não acessa a rede.
- `scripts/collectors/collect_nasa.py`: executor de coleta, com bloqueio por padrão.

### Proteções do executor

1. Sem `--allow-network`, o processo termina sem fazer chamadas externas.
2. Mesmo com `--allow-network`, exige `TVBRASIL_RATE_LIMIT_URL` e `RATE_LIMIT_ADMIN_TOKEN`.
3. Antes de cada consulta NASA, reserva uma chamada em `POST /api/rate-limit/consume` usando a fonte `nasa-image-library`.
4. Só consulta NASA depois de receber HTTP 200 e JSON com `ok: true`.
5. Se o endpoint estiver indisponível, a fonte estiver desativada, a quota estiver ausente ou o limite for atingido, a coleta é bloqueada. Não existe fallback direto.
6. Os resultados são gravados em `data/incoming/nasa_nail.json` e continuam com `rights_status: review_required`.

### Estado de ativação

A fonte `nasa-image-library` continua `enabled: false` e com limites nulos em `config/api-sources.json`. Portanto, mesmo que o executor seja iniciado manualmente, o motor central recusará a reserva. A coleta real permanece bloqueada.

**Não adicione ainda o executor ao workflow agendado.** Primeiro será necessário criar o Redis, configurar os segredos na Vercel e no GitHub Actions, confirmar o limite interno aprovado para NASA NAIL e ativar a fonte. O workflow atual executa somente os testes, a grade e a normalização.

### Execução futura (após ativação formal)

```bash
python scripts/collectors/collect_nasa.py --allow-network --query "earth" --page-size 10
```

Variáveis esperadas no ambiente seguro do GitHub Actions:

- `TVBRASIL_RATE_LIMIT_URL`: URL base da implantação Vercel do TV-BRASIL-PLAY.
- `RATE_LIMIT_ADMIN_TOKEN`: mesmo segredo configurado na Vercel; armazenar como GitHub Actions Secret.

O executor não precisa de `NASA_API_KEY`: utiliza a NASA Image and Video Library pública. Isso não significa quota ilimitada; o teto interno configurado no motor continua obrigatório.
