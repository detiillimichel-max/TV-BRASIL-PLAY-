# TV-BRASIL-PLAY — Documentação Oficial do Projeto

> Documento mestre de identidade, escopo, arquitetura e desenvolvimento.  
> **Versão:** 1.0  
> **Data:** 03/11/2026  
> **Status:** Planejamento inicial — implementação ainda não iniciada.

---

## 1. Identidade do projeto

- **Nome:** TV-BRASIL-PLAY
- **Repositório:** https://github.com/detiillimichel-max/TV-BRASIL-PLAY-
- **Proprietário:** `detiillimichel-max`
- **Visibilidade:** Público
- **Branch principal:** `main`
- **Objetivo:** construir uma plataforma gratuita de televisão digital em formato PWA, com canais temáticos, programação contínua, catálogo audiovisual e integração de emissoras parceiras mediante autorização.

O TV-BRASIL-PLAY pretende oferecer uma experiência semelhante à de uma televisão: o usuário escolhe uma categoria ou canal, acompanha o conteúdo atual e pode continuar assistindo a uma sequência programada de conteúdos.

A plataforma deverá ser tecnicamente sustentável, leve para dispositivos Android, transparente quanto à origem dos conteúdos e responsável quanto a direitos autorais, licenças e condições de incorporação.

## 2. Separação obrigatória de projetos

O TV-BRASIL-PLAY é um projeto independente.

Existe outro projeto chamado **TV-BRASIL-ENGINE**:

- Repositório: https://github.com/detiillimichel-max/TV-BRASIL-ENGINE
- Possui uma biblioteca própria de 88 canais, Blob, catálogo, player e outras funcionalidades.

### Regras de isolamento

1. Não modificar, apagar, migrar, sobrescrever ou reorganizar arquivos do TV-BRASIL-ENGINE.
2. Não importar automaticamente a biblioteca de 88 canais.
3. Não compartilhar configurações, variáveis, armazenamento ou banco de dados entre os projetos sem uma decisão explícita futura.
4. Não tratar o ENGINE como dependência do PLAY.
5. Manter repositórios, deploys, credenciais e ciclos de desenvolvimento independentes.

As PWAs Jamendo e Audius existentes também devem permanecer independentes e não poderão ter seus repositórios ou instalações modificados por este projeto.

## 3. Categorias oficiais

A plataforma terá nove categorias principais, cada uma com identidade visual, catálogo, curadoria e organização próprios.

1. **Filmes**
2. **Séries**
3. **Desenhos**
4. **Música**
5. **Natureza & Vida**
6. **Espaço & Ciência**
7. **História & Documentários**
8. **Viagens & Culturas**
9. **Notícias & Emissoras Parceiras**

A presença de uma categoria na interface não significa que já exista conteúdo disponível nela. Cada catálogo será habilitado progressivamente, conforme fontes, licenças, compatibilidade e moderação forem validadas.

## 4. Fontes de conteúdo previstas

Fontes inicialmente selecionadas:

- Pexels
- Pixabay
- Internet Archive
- NASA
- Wikimedia Commons

### Áudio

- **Jamendo:** existe uma PWA de música funcional que poderá ser aberta ou integrada por mecanismo permitido, sem modificar seu projeto independente.
- **Coverr:** já existe experiência anterior com integração e conteúdo de áudio; qualquer uso no PLAY deverá ser validado conforme a API e as condições vigentes.
- **Audius:** preservar a PWA existente. Não modificar seu repositório nem sua instalação.

### Regras para integração de fontes

- Respeitar termos de uso, licenças, atribuições, limites de requisição e políticas de cada provedor.
- Não presumir que todo conteúdo de uma plataforma é livre para redistribuição.
- Distinguir claramente conteúdo incorporado, conteúdo disponibilizado por API e conteúdo efetivamente hospedado pela plataforma.
- Não armazenar cópias de mídia quando não houver necessidade e autorização.
- Registrar a origem e os dados de licença de cada item.
- Tratar URLs externas como referências sujeitas a expiração, indisponibilidade e alteração de políticas.

## 5. Conceito de canais e programação contínua

O objetivo é oferecer canais temáticos com experiência semelhante à televisão.

Funcionalidades planejadas:

- Reprodução contínua de uma sequência de vídeos.
- Avanço automático para o próximo item.
- Programação organizada por horários.
- Identificação do conteúdo atual e do próximo.
- Catálogo acumulativo.
- Curadoria e moderação antes da publicação.
- Player unificado, respeitando os formatos e players permitidos pelas fontes.
- Experiência otimizada para Android.

### Modelo de programação

A primeira implementação poderá usar uma **grade virtual baseada em horários**. O sistema calcula qual item deveria estar em exibição de acordo com a programação cadastrada e o horário de referência.

Isso permite que usuários diferentes iniciem a reprodução em momentos diferentes e encontrem o item correspondente à mesma grade.

A grade virtual não equivale, por si só, a uma transmissão linear sincronizada. A plataforma só deverá afirmar que oferece transmissão ao vivo ou linear sincronizada quando houver infraestrutura e operação técnica que realmente forneçam esse serviço.

