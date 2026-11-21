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
- [ ] **CA19** (`RN07`) — Reservas respeitam o horário de funcionamento (07h–23h), terminam no mesmo dia e não são criadas no passado.
- [ ] **CA20** (`RN13`, `RF46`) — As regras específicas do espaço são exibidas antes da confirmação da reserva.
- [ ] **CA13** (`RF04–RF09`, `RF48`, `RF50`) — Salas e laboratórios podem ser pesquisados e filtrados (nome, bloco, tipo, capacidade e disponibilidade).
- [ ] **CA14** (`RF49`) — Equipamentos podem ser utilizados como filtro de pesquisa.
- [ ] **CA15** (`RF52`, `RN29`) — Coordenadores conseguem cadastrar, editar e associar equipamentos aos espaços.
- [ ] **CA16** (`RF12–RF15`, `RF43`, `RF44`) — Os calendários (geral e da sala) apresentam corretamente horários ocupados, pendentes, bloqueados e livres.
- [ ] **CA17** (`RF54`) — Alunos conseguem pesquisar por professor, sala ou atividade para localizar onde ocorrerá uma aula.
- [ ] **CA18** (`RF25–RF27`, `RF51`, `RN23`) — Notificações são apresentadas aos usuários na tela inicial conforme os eventos da reserva.

---

## 2. Cenários de Aceitação Detalhados (Formato BDD: Dado / Quando / Então)

### Fluxo 1 — Autenticação, Recuperação de Senha e Perfil (`RF01–RF03`, `RF40–RF42`, `RN01`, `RN03`)

#### Cenário 1.1: Login com RA e senha válidos
- **Dado** um usuário ativo cadastrado com RA e e-mail vinculados ao Firebase Auth
- **Quando** informa RA e senha corretos na tela de login e clica em "Entrar"
- **Então** o sistema inicia a sessão e carrega apenas os itens de menu correspondentes ao seu perfil.

#### Cenário 1.2: Recuperação de senha sem vazamento de RAs cadastrados (`RF03`)
- **Dado** um usuário na tela de login que abre o diálogo "Esqueci minha senha"
- **Quando** informa um RA cadastrado ou um RA inexistente e envia o formulário
- **Então** o sistema exibe a mesma mensagem neutra de confirmação em ambos os casos, enviando o e-mail de redefinição apenas quando o RA existir e estiver ativo.

#### Cenário 1.3: Edição de e-mail e telefone no perfil (`RF41`)
- **Dado** um usuário autenticado na página "Meu perfil"
- **Quando** altera o e-mail ou telefone (com DDD válido) e salva
- **Então** o sistema atualiza o Firestore e sincroniza o novo e-mail no Firebase Auth, mantendo a sessão ativa com os dados atualizados.

#### Cenário 1.4: Prevenção de escalada de privilégio no auto-cadastro (`RN01` — implementado)
- **Dado** um novo usuário sem aprovação prévia da coordenação criando conta pela tela pública
- **Quando** finaliza o cadastro
- **Então** a conta não recebe permissões administrativas nem privilégio de `professor` sem validação/aprovação institucional: o cadastro público só aceita `aluno` e `externo` (verificado em `tests/test_services.py`).

---

### Fluxo 2 — Consulta e Localização de Aulas pelo Aluno (`RF04–RF09`, `RF12–RF15`, `RF43–RF44`, `RF53–RF54`, `RN30`)

#### Cenário 2.1: Aluno localiza sala de uma aula (`RF54`)
- **Dado** um usuário autenticado com perfil `aluno` e uma reserva confirmada do "Professor João" na "Sala 204" das `19:00` às `21:00`
- **Quando** acessa a página "Agenda" e pesquisa por "João" ou "Sala 204"
- **Então** o sistema exibe dia, horário, sala, professor responsável, atividade e situação `Confirmada`.

