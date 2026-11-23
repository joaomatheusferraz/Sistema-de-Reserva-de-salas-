# Matriz de Rastreabilidade — UniReserve (Requisitos × Código)

> **Responsável:** Gabriel — Analista de Requisitos  
> **Base auditada:** branch `main` (commit `702230e`) + referência ao PR `#1` (`qa/melhorias-backend-e-testes`)  
> **Objetivo:** Rastrear cada Requisito Funcional (`RF01–RF55`) e Regra de Negócio (`RN01–RN31`) contra a implementação real, documentando lacunas e encaminhando pendências técnicas para Desenvolvedores, QA e UX no Kanban.

---

## 1. Resumo Executivo da Cobertura (`main`)

| Categoria | Total | Atendido | Parcial | Pendente (MVP) | Pós-MVP (Fora do escopo) |
|---|---:|---:|---:|---:|---:|
| **Requisitos Funcionais (`RF01–RF55`)** | 55 | 47 | 3 | 0 | 5 |
| **Regras de Negócio (`RN01–RN31`)** | 31 | 24 | 2 | 5 | 0 |

- **RFs Parciais no MVP:** `RF40` (`curso` exibido sem campo de cadastro/edição), `RF50` (filtro verifica janela fixa de 30 min a partir de um instante, sem intervalo início/fim), `RF51` (notificações de reserva funcionam; avisos institucionais ainda são slides estáticos).
- **RFs Pós-MVP (documentados como futuros):** `RF10`, `RF11`, `RF28`, `RF29`, `RF45`.
- **RNs Pendentes (não aplicadas no código):** `RN06` (espaços exclusivos por perfil além de externos), `RN08` (duração máxima), `RN09` (limite de antecedência), `RN12` (validação de capacidade na reserva), `RN14` (validação do campo `exige_autorizacao` dos equipamentos na reserva).
- **RNs Parciais (exigem reforço no backend/UI):** `RN05` e `RN29` (os serviços de espaço e equipamento exigem `coordenador`, mas a checagem é ignorada quando `perfil` não é informado e as views/controllers ainda não repassam o perfil).

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
| **RF46** | Características do espaço | MVP | Atendido | `views/componentes.py`, `views/espacos_view.py`, `views/reserva_dialogos.py` | Exibe características e equipamentos no card e as `regras_especificas` no diálogo de reserva, antes da confirmação (`tests/test_regras_espaco.py`). |
| **RF47** | Confirmação de cancelamento | MVP | Atendido | `views/reserva_dialogos.py` | Diálogo modal `dialogo_cancelar` exige confirmação ("Sim, cancelar"). |
| **RF48** | Pesquisa por capacidade | MVP | Atendido | `views/espacos_view.py` | Filtro por faixas (`Qualquer`, `>20`, `>50`, `>100`). |
| **RF49** | Pesquisa por equipamentos | MVP | Atendido | `views/espacos_view.py` | Multiselect de equipamentos exigindo que o espaço contenha todos os selecionados. |
| **RF50** | Pesquisa por disponibilidade | MVP | Parcial | `views/espacos_view.py` | Filtra por um instante `datetime_input` com janela fixa de 30 min (não permite escolher intervalo início–fim). |
| **RF51** | Notificações e avisos | MVP | Parcial | `views/home_view.py`, `controllers/notificacao_controller.py` | Exibe notificações de reserva com feedback de falha ao marcar lida; avisos institucionais dinâmicos ainda não existem. |
| **RF52** | Cadastro de equipamentos | MVP | Atendido | `views/coordenador_view.py`, `services/equipamento_service.py` | CRUD de equipamentos na Área do coordenador. |
| **RF53** | Consulta de reservas pelos alunos | MVP | Atendido | `main.py`, `views/calendario_view.py`, `views/reservas_view.py`, `services/reserva_service.py` | Aluno vê salas e agenda; bloqueado na UI e no serviço para criar reservas. |
| **RF54** | Consulta de localização de aulas | MVP | Atendido | `views/calendario_view.py` | Aluno pesquisa por professor, atividade ou sala para localizar a aula. |
| **RF55** | Gerenciamento de usuários externos | MVP | Atendido | `views/coordenador_view.py`, `controllers/usuario_controller.py`, `models/usuario_model.py` | Coordenador define perfil, status ativo e `espacos_autorizados_ids` para externos. |

---

## 3. Rastreabilidade das Regras de Negócio (RN01–RN31)