A programação deverá prever:
- Fuso horário definido e documentado.
- Duração e ordem dos itens.
- Tratamento de falhas e itens indisponíveis.
- Regras de repetição e preenchimento de lacunas.
- Identificação de conteúdo ao vivo, gravado ou programado.

## 6. Emissoras parceiras autorizadas

A plataforma poderá incorporar emissoras que autorizem expressamente a utilização de seus players em nosso PWA.

Exemplo de funcionamento pretendido:

1. Uma emissora parceira possui uma transmissão de jornal às 19h.
2. A grade do TV-BRASIL-PLAY contém uma janela de programação autorizada para essa transmissão.
3. No horário previsto, o aplicativo apresenta o player oficial, desde que a incorporação esteja permitida e disponível.
4. Ao fim da janela, a plataforma retorna à programação própria, conforme a grade cadastrada.

A troca automática só poderá ocorrer se o player e as condições técnicas e jurídicas da emissora permitirem esse comportamento.

### Cadastro obrigatório de cada parceira

- Nome da emissora.
- Site oficial.
- URL do player oficial.
- Tipo de incorporação permitida.
- Documento ou termo de autorização.
- Responsável pela autorização.
- Território permitido.
- Horários de programação.
- Data de validade da autorização.
- Condições e restrições de uso.

### Regras de transmissão

- Não extrair, copiar, retransmitir ou hospedar sinais sem autorização.
- Não utilizar URLs HLS de terceiros sem verificar direitos e condições.
- Não contornar DRM, geobloqueios, autenticação ou controles técnicos.
- Não remover marcas, créditos ou avisos.
- Respeitar integralmente as limitações territoriais, temporais e técnicas da autorização.
- Manter registro verificável da autorização e de sua validade.
- Suspender a incorporação quando a autorização expirar, for revogada ou ficar sob dúvida relevante.

## 7. Regra comercial para emissoras parceiras

É proibido inserir anúncios próprios durante os programas das emissoras parceiras.

Devem ser preservados integralmente:

- Player original.
- Marca e identidade visual da emissora.
- Anúncios existentes no player original.
- Créditos e atribuições.
- Restrições e condições da autorização.

O TV-BRASIL-PLAY não deverá bloquear, substituir, sobrepor ou modificar anúncios do player parceiro.

A monetização futura poderá ser avaliada somente nos espaços de programação própria e quando as licenças e demais condições aplicáveis permitirem.

## 8. Arquitetura técnica pretendida

A arquitetura abaixo é uma proposta inicial, ainda sujeita à validação por etapas.

| Componente | Responsabilidade prevista |
|---|---|
| GitHub Pages | Hospedagem do frontend PWA |
| Vercel Functions | Backend e integração segura com APIs |
| Vercel Blob | Armazenamento seletivo de metadados, catálogos e programação, se adequado |
| APIs externas | Descoberta e obtenção de metadados e referências de conteúdo |
| Player | Reprodução de conteúdos e players autorizados |
| Service Worker | Cache do aplicativo e recursos estáticos |
| Web App Manifest | Instalação e identificação da PWA no Android |

### Princípios de arquitetura

- Manter o frontend sem segredos ou chaves privadas.
- Encaminhar chamadas que exigem credenciais pelo backend.
- Armazenar preferencialmente metadados, referências, capas permitidas e programação.
- Evitar armazenar arquivos de vídeo desnecessariamente no Blob.
- Implementar cache com validade e limites claros.
- Considerar custos de armazenamento, requisições, execução e tráfego antes de ampliar a operação.
- Prever tratamento de erros, indisponibilidade de provedores e limites de API.
- Não escolher serviços pagos ou recursos de alto consumo sem avaliar alternativas e limites gratuitos.

A decisão final sobre Blob, estrutura de dados e serviços será tomada após validar o volume e a natureza dos dados. Blob não deve ser tratado automaticamente como banco de dados relacional.

## 9. Curadoria, direitos e moderação

Nenhum conteúdo deverá entrar no catálogo público sem passar por validação.

### Verificações mínimas

1. Origem e identificação do item.
2. Licença e permissão de uso.
3. Possibilidade de incorporação ou reprodução.
4. Atribuição e créditos exigidos.
5. Classificação indicativa ou adequação etária.
6. Presença de conteúdo impróprio.
7. Duplicidade.
8. Disponibilidade da URL.
9. Compatibilidade com Android e navegadores suportados.
10. Restrições geográficas, temporais ou técnicas.

### Estados editoriais recomendados

- **Pendente:** ainda não analisado.
- **Em revisão:** em processo de validação.
- **Aprovado:** verificações concluídas e uso permitido dentro das condições registradas.
- **Rejeitado:** não atende aos critérios.
- **Suspenso:** anteriormente aprovado, mas indisponível ou sob reavaliação.

Conteúdo sem direitos verificáveis não poderá ser apresentado como autorizado. A ausência de informação sobre licença não significa permissão de uso.

A moderação automatizada poderá auxiliar a triagem, mas não substituirá a verificação de direitos nem deverá ser a única proteção contra conteúdo impróprio.