#### Cenário 2.2: Aluno impedido de reservar (`RF53`, `RN30`)
- **Dado** um usuário autenticado com perfil `aluno`
- **Quando** navega pelas páginas "Início" e "Salas" ou tenta acionar a camada de serviço para criar reserva
- **Então** nenhum botão de "Reservar" é exibido na interface e o serviço rejeita a operação com `PermissionError`.

#### Cenário 2.3: Visualização de janelas livres da sala (`RF12`, `RF15`, `RF44`)
- **Dado** a "Sala Amarela" com reservas `08:00–10:00` (Confirmada) e `13:00–15:00` (Pendente) em uma data
- **Quando** o usuário filtra a Agenda no modo `Dia` selecionando apenas a "Sala Amarela"
- **Então** o sistema exibe os intervalos livres (`07:00–08:00`, `10:00–13:00` e `15:00–23:00`) marcados como `Disponível`.

---

### Fluxo 3 — Solicitação, Edição e Cancelamento de Reservas (`RF16–RF27`, `RF47`, `RN02`, `RN04`, `RN10`, `RN16`, `RN19`, `RN21–RN28`)

#### Cenário 3.1: Solicitação de professor nasce Pendente e bloqueia temporariamente o horário (`RN21`, `RN24`, `RN25`, `RN27`)
- **Dado** um `professor` autenticado e o "Laboratório 02" livre no dia `10/10` das `19:00` às `21:00`
- **Quando** envia uma solicitação informando finalidade "Aula prática de programação"
- **Então** a reserva é salva com status `pendente`, gera registro no histórico e notificação ao professor, e uma segunda solicitação para o mesmo laboratório entre `20:00` e `22:00` é recusada por sobreposição.

#### Cenário 3.2: Horários adjacentes são permitidos (`RN02`, `RN10`)
- **Dado** a "Sala 204" reservada das `18:00` às `20:00`
- **Quando** um professor solicita a "Sala 204" no mesmo dia das `20:00` às `22:00`
- **Então** o sistema aceita a solicitação sem erro de conflito.

#### Cenário 3.3: Restrição de espaços para Usuário Externo (`RN28`, `RF55`)
- **Dado** um `externo` autorizado apenas para o espaço `Auditório`
- **Quando** tenta reservar o `Laboratório 02` (não autorizado)
- **Então** o card exibe "Sem autorização" (desabilitado) e o backend rejeita a tentativa com `PermissionError`.

#### Cenário 3.4: Professor não pode editar reserva já aprovada (`RN04`, `RF21`)
- **Dado** uma reserva de um professor cujo status já foi alterado para `reservada` (aprovada)
- **Quando** tenta editar a reserva em "Minhas reservas" ou diretamente no serviço
- **Então** o botão de editar fica desabilitado com orientação ao usuário e o serviço lança `PermissionError`.

#### Cenário 3.5: Cancelamento com confirmação libera o horário (`RF22`, `RF47`, `RN19`)
- **Dado** uma reserva ativa do professor
- **Quando** clica em cancelar e confirma no diálogo "Cancelar reserva?"
- **Então** o status muda para `cancelada`, registra histórico e notificação, e o horário volta a aceitar novas solicitações.

#### Cenário 3.6: Reserva fora do horário de funcionamento ou no passado (`RN07`, `RF19`)
- **Dado** um `professor` autenticado e a "Sala 204" livre
- **Quando** solicita uma reserva em horário já transcorrido, antes das `07:00`, depois das `23:00` ou começando em um dia e terminando em outro
- **Então** o serviço recusa a solicitação com mensagem clara, sem depender da validação da interface (verificado em `tests/test_reserva_horarios.py`).

#### Cenário 3.7: Regras do laboratório visíveis antes de confirmar (`RN13`, `RF46`)
- **Dado** o "Laboratório 02" com a regra específica "Usar jaleco" cadastrada
- **Quando** um professor abre o diálogo "Reservar sala" desse laboratório
- **Então** as regras de uso são exibidas antes do botão "Enviar solicitação".

---

