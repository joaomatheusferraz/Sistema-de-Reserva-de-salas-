# UniReserve — Sistema de Reserva de Salas (UNISAPIENS)

Aplicação web em **Python e Streamlit** desenvolvida na área de Sistemas de Informação da **UNISAPIENS** para consultar espaços e organizar reservas de salas e laboratórios. A navegação considera quatro perfis de usuário (`Aluno`, `Professor`, `Coordenador` e `Usuário externo`) e reúne páginas de início, espaços, agenda/calendário, minhas reservas, perfil e área do coordenador.

## Perfis de Usuário

| Perfil | Consultar espaços e agenda | Solicitar/fazer reserva | Precisa de aprovação |
|---|---|---|---|
| **Aluno** | Sim | Não | — |
| **Professor** | Sim | Sim | Sim |
| **Coordenador** | Sim | Sim | Não (reserva direta) |
| **Usuário externo** | Sim | Sim (espaços autorizados) | Sim |

## Funcionalidades do MVP

- Autenticação por RA e senha, recuperação de senha e gestão de perfil.
- Consulta de salas/laboratórios com filtros (capacidade, bloco, equipamentos, tipo e disponibilidade) e agenda geral/por sala.
- Fluxo de solicitações de reserva com finalidade, prevenção de conflitos (inclusive para pendentes) e aprovação/rejeição pela coordenação.
- Área administrativa do coordenador (aprovações, todas as reservas com histórico, bloqueios temporários, equipamentos e permissões de usuários).
- Notificações internas de reserva e persistência em Cloud Firestore com Firebase Admin SDK.

## Documentação de Requisitos e Aceitação

Toda a especificação funcional, regras de negócio, rastreabilidade com o código e critérios de aceitação estão versionados em `docs/`:

- [Especificação de Requisitos (Perfis, RF01–RF55, RN01–RN31 e Escopo MVP)](docs/requisitos.md)
- [Matriz de Rastreabilidade (RF/RN × Código × Lacunas Kanban)](docs/matriz_rastreabilidade.md)
- [Critérios de Aceitação (BDD) e Checklist de Homologação](docs/criterios_aceitacao.md)

## Tecnologias e organização

- **Interface:** Streamlit, com páginas em `views/` e estilos em `utils/estilo.py`.
- **Regras e fluxos:** `domain/`, `controllers/` e `services/`.
- **Dados:** Firebase Admin SDK e Cloud Firestore em `models/`.
- **Documentação:** Especificação, matriz de rastreabilidade e critérios de aceitação em `docs/`.
- **Verificação:** Testes automatizados em `tests/`.

## Executar localmente

1. Clone o repositório e crie um ambiente virtual Python.
2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure uma conta de serviço de um projeto Firebase com Firestore. O código lê o JSON pela variável de ambiente `FIREBASE_SERVICE_ACCOUNT_JSON`, pelos Secrets do Streamlit ou por `secrets/key.json` no ambiente local. Esses arquivos de credenciais são ignorados pelo Git; **não publique a chave**.
4. Inicie a aplicação:

   ```bash
   streamlit run main.py
   ```

Projeto acadêmico em evolução (UNISAPIENS). O código-fonte evidencia a separação entre interface, regras de negócio, serviços e acesso aos dados.
