"""Estilo visual do UniReserve, seguindo o protótipo do Figma.

O tema (cores, fonte, barra lateral roxa) fica em .streamlit/config.toml.
Este CSS cobre só o que o tema não alcança: barra superior branca, cards
brancos sobre o fundo cinza, faixas de status dos cards de sala, banner da
tela inicial e cores específicas de alguns botões.

Os seletores usam as classes ``st-key-<key>`` que o Streamlit gera para
containers e widgets com ``key``; por isso as telas usam prefixos de chave
como ``card_``, ``faixa_verde_`` ou ``aprovar_``.
"""

import streamlit as st

CSS = """
<style>
:root {
  --ur-card: #FFFFFF;
  --ur-borda: #E2E8F0;
  --ur-texto-suave: #64748B;
  --ur-azul: #2563EB;
  --ur-azul-escuro: #1E3A5F;
  --ur-roxo: #5B2380;
}

/* ---------- Estrutura ---------- */
header[data-testid="stHeader"] { background: transparent; height: 0; overflow: visible; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stMainBlockContainer"] {
  padding: 0 2.25rem 3rem !important;
  max-width: none;
}

/* Barra lateral: itens maiores, ícones brancos e "Configurações" no rodapé */
section[data-testid="stSidebar"] { min-width: 290px !important; max-width: 290px !important; }
[data-testid="stSidebarHeader"] { padding-top: 1.6rem; padding-bottom: 1.6rem; }
[data-testid="stSidebarHeader"] img { height: 2.4rem !important; max-width: 100%; }
[data-testid="stSidebarNav"] ul { gap: .55rem; display: flex; flex-direction: column; }
[data-testid="stSidebarNavLink"] { padding: .55rem 1rem; border-radius: 8px; }
[data-testid="stSidebarNavLink"] span { color: #FFFFFF !important; font-size: 15.5px; }
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] { color: #FFFFFF; font-size: 1.4rem; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: rgba(255,255,255,.14); }
[data-testid="stSidebarNavLink"][aria-current="page"] span { font-weight: 600; }
[data-testid="stSidebarNavSeparator"] { display: none; }
[data-testid="stSidebarContent"] { display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] { margin-top: auto; padding-bottom: 1.25rem; }
.st-key-link_config a span { font-style: italic; color: #FFFFFF !important; font-size: 15.5px; }
.st-key-link_config [data-testid="stIconMaterial"] { color: #FFFFFF; font-size: 1.4rem; }

/* ---------- Barra superior ---------- */
/* O Streamlit embrulha cada container num stLayoutWrapper; a largura
   precisa ser ajustada nele para a barra ocupar a tela toda. */
[data-testid="stLayoutWrapper"]:has(> .st-key-topo) {
  margin: 0 -2.25rem 1.5rem -2.25rem;
  width: calc(100% + 4.5rem);
  max-width: none;
}
.st-key-topo {
  background: var(--ur-card);
  padding: .55rem 1.5rem .55rem 2.25rem;
  border-bottom: 1px solid var(--ur-borda);
}
/* No Streamlit Cloud a barra de ferramentas (Share, estrela, GitHub) ficava
   no canto superior direito, por cima do nome do usuário. Ela vai para o
   canto inferior direito, logo acima do botão "Manage app" do Cloud. */
[data-testid="stToolbar"] {
  position: fixed !important; top: auto !important; left: auto !important;
  right: 1rem !important; bottom: 4rem !important; z-index: 999990;
  /* O Streamlit dá width/height 100% à barra; com position fixed e fundo
     branco ela cobria a tela inteira no Cloud (tela branca). */
  width: auto !important; height: auto !important;
}
[data-testid="stToolbar"]:has([data-testid="stToolbarActions"] :is(button, a)) {
  background: #FFFFFF; border: 1px solid var(--ur-borda); border-radius: 10px;
  padding: 2px 6px; box-shadow: 0 4px 14px rgba(15, 23, 42, .12);
}
.ur-topo-texto { display: flex; flex-direction: column; line-height: 1.3; color: #1F2937; }
.ur-topo-texto small { font-size: 12.5px; color: var(--ur-texto-suave); }
.ur-topo-texto strong { font-size: 15px; font-weight: 700; }
.ur-topo-texto strong.grande { font-size: 19px; font-weight: 600; }
.ur-topo-texto.direita { text-align: right; }
.st-key-topo_avatar button {
  width: 44px; height: 44px; min-height: 44px; padding: 0; border-radius: 50% !important;
  background: var(--ur-roxo); border: 2px solid #FFFFFF; box-shadow: 0 0 0 1px var(--ur-borda);
}
.st-key-topo_avatar button p { color: #FFFFFF; font-weight: 700; font-size: 15px; }
.st-key-topo_avatar button:hover { background: #4A1B69; }

/* ---------- Cards brancos ---------- */
[class*="st-key-card"] {
  background: var(--ur-card);
  border: 1px solid var(--ur-borda);
  border-radius: 12px;
  padding: 1.25rem 1.4rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
}
.st-key-card_tabela, .st-key-card_pendentes { padding: 1.25rem 1.4rem 1rem; }
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-titulo_card"]) {
  margin: -1.25rem -1.4rem .9rem; width: calc(100% + 2.8rem); max-width: none;
}
[class*="st-key-titulo_card"] { border-bottom: 1px solid var(--ur-borda); padding: 1.1rem 1.4rem; }
/* Badges de status em formato de pílula, como no protótipo */
[class*="st-key-linha_"] .stMarkdownBadge { border-radius: 999px !important; padding: 4px 12px !important; font-weight: 600 !important; font-size: 13.5px !important; }

/* Tabelas montadas com colunas */
[class*="st-key-cabecalho_tabela"] {
  background: #F3F6FA; border-radius: 6px; padding: .55rem .9rem;
}
[class*="st-key-cabecalho_tabela"] p { font-weight: 700; font-size: 14px; }
[class*="st-key-cabecalho_tabela"].pequeno p { font-size: 12.5px; }
[class*="st-key-linha_"] {
  border-bottom: 1px solid var(--ur-borda); padding: .35rem .9rem;
}
[class*="st-key-linha_"] [data-testid="stMarkdownContainer"] p { font-size: 14.5px; }
[class*="st-key-linha_"] [data-testid="stColumn"] { justify-content: center; }

/* ---------- Banner da tela inicial ---------- */
.st-key-banner {
  background:
    radial-gradient(circle at 104% 140%, rgba(255,255,255,.14) 0 30%, transparent 30.2%),
    radial-gradient(circle at 92% 46%, rgba(255,255,255,.08) 0 34%, transparent 34.2%),
    #1E4B9B;
  border-radius: 12px; padding: 2.6rem 2rem 1.1rem; min-height: 270px;
}
.st-key-banner h2 { color: #FFFFFF; font-size: 36px; font-weight: 800; padding: 0; }
.st-key-banner p { color: #E8EEFA; font-size: 16.5px; }
.st-key-banner_icone {
  background: rgba(255,255,255,.18); border-radius: 18px;
  align-items: center; justify-content: center;
}
[data-testid="stLayoutWrapper"]:has(> .st-key-banner_icone) { margin-right: 9%; }
.ur-icone.ur-icone-banner { font-size: 68px; color: #FFFFFF; display: block; }
.st-key-banner_nav { background: #13305F; border-radius: 999px; padding: 2px 8px; }
.st-key-banner_nav button { min-height: 28px; height: 28px; padding: 0 8px; }
.st-key-banner_nav button p { color: #FFFFFF; font-size: 13px; margin: 0; }
.st-key-banner_nav button [data-testid="stIconMaterial"] { color: #FFFFFF; }
.ur-pontos { display: flex; gap: 6px; align-items: center; height: 28px; }
.ur-pontos span { width: 7px; height: 7px; border-radius: 99px; background: rgba(255,255,255,.55); }
.ur-pontos span.ativo { width: 28px; background: #FFFFFF; }

/* Atalhos grandes da tela inicial */
[class*="st-key-acao_"] button {
  background: var(--ur-card); border: 1px solid var(--ur-borda); min-height: 98px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .04); gap: .9rem;
}
[class*="st-key-acao_"] button:hover { border-color: #CBD5E1; background: #FAFBFD; }
[class*="st-key-acao_"] button p { font-size: 16.5px; font-weight: 700; color: #1F2937; }
[class*="st-key-acao_"] button [data-testid="stIconMaterial"] {
  color: #FFFFFF; font-size: 26px; padding: 12px; border-radius: 8px; box-sizing: content-box;
  margin-right: 1rem;
}
.st-key-acao_salas button [data-testid="stIconMaterial"] { background: #22C55E; }
.st-key-acao_minhas button [data-testid="stIconMaterial"] { background: #2F6BD8; }
.st-key-acao_coordenador button [data-testid="stIconMaterial"] { background: #E5484D; }
.st-key-acao_agenda button [data-testid="stIconMaterial"] { background: #7C3AED; }

/* ---------- Cards de sala ---------- */
[class*="st-key-sala_"] {
  background: var(--ur-card); border: 1px solid var(--ur-borda); border-radius: 12px;
  overflow: hidden; gap: 0; height: 100%;
}
[class*="st-key-faixa_"] { padding: .55rem 1rem; }
[class*="st-key-faixa_"] p { font-weight: 600; font-size: 14px; }
[class*="st-key-faixa_verde"] { background: #E8F5EC; }
[class*="st-key-faixa_verde"] p { color: #15803D; }
[class*="st-key-faixa_vermelho"] { background: #FDECEC; }
[class*="st-key-faixa_vermelho"] p { color: #DC2626; }
[class*="st-key-faixa_laranja"] { background: #FEF3E2; }
[class*="st-key-faixa_laranja"] p { color: #B45309; }
[class*="st-key-faixa_cinza"] { background: #E5E7EB; }
[class*="st-key-faixa_cinza"] p { color: #374151; }
[class*="st-key-corpo_"] { padding: .9rem 1rem 1rem; gap: .35rem; }
.ur-sala-titulo { display: flex; justify-content: space-between; align-items: baseline; gap: .5rem; }
.ur-sala-titulo strong { font-size: 16px; font-weight: 700; color: #1F2937; line-height: 1.3; }
.ur-sala-titulo span { font-size: 13.5px; color: var(--ur-texto-suave); white-space: nowrap; }
[class*="st-key-corpo_"] [data-testid="stCaptionContainer"] p { font-size: 14px; }
.ur-equip { font-size: 11.5px; font-weight: 600; letter-spacing: .02em; color: #1F2937; margin-top: .4rem; }
.ur-equip-itens { display: flex; flex-wrap: wrap; gap: .35rem .9rem; font-size: 12.5px; color: #374151; }
.ur-equip-itens span { display: inline-flex; align-items: center; gap: 4px; }
.ur-icone { font-family: "Material Symbols Rounded"; font-size: 15px; line-height: 1; font-weight: 400; }
[class*="st-key-reservar_"] button { background: #2F6BB8; border-color: #2F6BB8; }
[class*="st-key-reservar_"] button:hover { background: #255A9C; border-color: #255A9C; }
[class*="st-key-reservar_ocupada"] button { background: #4B5563; border-color: #4B5563; }
[class*="st-key-reservar_ocupada"] button:hover { background: #374151; border-color: #374151; }

/* Barra de busca + filtros avançados */
.st-key-btn_filtros button { background: var(--ur-azul-escuro); border-color: var(--ur-azul-escuro); min-height: 44px; }
.st-key-btn_filtros button:hover { background: #15304F; border-color: #15304F; }
.st-key-busca_salas input { min-height: 44px; }

/* ---------- Área do coordenador ---------- */
[class*="st-key-card_metrica"] [data-testid="stCaptionContainer"] p { font-size: 16px; color: #4B5563; }
[class*="st-key-card_metrica"] h2 { font-size: 38px; font-weight: 800; padding: .1rem 0 .3rem; }
[class*="st-key-aprovar_"] button, [class*="st-key-rejeitar_"] button {
  min-width: 38px; width: auto; height: 32px; min-height: 32px; padding: 0 10px; border: none; border-radius: 6px;
}
[class*="st-key-aprovar_"] button { background: #22C55E; }
[class*="st-key-aprovar_"] button:hover { background: #16A34A; }
[class*="st-key-rejeitar_"] button { background: #EF4444; }
[class*="st-key-rejeitar_"] button:hover { background: #DC2626; }
[class*="st-key-aprovar_"] button p, [class*="st-key-rejeitar_"] button p {
  color: #FFFFFF !important; font-size: 13px; font-weight: 600; margin: 0;
}
[class*="st-key-aprovar_"] [data-testid="stIconMaterial"],
[class*="st-key-rejeitar_"] [data-testid="stIconMaterial"] { color: #FFFFFF; font-size: 18px; }

/* Avatares com iniciais */
.ur-pessoa { display: flex; align-items: center; gap: 10px; }
.ur-avatar {
  display: inline-flex; align-items: center; justify-content: center; flex: none;
  border-radius: 50%; color: #FFFFFF; font-weight: 700;
}

/* ---------- Minhas reservas ---------- */
[class*="st-key-tab_"] button {
  min-width: 34px; width: auto; height: 32px; min-height: 32px; padding: 0 8px; background: #FFFFFF;
}
[class*="st-key-tab_"] button p { font-size: 13px; margin: 0; }
[class*="st-key-pagina_"] button { min-width: 34px; height: 32px; min-height: 32px; padding: 0 8px; }

/* ---------- Meu perfil ---------- */
.st-key-voltar button { padding: 0; min-height: 36px; }
.st-key-voltar [data-testid="stIconMaterial"] { font-size: 26px; color: #1F2937; }
.ur-campo-rotulo { font-size: 12.5px; color: var(--ur-texto-suave); margin: 0; }
.ur-campo-valor { font-size: 16px; font-weight: 500; margin: 0 0 .7rem; color: #1F2937; }
[class*="st-key-perfil_acao"] button {
  border: 1.5px solid #2F6BB8; color: #2F6BB8; background: #FFFFFF; min-height: 42px;
}
[class*="st-key-perfil_acao"] button p, [class*="st-key-perfil_acao"] [data-testid="stIconMaterial"] { color: #2F6BB8; font-weight: 600; }
[class*="st-key-perfil_acao"] button:hover { background: #F0F5FC; }
.st-key-perfil_sair button { background: #E5383B; border-color: #E5383B; min-height: 42px; }
.st-key-perfil_sair button:hover { background: #C92A2D; border-color: #C92A2D; }

/* ---------- Responsividade e Acessibilidade (H8 / WCAG) ---------- */
@media (max-width: 768px) {
  [data-testid="stMainBlockContainer"] {
    padding: 0 1rem 2rem !important;
  }
  [data-testid="stLayoutWrapper"]:has(> .st-key-topo) {
    margin: 0 -1rem 1rem -1rem;
    width: calc(100% + 2rem);
  }
  .st-key-topo {
    padding: .5rem 1rem;
  }
  .st-key-banner {
    padding: 1.5rem 1.25rem 1rem;
    min-height: auto;
  }
  .st-key-banner h2 {
    font-size: 24px;
  }
  .st-key-banner p {
    font-size: 14px;
  }
  [class*="st-key-aprovar_"] button, [class*="st-key-rejeitar_"] button,
  [class*="st-key-tab_"] button {
    min-height: 44px;
    min-width: 44px;
  }
}

@media (max-width: 1024px) {
  section[data-testid="stSidebar"] {
    min-width: 240px !important;
    max-width: 240px !important;
  }
}
</style>
"""


def aplicar_estilo():
    st.html(CSS)
