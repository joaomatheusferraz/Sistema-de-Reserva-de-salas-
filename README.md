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

1. Clone o repositório e crie um ambiente virtual Python:

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate   # No Linux/Mac: source .venv/bin/activate
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configuração do Firebase:**
   O sistema utiliza autenticação e Firestore. É possível configurar via:
   - **Arquivo local:** salve a chave de serviço em `secrets/key.json`.
   - **Streamlit Secrets:** copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha as credenciais.
   - **Variáveis de ambiente:**
     - `FIREBASE_WEB_API_KEY`: Chave de API Web do Firebase (para login e registro via REST).
     - `FIREBASE_SERVICE_ACCOUNT_JSON`: Conteúdo JSON da conta de serviço.

   > [!IMPORTANT]
   > Esses arquivos de credenciais são ignorados pelo Git; **nunca publique suas chaves**.

4. **Primeiro acesso de Coordenador:**
   Por segurança, o auto-cadastro na tela inicial permite apenas os perfis `Aluno` e `Usuário externo`. Para promover uma conta a `Coordenador`, altere o campo `perfil` do documento correspondente na coleção `usuarios` do Cloud Firestore para `"coordenador"`. A partir daí, o coordenador pode alterar perfis diretamente na interface.

5. **Executar testes automatizados:**

   ```bash
   python -m pytest
   ```

6. Inicie a aplicação:

   ```bash
   streamlit run main.py
   ```

## Cobertura de testes por requisito

Os testes em `tests/` citam no nome ou na docstring a regra de negócio (`RN`) ou o requisito funcional (`RF`) que verificam:

| Arquivo | Regras e requisitos verificados |
|---|---|
| `tests/test_regras_negocio.py` | RN01, RN04, RN11, RN15, RN17, RN19–RN25, RN27, RN28, RN30, RF25–RF27, RF39, RF53 |
| `tests/test_reserva_horarios.py` | RN02, RN07, RF19 |
| `tests/test_bloqueios.py` | RN05, RN18, RF36 |
| `tests/test_regras_espaco.py` | RN13, RF46 |
| `tests/test_services.py` | RN01, RN02, RN04, RN07, RN10, RN18, RN26, RN28, RN30, RF03 |

Projeto acadêmico em evolução (UNISAPIENS). O código-fonte evidencia a separação entre interface, regras de negócio, serviços e acesso aos dados.
