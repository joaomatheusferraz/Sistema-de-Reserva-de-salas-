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

#### Cenário 1.4: Prevenção de escalada de privilégio no auto-cadastro (`RN01` — pendência de segurança)
- **Dado** um novo usuário sem aprovação prévia da coordenação criando conta pela tela pública
- **Quando** finaliza o cadastro
- **Então** a conta não deve receber permissões administrativas ou privilégio de `professor` sem validação/aprovação institucional.

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
