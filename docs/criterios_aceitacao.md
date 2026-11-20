# Critérios de Aceitação (BDD) e Checklist de Homologação — UniReserve

> **Responsável:** Gabriel — Analista de Requisitos  
> **Público-alvo:** Equipe de Desenvolvimento, Qualidade e Testes (QA) e Homologação com a Coordenação / Reitoria (UNISAPIENS)  
> **Referências:** [docs/requisitos.md](requisitos.md) · [docs/matriz_rastreabilidade.md](matriz_rastreabilidade.md)

---

## 1. Checklist Geral de Aceitação do MVP (Seção 23)

O MVP será considerado pronto para homologação quando todos os critérios abaixo estiverem validados:

- [ ] **CA01** (`RF01`, `RF02`, `RN01`, `RN03`) — Usuários conseguem acessar o sistema com RA e senha de acordo com seus perfis.
- [ ] **CA02** (`RF53`, `RN30`) — Alunos conseguem consultar salas e reservas sem poder criar, editar ou cancelar reservas.
- [ ] **CA03** (`RF17–RF20`, `RN21`, `RN25`) — Professores conseguem enviar solicitações de reserva (nascendo como `Pendente`).
- [ ] **CA04** (`RF17`, `RF55`, `RN28`) — Usuários externos conseguem solicitar reservas apenas nos espaços autorizados pela coordenação.
- [ ] **CA05** (`RF39`, `RN25`) — Coordenadores conseguem aprovar ou rejeitar solicitações pendentes (com motivo obrigatório na rejeição).
- [ ] **CA06** (`RN26`) — Coordenadores conseguem realizar reservas diretamente (nascendo como `Confirmada`/`Reservada`).
- [ ] **CA07** (`RN02`, `RN10`) — O sistema impede conflitos de horário no mesmo espaço, permitindo horários adjacentes.
- [ ] **CA08** (`RN24`) — Solicitações pendentes bloqueiam temporariamente o horário contra novas solicitações.
- [ ] **CA09** (`RN19`) — Solicitações rejeitadas e reservas canceladas liberam imediatamente o período.
- [ ] **CA10** (`RF30`, `RN22`) — Reservas aprovadas passam a aparecer como confirmadas (`Reservada`).
- [ ] **CA11** (`RF36`, `RN17`, `RN18`, `RN31`) — Espaços bloqueados não recebem novas reservas nem aprovações conflitantes durante o bloqueio.
- [ ] **CA12** (`RN27`) — A finalidade da reserva é obrigatória e fica registrada na solicitação.
- [ ] **CA13** (`RF04–RF09`, `RF48`, `RF50`) — Salas e laboratórios podem ser pesquisados e filtrados (nome, bloco, tipo, capacidade e disponibilidade).
- [ ] **CA14** (`RF49`) — Equipamentos podem ser utilizados como filtro de pesquisa.
- [ ] **CA15** (`RF52`, `RN29`) — Coordenadores conseguem cadastrar, editar e associar equipamentos aos espaços.
- [ ] **CA16** (`RF12–RF15`, `RF43`, `RF44`) — Os calendários (geral e da sala) apresentam corretamente horários ocupados, pendentes, bloqueados e livres.
- [ ] **CA17** (`RF54`) — Alunos conseguem pesquisar por professor, sala ou atividade para localizar onde ocorrerá uma aula.
- [ ] **CA18** (`RF25–RF27`, `RF51`, `RN23`) — Notificações são apresentadas aos usuários na tela inicial conforme os eventos da reserva.