### Fluxo 4 — Área do Coordenador, Aprovação, Bloqueios e Equipamentos (`RF32–RF39`, `RF52`, `RN05`, `RN17`, `RN18`, `RN20`, `RN26`, `RN29`, `RN31`)

#### Cenário 4.1: Reserva direta do coordenador (`RN26`)
- **Dado** um `coordenador` autenticado
- **Quando** realiza uma reserva para uma sala disponível
- **Então** a reserva já nasce com status `reservada` (`aprovacao_necessaria = False`), sem entrar na fila de pendentes.

#### Cenário 4.2: Aprovação de solicitação pendente (`RF39`, `RN20`, `RN23`, `RN25`)
- **Dado** uma solicitação `pendente` na fila da Área do coordenador
- **Quando** o coordenador clica em aprovar
- **Então** o status passa a `reservada`, a ação `aprovacao` é gravada no histórico e o solicitante recebe notificação `reserva_aprovada`.

#### Cenário 4.3: Rejeição exige motivo obrigatório e libera o horário (`RF39`, `RN19`, `RN20`, `RN23`)
- **Dado** uma solicitação `pendente` na fila da Área do coordenador
- **Quando** o coordenador tenta rejeitar sem preencher o motivo, o sistema recusa; quando informa o motivo e confirma
- **Então** o status passa a `rejeitada` com o motivo registrado, o horário volta a ficar disponível, o histórico grava `rejeicao` e o solicitante recebe notificação `reserva_rejeitada`.

#### Cenário 4.4: Bloqueio administrativo impede novas reservas e aprovações conflitantes (`RF36`, `RN17`, `RN18`, `RN31`)
- **Dado** um bloqueio ativo criado pelo coordenador para o "Laboratório 02" de `01/10` a `05/10` por motivo "Manutenção"
- **Quando** qualquer usuário tenta reservar ou editar uma reserva para esse período, **ou** o coordenador tenta aprovar uma solicitação pendente que colide com o bloqueio
- **Então** o sistema impede a operação informando que o espaço está bloqueado no período.

#### Cenário 4.5: Controle administrativo de equipamentos e espaços (`RF34`, `RF35`, `RF52`, `RN05`, `RN29`)
- **Dado** um usuário que **não** possui perfil `coordenador`
- **Quando** tenta cadastrar, editar ou desativar espaços ou equipamentos
- **Então** o acesso é negado tanto na interface quanto na camada de serviços. *(Nota: os serviços de espaço/equipamento rejeitam outros perfis quando o perfil é informado, mas as views ainda não o repassam; tornar a checagem obrigatória segue como pendência para Devs — ver `RN05`/`RN29` na matriz.)*

---

## 3. Roteiro Rápido de Homologação (Apresentação ao Reitor / Banca)

1. **Login e Visão do Coordenador:** entrar como `coordenador`, cadastrar 1 equipamento (ex.: `Projetor`) e 1 sala/laboratório associado a esse equipamento; criar 1 reserva direta e confirmar que nasce como `Confirmada`.
2. **Fluxo do Professor:** entrar como `professor`, filtrar a sala por capacidade + equipamento, solicitar reserva com finalidade e confirmar status `Pendente`.
3. **Prevenção de Conflito:** tentar solicitar o mesmo horário (ou parcial) com outro usuário e comprovar o bloqueio automático por sobreposição.
4. **Aprovação / Rejeição e Notificação:** voltar como `coordenador`, aprovar a solicitação (e testar uma rejeição com motivo); entrar novamente como `professor` e comprovar a notificação na tela inicial e o status `Confirmada`.
5. **Bloqueio Temporário:** como `coordenador`, bloquear a sala por manutenção e comprovar que ela aparece como `Bloqueado` na agenda e recusa novas reservas.
6. **Visão do Aluno:** entrar como `aluno`, pesquisar pelo nome do professor na Agenda para localizar a sala da aula e confirmar que não há opção de criar/editar/cancelar reservas.
