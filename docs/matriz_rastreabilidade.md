# Matriz de Rastreabilidade — UniReserve (Requisitos × Código)

> **Responsável:** Gabriel — Analista de Requisitos  
> **Base auditada:** branch `main` (commit `702230e`) + referência ao PR `#1` (`qa/melhorias-backend-e-testes`)  
> **Objetivo:** Rastrear cada Requisito Funcional (`RF01–RF55`) e Regra de Negócio (`RN01–RN31`) contra a implementação real, documentando lacunas e encaminhando pendências técnicas para Desenvolvedores, QA e UX no Kanban.

---

## 1. Resumo Executivo da Cobertura (`main`)

| Categoria | Total | Atendido | Parcial | Pendente (MVP) | Pós-MVP (Fora do escopo) |
|---|---:|---:|---:|---:|---:|
| **Requisitos Funcionais (`RF01–RF55`)** | 55 | 46 | 4 | 0 | 5 |
| **Regras de Negócio (`RN01–RN31`)** | 31 | 19 | 7 | 5 | 0 |

- **RFs Parciais no MVP:** `RF40` (`curso` exibido sem campo de cadastro/edição), `RF46` (`regras_especificas` não exibidas antes da reserva), `RF50` (filtro verifica janela fixa de 30 min a partir de um instante, sem intervalo início/fim), `RF51` (notificações de reserva funcionam; avisos institucionais ainda são slides estáticos).
- **RFs Pós-MVP (documentados como futuros):** `RF10`, `RF11`, `RF28`, `RF29`, `RF45`.
- **RNs Pendentes (não aplicadas no código):** `RN06` (espaços exclusivos por perfil além de externos), `RN08` (duração máxima), `RN09` (limite de antecedência), `RN12` (validação de capacidade na reserva), `RN14` (validação do campo `exige_autorizacao` dos equipamentos na reserva).
- **RNs Parciais (exigem reforço no backend/UI):** `RN01` (auto-cadastro permite escolher `professor`), `RN05` e `RN29` (RBAC de espaços/equipamentos/usuários apenas na UI), `RN07` (horário de funcionamento só na exibição da agenda; passado validado só na UI), `RN13` (`regras_especificas` salvas, mas não exibidas ao reservar), `RN17` (`aprovar_se_disponivel` não revalida bloqueios), `RN18` (criação de bloqueio não alerta sobre reservas existentes).

---

## 2. Rastreabilidade dos Requisitos Funcionais (RF01–RF55)

