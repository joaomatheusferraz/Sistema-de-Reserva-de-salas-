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

---

## 5. Requisitos Funcionais Consolidados (RF01–RF55)

> **Classificação de Escopo:**  
> - `[MVP]` — Escopo obrigatório desta primeira entrega.  
> - `[Pós-MVP]` — Funcionalidade prevista para evolução futura (conforme Seções 25 e 26 da documentação).

| ID | Requisito | Descrição | Escopo |
|---|---|---|---|
| **RF01** | Login utilizando RA e senha | Permitir que usuários autenticados acessem o sistema de acordo com seu perfil. | `[MVP]` |
| **RF02** | Identificação dos usuários | Permitir identificar alunos, professores, coordenadores e usuários externos. | `[MVP]` |
| **RF03** | Recuperação de senha | Permitir recuperação ou redefinição de senha. | `[MVP]` |
| **RF04** | Visualização de salas e laboratórios | Permitir consultar os espaços cadastrados. | `[MVP]` |
| **RF05** | Pesquisa de salas e laboratórios | Permitir pesquisar espaços. | `[MVP]` |
| **RF06** | Filtros de pesquisa | Permitir filtrar espaços por diferentes características. | `[MVP]` |
| **RF07** | Visualização da capacidade | Exibir a capacidade máxima dos ambientes. | `[MVP]` |
| **RF08** | Visualização de equipamentos | Exibir os equipamentos associados aos espaços. | `[MVP]` |
| **RF09** | Visualização da localização | Exibir a localização dos ambientes. | `[MVP]` |
| **RF10** | Mapa 2D | Permitir visualizar a instituição em um mapa superior. | `[Pós-MVP]` |
| **RF11** | Mapa 3D | Permitir futuramente uma visualização tridimensional. | `[Pós-MVP]` |
| **RF12** | Visualização de horários disponíveis | Exibir períodos disponíveis. | `[MVP]` |
| **RF13** | Visualização de horários ocupados | Exibir períodos ocupados. | `[MVP]` |
| **RF14** | Calendário geral | Exibir as reservas da instituição. | `[MVP]` |
| **RF15** | Calendário específico do espaço | Exibir as reservas de uma sala ou laboratório. | `[MVP]` |
| **RF16** | Consulta das próprias reservas | Permitir que o usuário consulte suas reservas e solicitações. | `[MVP]` |
| **RF17** | Solicitação de reserva | Permitir que professores e usuários externos solicitem reservas. | `[MVP]` |
| **RF18** | Seleção do espaço | Permitir selecionar a sala ou laboratório. | `[MVP]` |
| **RF19** | Seleção de data e horário | Permitir selecionar o período desejado. | `[MVP]` |
| **RF20** | Confirmação da solicitação | Permitir confirmar uma solicitação de reserva. | `[MVP]` |
| **RF21** | Edição de reserva | Permitir editar reservas conforme as permissões do usuário. | `[MVP]` |
| **RF22** | Cancelamento de reserva | Permitir cancelar reservas conforme as regras definidas. | `[MVP]` |
| **RF23** | Detalhes da reserva | Permitir visualizar informações completas da reserva. | `[MVP]` |
| **RF24** | Histórico de reservas | Permitir consultar reservas anteriores. | `[MVP]` |
| **RF25** | Notificação após solicitação | Notificar o usuário sobre o envio da solicitação. | `[MVP]` |
| **RF26** | Notificação após alteração | Notificar alterações realizadas. | `[MVP]` |
| **RF27** | Notificação após cancelamento | Notificar cancelamentos. | `[MVP]` |
| **RF28** | Chat com coordenadores | Permitir comunicação entre usuários autorizados e coordenadores. | `[Pós-MVP]` |
| **RF29** | Envio e recebimento de mensagens | Permitir troca de mensagens pelo chat. | `[Pós-MVP]` |
| **RF30** | Visualização do status | Exibir se a solicitação está Pendente, Reservada, Rejeitada, Cancelada ou outra situação definida. | `[MVP]` |
| **RF31** | Tela inicial personalizada | Apresentar funcionalidades conforme o perfil do usuário. | `[MVP]` |
| **RF32** | Área administrativa do coordenador | Disponibilizar funções administrativas. | `[MVP]` |
| **RF33** | Gerenciamento de salas e laboratórios | Permitir administrar os espaços. | `[MVP]` |
| **RF34** | Cadastro de salas e laboratórios | Permitir cadastrar novos espaços e seus equipamentos. | `[MVP]` |
| **RF35** | Edição de espaços | Permitir alterar informações dos espaços. | `[MVP]` |
| **RF36** | Bloqueio temporário | Permitir bloquear salas e laboratórios. | `[MVP]` |
| **RF37** | Visualização de todas as reservas | Permitir ao coordenador consultar todas as reservas. | `[MVP]` |
| **RF38** | Pesquisa de reservas | Permitir pesquisar reservas por usuário, espaço ou data. | `[MVP]` |
| **RF39** | Aprovação e rejeição | Permitir que coordenadores aprovem ou rejeitem solicitações. | `[MVP]` |
| **RF40** | Informações do usuário | Permitir consultar dados do usuário. | `[MVP]` |
| **RF41** | Alteração de dados da conta | Permitir alteração de dados autorizados. | `[MVP]` |
| **RF42** | Logout | Permitir encerrar a sessão. | `[MVP]` |
| **RF43** | Filtro do calendário | Permitir visualizar reservas por dia, semana ou mês. | `[MVP]` |
| **RF44** | Visualização de horários livres | Exibir horários disponíveis diretamente no calendário. | `[MVP]` |
| **RF45** | Detalhes pelo mapa | Permitir consultar informações de um espaço selecionado no mapa. | `[Pós-MVP]` |
| **RF46** | Características do espaço | Exibir características antes da realização da reserva. | `[MVP]` |
| **RF47** | Confirmação de cancelamento | Solicitar confirmação antes de cancelar uma reserva. | `[MVP]` |
| **RF48** | Pesquisa por capacidade | Permitir pesquisar ambientes pela capacidade. | `[MVP]` |
| **RF49** | Pesquisa por equipamentos | Permitir pesquisar ambientes pelos equipamentos disponíveis. | `[MVP]` |
| **RF50** | Pesquisa por disponibilidade | Permitir pesquisar espaços disponíveis em determinado período. | `[MVP]` |
| **RF51** | Notificações e avisos | Exibir notificações de reservas e avisos institucionais na tela inicial. | `[MVP]` |
| **RF52** | Cadastro de equipamentos | Permitir que coordenadores cadastrem novos tipos de equipamentos. | `[MVP]` |
| **RF53** | Consulta de reservas pelos alunos | Permitir que alunos visualizem reservas existentes, sem permitir que realizem ou alterem reservas. | `[MVP]` |
| **RF54** | Consulta de localização de aulas | Permitir que alunos utilizem as informações de reservas para identificar o espaço utilizado em determinada aula ou atividade. | `[MVP]` |
| **RF55** | Gerenciamento de usuários externos | Permitir que coordenadores gerenciem usuários externos autorizados. | `[MVP]` |
