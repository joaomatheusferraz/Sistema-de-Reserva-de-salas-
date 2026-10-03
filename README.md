# UniReserve — Sistema de Reserva de Salas

Aplicação web em **Python e Streamlit** para consultar espaços e organizar reservas de salas. A navegação considera diferentes perfis de usuário e reúne páginas de espaços, calendário, reservas e coordenação.

## Funcionalidades

- Consulta de espaços e calendário.
- Fluxo de reservas para perfis autorizados.
- Área de coordenação e serviços separados por responsabilidade.
- Persistência em Firestore com o Firebase Admin SDK.

## Tecnologias e organização

- **Interface:** Streamlit, com páginas em `views/`.
- **Regras e fluxos:** `domain/`, `controllers/` e `services/`.
- **Dados:** Firebase Admin SDK e Firestore.
- **Verificação:** testes em `tests/`.

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

Projeto de estudo em evolução. O código-fonte mostra a separação entre interface, regras, serviços e acesso aos dados.