| ID | Requisito | Escopo | Status (`main`) | Arquivos no Código | Observações / Lacunas |
|---|---|---|---|---|---|
| **RF01** | Login utilizando RA e senha | MVP | Atendido | `views/login_view.py`, `controllers/auth_controller.py`, `services/auth_service.py` | Autentica via RA no Firestore + Firebase Auth (`signInWithPassword` + `verify_id_token`). |
| **RF02** | Identificação dos usuários | MVP | Atendido | `domain/enums.py`, `utils/ui.py`, `views/componentes.py` | Identifica os 4 perfis com badges e barra superior. |
| **RF03** | Recuperação de senha | MVP | Atendido | `views/login_view.py`, `views/perfil_view.py`, `services/auth_service.py` | Envia `PASSWORD_RESET` via Firebase sem expor se o RA existe. |
| **RF04** | Visualização de salas e laboratórios | MVP | Atendido | `views/espacos_view.py`, `views/componentes.py` | Grade de cards com faixa de status em tempo real. |
| **RF05** | Pesquisa de salas e laboratórios | MVP | Atendido | `views/espacos_view.py` | Busca textual por nome, bloco, andar, identificação, tipo, características e equipamentos. |
| **RF06** | Filtros de pesquisa | MVP | Atendido | `views/espacos_view.py` | Painel "Filtros avançados" com 5 critérios combináveis. |
| **RF07** | Visualização da capacidade | MVP | Atendido | `views/componentes.py`, `views/reserva_dialogos.py` | Exibida no card da sala e no painel do diálogo de reserva. |
| **RF08** | Visualização de equipamentos | MVP | Atendido | `views/componentes.py` | Lista equipamentos com ícones Material no card da sala. |
| **RF09** | Visualização da localização | MVP | Atendido | `views/componentes.py`, `utils/ui.py` | Exibe bloco, andar e identificação. |
| **RF10** | Mapa 2D | Pós-MVP | Pós-MVP | — | Classificado fora do MVP conforme Seção 25. |
| **RF11** | Mapa 3D | Pós-MVP | Pós-MVP | — | Previsto como funcionalidade futura. |
| **RF12** | Visualização de horários disponíveis | MVP | Atendido | `views/calendario_view.py`, `views/reserva_dialogos.py` | Mostra janelas livres (07h–23h) com identificação da sala ao filtrar 1 sala + 1 dia e badge "Dia livre". |
| **RF13** | Visualização de horários ocupados | MVP | Atendido | `views/calendario_view.py`, `views/reserva_dialogos.py`, `views/componentes.py` | Exibe reservas confirmadas, pendentes e bloqueios. |
| **RF14** | Calendário geral | MVP | Atendido | `views/calendario_view.py`, `services/reserva_service.py` | Lista todas as ocupações (reservas ativas + bloqueios). |
| **RF15** | Calendário específico do espaço | MVP | Atendido | `views/calendario_view.py`, `views/componentes.py` | Botão "Ver agenda" pré-seleciona a sala na agenda. |
| **RF16** | Consulta das próprias reservas | MVP | Atendido | `views/reservas_view.py`, `services/reserva_service.py` | Tabela paginada com filtros de período, sala e status. |
| **RF17** | Solicitação de reserva | MVP | Atendido | `views/reserva_dialogos.py`, `services/reserva_service.py` | Professores e externos criam solicitações (`pendente`); coordenador cria `reservada`. |
| **RF18** | Seleção do espaço | MVP | Atendido | `views/espacos_view.py`, `views/reserva_dialogos.py` | Seleção via botão "Reservar" no card ou selectbox na edição. |
| **RF19** | Seleção de data e horário | MVP | Atendido | `views/reserva_dialogos.py` | Inputs de data e hora início/fim (passo de 30 min). |
| **RF20** | Confirmação da solicitação | MVP | Atendido | `views/reserva_dialogos.py`, `views/espacos_view.py` | Exibe feedback explícito após envio da solicitação/confirmação. |
| **RF21** | Edição de reserva | MVP | Atendido | `views/reservas_view.py`, `views/reserva_dialogos.py`, `services/reserva_service.py` | Permitida para dono (enquanto `pendente`) e coordenador, com aviso de erro de disponibilidade. |
| **RF22** | Cancelamento de reserva | MVP | Atendido | `views/reservas_view.py`, `views/coordenador_view.py`, `services/reserva_service.py` | Permitido ao dono ou coordenador em reservas ativas. |
| **RF23** | Detalhes da reserva | MVP | Atendido | `views/reserva_dialogos.py` | Diálogo `dialogo_detalhes` com status, período, motivo e motivo da recusa. |
| **RF24** | Histórico de reservas | MVP | Atendido | `views/reservas_view.py`, `views/coordenador_view.py`, `services/historico_service.py` | Usuário vê reservas passadas (`Concluída`/`Expirada`); coordenador vê trilha de eventos. |
| **RF25** | Notificação após solicitação | MVP | Atendido | `services/reserva_service.py`, `services/notificacao_service.py` | Cria notificação `reserva_criada`. |
| **RF26** | Notificação após alteração | MVP | Atendido | `services/reserva_service.py`, `services/notificacao_service.py` | Cria notificação `reserva_alterada` (e também aprovação/rejeição). |
| **RF27** | Notificação após cancelamento | MVP | Atendido | `services/reserva_service.py`, `services/notificacao_service.py` | Cria notificação `reserva_cancelada`. |
| **RF28** | Chat com coordenadores | Pós-MVP | Pós-MVP | — | Previsto como funcionalidade futura. |
| **RF29** | Envio e recebimento de mensagens | Pós-MVP | Pós-MVP | — | Previsto como funcionalidade futura. |
| **RF30** | Visualização do status | MVP | Atendido | `utils/ui.py`, `views/reservas_view.py`, `views/coordenador_view.py` | Badges diferenciados para Confirmada, Pendente, Concluída, Recusada, Cancelada, Expirada e Bloqueado. |
| **RF31** | Tela inicial personalizada | MVP | Atendido | `main.py`, `views/home_view.py` | Menu lateral e atalhos adaptados ao perfil logado. |
| **RF32** | Área administrativa do coordenador | MVP | Atendido | `views/coordenador_view.py` | Dashboard com indicadores e 5 seções administrativas. |
| **RF33** | Gerenciamento de salas e laboratórios | MVP | Atendido | `views/espacos_view.py`, `views/coordenador_view.py`, `services/espaco_service.py` | Criação, edição e desativação lógica de espaços. |
| **RF34** | Cadastro de salas e laboratórios | MVP | Atendido | `views/espacos_view.py`, `controllers/espaco_controller.py`, `services/espaco_service.py` | Diálogo "Criar nova sala" com associação de equipamentos. |
| **RF35** | Edição de espaços | MVP | Atendido | `views/espacos_view.py`, `services/espaco_service.py` | Diálogo `_editar_espaco` acessível pelo coordenador. |
| **RF36** | Bloqueio temporário | MVP | Atendido | `views/coordenador_view.py`, `services/bloqueio_service.py`, `models/bloqueio_model.py` | Criação, listagem e remoção de bloqueios por período e motivo. |
| **RF37** | Visualização de todas as reservas | MVP | Atendido | `views/coordenador_view.py`, `services/reserva_service.py` | Seção "Todas as reservas" exclusiva do coordenador. |
| **RF38** | Pesquisa de reservas | MVP | Atendido | `views/coordenador_view.py` | Filtro por usuário/sala/finalidade, situação e data. |
| **RF39** | Aprovação e rejeição | MVP | Atendido | `views/coordenador_view.py`, `services/reserva_service.py` | Aprovação em um clique e rejeição com motivo obrigatório. |
| **RF40** | Informações do usuário | MVP | Parcial | `views/perfil_view.py` | Exibe Nome, RA, E-mail, Telefone, Perfil e `Curso`, mas não há cadastro/edição de `curso` (sempre `—`). |
| **RF41** | Alteração de dados da conta | MVP | Atendido | `views/perfil_view.py`, `controllers/usuario_controller.py`, `models/usuario_model.py` | Permite editar e-mail/telefone (sincronizado com Firebase Auth) e solicitar troca de senha. **Atenção:** preservar no merge do PR `#1`. |
| **RF42** | Logout | MVP | Atendido | `controllers/auth_controller.py`, `utils/session.py`, `views/perfil_view.py` | Encerra sessão limpando usuário e token. |
| **RF43** | Filtro do calendário | MVP | Atendido | `views/calendario_view.py` | Alterna visualização por Dia, Semana ou Mês. |
| **RF44** | Visualização de horários livres | MVP | Atendido | `views/calendario_view.py` | `_horarios_livres` calcula lacunas livres no modo Dia + 1 sala. |
| **RF45** | Detalhes pelo mapa | Pós-MVP | Pós-MVP | — | Dependente de `RF10` (Mapa 2D). |
| **RF46** | Características do espaço | MVP | Parcial | `views/componentes.py`, `views/espacos_view.py` | Exibe características e equipamentos no card, mas **não exibe `regras_especificas`** antes de reservar. |
| **RF47** | Confirmação de cancelamento | MVP | Atendido | `views/reserva_dialogos.py` | Diálogo modal `dialogo_cancelar` exige confirmação ("Sim, cancelar"). |
| **RF48** | Pesquisa por capacidade | MVP | Atendido | `views/espacos_view.py` | Filtro por faixas (`Qualquer`, `>20`, `>50`, `>100`). |
| **RF49** | Pesquisa por equipamentos | MVP | Atendido | `views/espacos_view.py` | Multiselect de equipamentos exigindo que o espaço contenha todos os selecionados. |
| **RF50** | Pesquisa por disponibilidade | MVP | Parcial | `views/espacos_view.py` | Filtra por um instante `datetime_input` com janela fixa de 30 min (não permite escolher intervalo início–fim). |
| **RF51** | Notificações e avisos | MVP | Parcial | `views/home_view.py`, `controllers/notificacao_controller.py` | Exibe notificações de reserva com feedback de falha ao marcar lida; avisos institucionais dinâmicos ainda não existem. |
| **RF52** | Cadastro de equipamentos | MVP | Atendido | `views/coordenador_view.py`, `services/equipamento_service.py` | CRUD de equipamentos na Área do coordenador. |
| **RF53** | Consulta de reservas pelos alunos | MVP | Atendido | `main.py`, `views/calendario_view.py`, `views/reservas_view.py`, `services/reserva_service.py` | Aluno vê salas e agenda; bloqueado na UI e no serviço para criar reservas. |
| **RF54** | Consulta de localização de aulas | MVP | Atendido | `views/calendario_view.py` | Aluno pesquisa por professor, atividade ou sala para localizar a aula. |
| **RF55** | Gerenciamento de usuários externos | MVP | Atendido | `views/coordenador_view.py`, `controllers/usuario_controller.py`, `models/usuario_model.py` | Coordenador define perfil, status ativo e `espacos_autorizados_ids` para externos. |