| ID | Regra de Negócio | Status (`main`) | Onde está no Código / Testes | Lacunas Identificadas |
|---|---|---|---|---|
| **RN01** | Níveis de acesso | Atendido | `domain/enums.py`, `main.py`, `services/auth_service.py`, `services/reserva_service.py`, `tests/test_services.py`, `tests/test_regras_negocio.py` | Auto-cadastro só aceita `aluno` e `externo` (backend e tela); o perfil informado na reserva precisa corresponder ao do usuário. |
| **RN02** | Reservas no mesmo dia | Atendido | `models/reserva_model.py` (`_sobrepoe`), `tests/test_services.py` | Permite horários adjacentes no mesmo dia; coberto por teste unitário. |
| **RN03** | Autenticação | Atendido | `main.py`, `utils/session.py`, `services/auth_service.py` | Bloqueia navegação sem login e valida token Firebase. |
| **RN04** | Permissão de alteração | Atendido | `services/reserva_service.py`, `tests/test_services.py` | Valida dono ou coordenador e impede professor de editar reserva já aprovada. |
| **RN05** | Permissões administrativas | Parcial | `views/coordenador_view.py`, `services/reserva_service.py`, `services/bloqueio_service.py`, `services/espaco_service.py`, `services/equipamento_service.py` | Reservas e bloqueios exigem `coordenador` no serviço (testado). Em `EspacoService`/`EquipamentoService` a checagem existe, mas é pulada quando `perfil=None` (padrão) e `espacos_view.py`/`coordenador_view.py` não repassam o perfil: falta torná-la obrigatória. |
| **RN06** | Espaços exclusivos | Pendente | — | Apenas externos têm restrição por espaço (`RN28`); não há campo de restrição de perfis no modelo de espaço. |
| **RN07** | Horário de funcionamento | Atendido | `services/reserva_service.py`, `views/calendario_view.py`, `views/reserva_dialogos.py`, `tests/test_reserva_horarios.py` | `ReservaService` valida 07h–23h, início e fim no mesmo dia e bloqueia criação em horário já passado (além da validação na UI). |
| **RN08** | Duração máxima | Pendente | — | Não há limite de duração máxima configurado ou validado em `ReservaService`. |
| **RN09** | Antecedência | Pendente | — | Não há regra de antecedência mínima/máxima validada em `ReservaService`. |
| **RN10** | Sobreposição | Atendido | `models/reserva_model.py`, `tests/test_services.py` | Garantida por transação no Firestore + `agenda_version` + normalização UTC/BRT. |
| **RN11** | Cancelamento | Atendido | `services/reserva_service.py` (`cancelar`), `views/reserva_dialogos.py` | Cancela reservas ativas com confirmação e registra histórico/notificação. |
| **RN12** | Capacidade | Pendente | `services/espaco_service.py` | Capacidade é cadastrada e filtrada, mas não existe campo de número de participantes na reserva para validar limite. |
| **RN13** | Regras específicas dos laboratórios | Atendido | `services/espaco_service.py`, `views/espacos_view.py`, `views/reserva_dialogos.py`, `tests/test_regras_espaco.py` | Campo `regras_especificas` é exibido ao solicitante no diálogo de reserva, antes da confirmação. |
| **RN14** | Equipamentos com autorização | Pendente | `services/equipamento_service.py`, `views/coordenador_view.py` | Flag `exige_autorizacao` existe no cadastro, mas nunca é verificada em `ReservaService`. |
| **RN15** | Responsável pela reserva | Atendido | `services/reserva_service.py` | Toda reserva valida e vincula `responsavel_id` existente e ativo. |
| **RN16** | Validação durante alteração | Atendido | `services/reserva_service.py` (`editar`), `models/reserva_model.py` (`atualizar_se_disponivel`) | Revalida sobreposição e bloqueios em transação (melhoria menor: checar também se espaço destino está `ativo=True`). |
| **RN17** | Espaços indisponíveis | Atendido | `models/reserva_model.py` | Criação, edição e aprovação verificam bloqueios ativos na transação da reserva. |
| **RN18** | Bloqueio administrativo | Atendido | `services/bloqueio_service.py`, `controllers/bloqueio_controller.py`, `views/coordenador_view.py`, `tests/test_bloqueios.py` | Ao criar o bloqueio, as reservas pendentes/confirmadas do período são identificadas, gravadas em `reservas_conflitantes_ids` e contadas no histórico. Melhoria futura: avisar o coordenador na tela. |
| **RN19** | Liberação após cancelamento | Atendido | `models/reserva_model.py` | Apenas status `pendente` e `reservada` ocupam agenda; `cancelada` e `rejeitada` liberam o período automaticamente. |
| **RN20** | Registro de alterações | Atendido | `services/historico_service.py`, `services/reserva_service.py`, `services/bloqueio_service.py` | Registra criação, alteração, aprovação, rejeição, cancelamento e bloqueio (melhoria: preencher `dados_anteriores` na edição). |
| **RN21** | Status pendente | Atendido | `services/reserva_service.py`, `tests/test_services.py` | Solicitações de professor/externo nascem `pendente` até análise. |
| **RN22** | Solicitação pendente não é reserva confirmada | Atendido | `services/reserva_service.py`, `utils/ui.py`, `views/coordenador_view.py` | Diferencia claramente `Pendente` de `Confirmada`/`Reservada` em status, badges e métricas. |
| **RN23** | Notificações | Atendido | `services/notificacao_service.py`, `views/home_view.py` | Notifica criação, aprovação, rejeição, alteração e cancelamento (avisos institucionais permanecem pendentes). |
| **RN24** | Bloqueio temporário de solicitações pendentes | Atendido | `models/reserva_model.py` | Checa conflito contra `{"pendente", "reservada"}` dentro da transação. |
| **RN25** | Aprovação de professores e externos | Atendido | `services/reserva_service.py`, `tests/test_services.py` | Exige `coordenador` para aprovar/rejeitar solicitações pendentes. |
| **RN26** | Reserva direta do coordenador | Atendido | `services/reserva_service.py`, `tests/test_services.py` | Reserva do coordenador nasce `reservada` com `aprovacao_necessaria=False`. |
| **RN27** | Finalidade da reserva | Atendido | `services/reserva_service.py` | Obrigatória na criação e edição. |
| **RN28** | Usuários externos | Atendido | `services/reserva_service.py`, `views/espacos_view.py`, `tests/test_services.py` | Valida `espacos_autorizados_ids` tanto na criação quanto na edição. |
| **RN29** | Controle de equipamentos | Parcial | `views/coordenador_view.py`, `services/equipamento_service.py`, `tests/test_equipamento_service.py` | Restrito ao coordenador na UI; o serviço rejeita outros perfis, mas só quando `perfil` é informado (mesma lacuna da `RN05`). |
| **RN30** | Consulta por alunos | Atendido | `main.py`, `services/reserva_service.py`, `tests/test_services.py` | Aluno consulta espaços/calendário e recebe `PermissionError` se tentar criar reserva. |
| **RN31** | Bloqueio durante manutenção | Atendido | `models/reserva_model.py`, `services/bloqueio_service.py` | Impede novas reservas e edições em períodos bloqueados. |