## 10. Experiência visual e acessibilidade

Direção visual planejada:

- Tema escuro premium.
- Destaques verdes.
- Ícones Lucide.
- Cards com capas.
- Carrosséis horizontais.
- Player em posição de destaque.
- Navegação simples.
- Layout responsivo.
- Barra inferior compatível com áreas seguras do Android.
- PWA instalável.
- Interface leve e econômica em dados.

A interface deverá manter boa legibilidade, controles acessíveis, estados de carregamento e mensagens claras para falhas de reprodução.

## 11. Estrutura inicial de diretórios proposta

A estrutura será criada gradualmente. A lista abaixo é uma referência de organização, não uma declaração de arquivos já existentes.

```text
TV-BRASIL-PLAY-/
├── index.html
├── manifest.json
├── sw.js
├── README.md
├── DOCUMENTACAO-OFICIAL.md
├── assets/
│   ├── icons/
│   └── covers/
├── css/
│   └── style.css
├── js/
│   ├── app.js
│   ├── navigation.js
│   ├── player.js
│   ├── catalog.js
│   ├── schedule.js
│   └── moderation.js
├── data/
│   └── categories.json
└── api/
    ├── catalog/
    ├── schedule/
    └── sources/
```

A estrutura de backend poderá exigir organização própria no projeto Vercel. O diretório `api/` acima é uma referência conceitual e deverá ser adaptado à configuração real de deploy, sem presumir que funções serverless serão executadas pelo GitHub Pages.

## 12. Plano de desenvolvimento por etapas

O projeto será implementado em pequenas entregas. Cada etapa deverá ser testada antes de avançar.

| Etapa | Entrega | Critério de validação |
|---|---|---|
| 1 | Auditoria e documentação | Repositório e escopo confirmados |
| 2 | Estrutura inicial e interface | Página abre e navega no Android |
| 3 | Manifest e Service Worker | PWA instalável e cache funcional |
| 4 | Nove categorias | Navegação e identidade de cada categoria |
| 5 | Player unificado | Reprodução e tratamento de erros |
| 6 | Fontes e catálogo | Itens identificados e validados |
| 7 | Backend e armazenamento | Integrações seguras e custos avaliados |
| 8 | Curadoria e moderação | Fluxo editorial testado |
| 9 | Programação automática | Grade virtual calculada corretamente |
| 10 | Emissoras parceiras | Incorporação autorizada e controles de validade |

Não implementar todas as etapas de uma vez. Cada entrega deve preservar o que já funciona.

## 13. Condições de desenvolvimento

O desenvolvimento será conduzido principalmente por um celular Android, sem depender de computador.

Diretrizes operacionais:

- Priorizar operações possíveis diretamente pelo GitHub no navegador.
- Fornecer instruções curtas, numeradas e adequadas ao celular.
- Evitar exigir terminal ou computador.
- Evitar edição manual de muitos arquivos pelo usuário.
- Auditar o estado atual do repositório antes de cada alteração relevante.
- Não afirmar que arquivos foram criados, publicados ou testados sem confirmação.
- Evitar mudanças desnecessárias que consumam créditos, armazenamento ou recursos.
- Fazer alterações pequenas, rastreáveis e com mensagens de commit claras.
- Testar cada etapa no Android.

## 14. Estado inicial confirmado

Na auditoria inicial de 03/11/2026, foi confirmado:

- Repositório público: `detiillimichel-max/TV-BRASIL-PLAY-`.
- Branch principal: `main`.
- Permissões de leitura e escrita disponíveis pela integração conectada.
- Um commit inicial na branch principal.
- Apenas `README.md` na raiz naquele momento.
- README com a identificação resumida do projeto.
- Nenhuma implementação funcional do aplicativo identificada na auditoria inicial.

O estado do repositório poderá mudar com novos commits. Antes de qualquer intervenção futura, consultar novamente a branch e os arquivos existentes.

## 15. Decisões ainda pendentes

As decisões abaixo deverão ser tomadas com base em testes e evidências, não por suposição:

- Modelo definitivo de catálogo e persistência.
- Política e duração de cache por tipo de dado.
- Provedores e limites de API efetivamente disponíveis.
- Formatos de mídia suportados pelo player.
- Estratégia de fallback para URLs indisponíveis.
- Modelo de sincronização e cálculo da grade virtual.
- Processo de recebimento e validação de autorizações de emissoras.
- Regras de classificação indicativa e política editorial.
- Custos e limites operacionais dos serviços escolhidos.
- Estratégia de monitoramento e manutenção.

## 16. Diretriz principal

Construir uma televisão digital própria, gratuita e organizada, com conteúdo de diversas fontes e emissoras parceiras autorizadas.

O TV-BRASIL-PLAY deverá ser:

- Tecnicamente sustentável.
- Juridicamente responsável.
- Leve para o usuário.
- Compatível com Android.
- Transparente sobre origem, licença e tipo de reprodução.
- Preparado para crescer sem misturar projetos independentes.

**Princípio de execução:** primeiro documentar, depois construir a base, testar no Android e somente então integrar fontes, programação e parceiros.
