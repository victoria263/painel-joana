# Painel da Joana (ADERE.AI) — pacote pra iterar no Fable / claude.ai/code

Painel de monitoramento das pacientes que a Joana acompanha por WhatsApp, pra Dra. Isabelle e Victoria.
Já vem construído e funcionando. Abra no claude.ai/code com o Fable 5 selecionado e itere a partir daqui.

## O que tem no pacote
- `index.html` — o PAINEL inteiro (frontend), single-file. Já RENDERIZA SOZINHO com dados de exemplo embutidos (modo demo), então é só abrir no navegador pra ver. Sem build, sem dependência.
- `backend/painel_api.py` — a API real (FastAPI) que alimenta o painel em tempo real a partir das conversas da Joana. É o que roda no servidor de produção.
- `backend/clinico.exemplo.json` — os fatos clínicos por paciente (marcos + ciclos). Em produção a Joana mantém esse arquivo.
- `PROMPT.md` — a especificação completa (contexto, telas, modelo de dados, critérios de aceite). Bom pra dar ao Fable como contexto.

## Como abrir agora (visual)
Abra o `index.html` no navegador. Ele vai mostrar o painel com as 4 pacientes de exemplo (modo demo). Clique numa paciente pra ver o mockup do WhatsApp + os marcos + os ciclos. A senha da tela de login é: `donna`.

## Como iterar no Fable / claude.ai/code
1. Suba a pasta no claude.ai/code (com o Fable 5 selecionado).
2. Peça as mudanças que quiser (mais marcos, outro visual, cores da ADERE, gráfico de evolução, etc.). O `index.html` é o arquivo do frontend; mexa nele.
3. O modo demo usa `SAMPLE_DATA` embutido no `index.html` — edite lá pra testar cenários.

## Como ligar na API ao vivo (produção)
- A API real está em `backend/painel_api.py` e serve tanto o painel (`/`) quanto os dados (`/api/patients`, `/api/patients/{telefone}`, `/api/stream`).
- Contrato: `GET /api/patients` devolve `{total, ativas, pacientes:[...]}`; cada paciente tem `{telefone, nome, foto, ativa, ultimaInteracao, mensagens:[{de,texto,hora}], marcos:{...}, ciclos:[...]}`.
- No `index.html`, a constante `API_BASE` no topo do script controla de onde vem o dado: vazia = mesma origem (produção); pra testar contra a API ao vivo de outro lugar, cole a URL do túnel ali. Se a API não responde, ele cai no modo demo automático.
- Quando o painel está servido pela própria API (mesma origem), ele já puxa o dado real da Joana em tempo real (atualiza a cada 15s).

## Observação
Alguns campos clínicos vêm como "a confirmar" — são os que só a Dra. Isabelle sabe (datas de consulta, medicação do ciclo 2 da Renata). Quando ela passar, entram no `clinico.json` e aparecem no painel na hora.
