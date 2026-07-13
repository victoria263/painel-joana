# PROMPT — Painel de Monitoramento da Joana (ADERE.AI) — para construir com o Fable

CONTEXTO
Construa um painel web de monitoramento de pacientes para a ADERE.AI. A Joana é uma assistente virtual (IA) que acompanha, pelo WhatsApp, as pacientes da Dra. Isabelle (reposição hormonal / TRH). O painel é usado por DUAS pessoas: a Dra. Isabelle (médica) e a Victoria (gestora). Objetivo: ver rapidamente todas as pacientes que a Joana gerencia, o status de cada uma, o histórico da conversa e os marcos clínicos e de acompanhamento.

TOM E MARCA
Ferramenta clínica, porém humana e acolhedora (a ADERE.AI é sobre devolver tempo e cuidado humano). Visual limpo, moderno, profissional, com um toque caloroso. São dados sensíveis de saúde: incluir uma tela de login simples (só Isabelle e Victoria) e um aviso de confidencialidade LGPD.

STACK
App web responsivo (React + Tailwind).

FONTE DE DADOS — TEMPO REAL (obrigatório)
O painel NÃO usa dados estáticos. Ele é alimentado pela PRÓPRIA JOANA em tempo real: a Joana escreve o estado das pacientes e as conversas, e o painel reflete isso ao vivo. Consuma uma API HTTP (que já será fornecida) com este contrato:
- GET /api/patients -> lista de pacientes no formato do MODELO DE DADOS abaixo (com mensagens, marcos e ciclos).
- GET /api/patients/:telefone -> uma paciente específica (mesmo formato).
- TEMPO REAL: o painel deve se ATUALIZAR SOZINHO, sem recarregar. Faça polling da API a cada 15 segundos e, se disponível, escute o stream GET /api/stream (Server-Sent Events) para atualização instantânea. Quando chega mensagem nova, marco novo, paciente nova ou muda o status ativa/inativa, a tela reflete na hora (novo balão no mockup, selo muda, contador atualiza).
- URL base da API por variável de ambiente (ex.: VITE_API_URL), com fallback pros DADOS DE EXEMPLO abaixo só em modo dev/preview.
- Tratar carregando/erro com elegância (skeleton nos cards; aviso discreto se a API cair).

TELA 1 — HOME (visão geral)
- Grid de cards, um por paciente.
- Cada card: FOTO do WhatsApp (circular) + NOME + selo de status: ATIVA (verde) se a paciente já respondeu à Joana ao menos uma vez, INATIVA (cinza) se nunca respondeu.
- Mostrar a data da última interação.
- Cabeçalho: logo ADERE.AI, contador (X ativas / Y total) e busca por nome.
- Clicar num card abre a TELA 2 daquela paciente.

TELA 2 — DETALHE DA PACIENTE (duas colunas)
(A) MOCKUP DO WHATSAPP (esquerda)
Réplica fiel da conversa do WhatsApp: cabeçalho com foto+nome, fundo do WhatsApp, balões verdes para a Joana e brancos para a paciente, horários e "visto". Renderizar TODAS as trocas em ordem cronológica.

(B) PAINEL DE MARCOS (direita, FORA do mockup)
Atalhos visuais (cards + mini timeline) para:
- Aceite do termo LGPD (data + selo "aceito")
- Diagnóstico recente
- Tratamento atual
- Medicamentos (lista)
- Data da última consulta
- Data da próxima consulta
- Regras de check-in (ex.: semanal)
- META: agendar consulta de retorno em 30 dias — com a DATA em que vence, contagem ("faltam X dias") e status (em andamento / vencida / ALCANÇADA).

CICLOS (estado especial)
Uma paciente evolui em ciclos. Quando a meta de retorno é cumprida (consulta feita), a meta vira ALCANÇADA (selo verde) e abre um NOVO CICLO com novo tratamento e nova meta. Mostrar um seletor/timeline de ciclos: "Ciclo 1 ✓ · Ciclo 2 (atual)".

MODELO DE DADOS (por paciente)
{ nome, foto, telefone, ativa, ultimaInteracao,
  mensagens: [{ de: "joana"|"paciente", texto, hora }],
  marcos: { termoLGPD:{aceito,data}, diagnostico, tratamento, medicamentos:[], ultimaConsulta, proximaConsulta, checkins, metaRetorno:{data,status} },
  ciclos: [{ numero, tratamento, meta:{data,status}, atual }] }

DADOS DE EXEMPLO (pacientes reais — usar)
- RENATA LOVETRO — ATIVA. Termo LGPD aceito 03/06/2026. TRH. Ciclo 1: meta de retorno ALCANÇADA (consulta feita). Ciclo 2 (atual): novo tratamento + nova meta = consulta em 30 dias. Check-in semanal. Conversa: onboarding + aceite do termo + check-ins ("adesivo tranquilo, sem vermelhidão; fogachos e irritação continuam; sono ruim").
- PATRÍCIA GUIMARÃES — ATIVA. TRH: estradiol transdérmico (1 pump manhã) + progesterona oral (noite) + testosterona gel (manhã, libido). Retorno para ajuste de dose. Check-in semanal.
- THAÍS THOMAZZONI — ATIVA. TRH há 3 anos: Lenzzeto (2 sprays estradiol manhã) + progesterona (1 comp noite) + testosterona gel (manhã). Exames a coletar. Check-in semanal.
- ANNA PAOLA — INATIVA (ainda não respondeu). Sem conversa.
(Fotos: usar avatares/placeholders por enquanto.)

DESIGN
Paleta acolhedora e clínica (verdes suaves / creme / off-white), tipografia limpa. Mockup do WhatsApp fiel (verde #25D366 nos balões da Joana). Cards de marco com ícones. Selos de status coloridos. Totalmente responsivo. Tela de login simples + aviso "Dados clínicos confidenciais — LGPD".

CRITÉRIOS DE ACEITE
- O painel lê da API ao vivo e se atualiza sozinho (polling 15s / SSE): mensagem nova da Joana aparece no mockup sem recarregar; paciente nova aparece na home; status ativa/inativa muda em tempo real.
- Home lista todas as pacientes com foto, nome e status ativa/inativa correto.
- Clicar abre o detalhe com o mockup do WhatsApp + painel de marcos.
- Renata no Ciclo 2, com o Ciclo 1 marcado como meta ALCANÇADA.
- Meta de retorno mostra a data de vencimento e quantos dias faltam.