---

## 4. Encaminhamento de Pendências no Kanban (Por Papel)

### Para Desenvolvedores (Many / Jadson)
1. **[Concluído — RN01]** Auto-cadastro restrito a `aluno` e `externo` (`login_view.py` / `auth_service.py`).
2. **[Concluído — RN18]** `BloqueioService.criar` registra as reservas conflitantes (modelo de reservas agora ligado ao `BloqueioController`). Falta apenas o aviso visual na tela.
3. **[Alta — Segurança / RN05 e RN29]** Tornar obrigatória a checagem de `coordenador` em `EspacoService` e `EquipamentoService` (hoje ignorada quando `perfil=None`) e repassar o perfil a partir de `EspacoController`, `EquipamentoController` e das views.
4. **[Média — Performance]** Eliminar consulta N+1 de `_historico` dentro dos 50 expanders em `views/coordenador_view.py` (carregar histórico sob demanda — já entregue). *(Validação de horário no passado em `ReservaService` também concluída.)*
5. **[Baixa — Alinhamento RF40]** Definir se `curso` (em `perfil_view.py`) será editável ou removido. *(RF46/RN13 concluídos: `regras_especificas` exibidas no diálogo de reserva.)*

### Para Qualidade e Testes (Caio / `Solu-o`)
1. **[Concluído — PR `#1` e branch QA]** Método `atualizar_contato` integrado em `UsuarioService` e `UsuarioController`, garantindo compatibilidade com `views/perfil_view.py`.
2. **[Concluído — Limpeza e Segurança]** Arquivos legados `login.py` e `views/usuario_view.py` removidos definitivamente do repositório.
3. **[Concluído — Backend & Regras]** Validação de horário de funcionamento, mesmo dia e horário passado (`RN07`), restrição de auto-cadastro (`RN01`), detecção de conflitos ao criar bloqueios (`RN18`). A checagem de coordenador (`RN05`/`RN29`) está parcial: veja a pendência acima.
4. **[Concluído — Cobertura Automatizada]** Suíte de testes unitários expandida com 100% de aprovação no pytest.

### Para UX e Prototipação (Amadio)
1. **[Baixa]** Decidir o formato de avisos institucionais no banner inicial (`RF51`). *(A exibição de `regras_especificas` no modal de reserva — `RF46`/`RN13` — já foi entregue.)*

### Para o Product Owner (Ruy)
Decisões de produto que destravam as regras ainda pendentes (nenhuma é implementável sem um valor definido pela coordenação):

1. **[Alta — `RN08`]** Definir a duração máxima de uma reserva (ex.: 4 h) e se laboratórios têm limite diferente.
2. **[Alta — `RN09`]** Definir a antecedência mínima e máxima para solicitações (ex.: até 60 dias à frente).
3. **[Média — `RN12`]** Decidir se a reserva passa a informar o número de participantes para validar a capacidade.
4. **[Média — `RN14`]** Definir quais equipamentos exigem autorização e quem os autoriza.
5. **[Baixa — `RN06`]** Confirmar se há espaços exclusivos por perfil além dos usuários externos.
6. **[Baixa — `RF50`/`RF51`]** Priorizar a busca por intervalo início–fim e os avisos institucionais dinâmicos.
