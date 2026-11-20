# Especificação de Requisitos — UniReserve (UNISAPIENS)

> **Responsável:** Gabriel — Analista de Requisitos  
> **Projeto:** MVP — Aplicação Web para Reserva de Salas e Laboratórios  
> **Instituição:** UNISAPIENS · **Área:** Sistemas de Informação  
> **Metodologia:** Kanban (Requisitos, UX/Prototipação, Desenvolvimento e QA/Testes)

---

## 1. Equipe e Papéis

| Integrante | Papel no Projeto |
|---|---|
| Gabriel | Analista de Requisitos |
| Caio | Qualidade e Testes (QA) |
| Many | Desenvolvedor |
| Jadson | Desenvolvedor |
| Amadio | UX e Prototipação |

> **Nota de governança (Kanban):** Os papéis de *Product Owner* (priorização de produto junto à coordenação/reitoria) e *Scrum Master* (remoção de impedimentos e organização do fluxo Kanban) são conduzidos de forma colaborativa pelo time, mantendo a separação de entregas por especialidade.

---

## 2. Objetivo e Contextualização

Centralizar e organizar o processo de **consulta, solicitação, aprovação e gerenciamento de reservas de salas e laboratórios** da UNISAPIENS, reduzindo conflitos de horário, facilitando a localização de aulas pelos alunos e dando controle administrativo à coordenação.

---

## 3. Perfis de Usuário e Permissões

| Perfil | Pode consultar | Pode reservar | Precisa de aprovação | Escopo principal |
|---|---|---|---|---|
| **Aluno** | Sim | Não | — | Consulta salas, equipamentos, localização, calendário e horários de aula |
| **Professor** | Sim | Sim | Sim | Consulta e solicita reservas com finalidade; edita/cancela conforme regra |
| **Coordenador** | Sim | Sim | Não | Reserva direta; aprova/rejeita; gerencia espaços, bloqueios, equipamentos e usuários |
| **Usuário externo** | Sim | Sim | Sim | Solicita reservas apenas nos espaços previamente autorizados pela coordenação |

### 3.1 Aluno
- Visualizar salas e laboratórios, capacidade, equipamentos e localização.
- Consultar calendário geral e da sala, verificar salas ocupadas/horários e localizar em qual sala ocorrerá a aula de determinado professor.
- **Restrição:** não pode criar, editar ou cancelar reservas.

### 3.2 Professor
- Consultar e pesquisar espaços, equipamentos e disponibilidade.
- Solicitar reservas informando a finalidade; acompanhar status; visualizar, editar (enquanto pendente) e cancelar suas próprias reservas.
- Toda solicitação nasce com status **Pendente** e só é confirmada após aprovação do coordenador.

### 3.3 Coordenador
- Realizar reservas diretamente (já nascem **Reservadas**, sem aprovação).
- Aprovar ou rejeitar solicitações pendentes; visualizar e pesquisar todas as reservas.
- Cadastrar/editar salas, laboratórios e equipamentos; associar equipamentos aos espaços; aplicar/remover bloqueios temporários; gerenciar usuários externos e autorizações; consultar histórico de alterações e administrar regras de utilização.

### 3.4 Usuário Externo
- Exemplos: Atlética, líder de grupo, ministrante, palestrante e outros autorizados.
- Segue fluxo de solicitação com aprovação semelhante ao professor, porém **restrito exclusivamente aos espaços autorizados pela coordenação**.

---

## 4. Fluxo Geral de Reserva e Status dos Espaços

### Fluxos
- **Professor / Usuário Externo:** `Solicitação → Pendente → Análise do Coordenador`
  - Se aprovada: `Pendente → Reservada`
  - Se rejeitada: `Pendente → Disponível` (libera o horário e registra motivo)
- **Coordenador:** `Reserva → Reservada` (confirmação imediata)

### Status no Calendário
- **Disponível:** sem reserva ativa nem bloqueio no período.
- **Pendente:** solicitação em análise; **bloqueia temporariamente o período** contra novas solicitações concorrentes.
- **Reservado:** solicitação aprovada ou reserva direta do coordenador.
- **Bloqueado:** período interditado administrativamente pela coordenação (manutenção, evento, etc.).
