import streamlit as st


def home_view(usuario):
    nome = usuario.get("nome", "Carlos Silva")
    perfil = usuario.get("perfil", "Coordenador")

    st.title("Início")
    st.caption(f"Bem-vindo, {nome} · Perfil: {perfil}")

    st.info("Acompanhe suas reservas em um só lugar.")

    cards = [
        ("Reservar Sala", "#2bb673"),
        ("Minhas Reservas", "#2e77d9"),
        ("Área do Coordenador", "#ea4c4c"),
    ]

    for texto, cor in cards:
        st.markdown(
            f"""
            <div style='
                display:flex;
                align-items:center;
                justify-content:space-between;
                background: rgba(255,255,255,0.8);
                border: 1px solid rgba(15,23,42,0.08);
                border-radius: 12px;
                padding: 0.9rem 1rem;
                margin-top: 0.8rem;
                min-height: 70px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            '>
                <div style='font-size: 1.08rem; font-weight: 700; color: #1d2430;'>{texto}</div>
                <div style='width: 18px; height: 18px; border-radius: 6px; background: {cor};'></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
