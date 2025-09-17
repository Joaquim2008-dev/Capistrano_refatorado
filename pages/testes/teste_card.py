import streamlit as st

st.set_page_config(page_title="Teste Card - Concentração", layout="wide")

# Original (Bege suave - sem fundo) — texto mais claro, números em destaque
st.markdown("""
    <div style="padding:10px 16px;display:flex;align-items:center;gap:24px;
                color:#7b6654;font-size:14px;">
        <div><span style="color:#d35400;font-weight:700;">50%</span> dos clientes estão entre <span style="color:#d35400;font-weight:700;">51</span> e <span style="color:#d35400;font-weight:700;">72</span> anos</div>
        <div style="border-left:1px solid rgba(123,102,84,0.12);padding-left:16px;">
            <span style="color:#d35400;font-weight:700;">80%</span> dos clientes estão entre <span style="color:#d35400;font-weight:700;">38</span> e <span style="color:#d35400;font-weight:700;">77</span> anos
        </div>
        <div style="border-left:1px solid rgba(123,102,84,0.12);padding-left:16px;">Mediana: <span style="color:#d35400;font-weight:700;">64 anos</span></div>
        <div style="border-left:1px solid rgba(123,102,84,0.12);padding-left:16px;">Faixa mais comum: <span style="color:#d35400;font-weight:700;">71 a 76 anos</span></div>
    </div>
""", unsafe_allow_html=True)

st.markdown("## Variantes de cor (apenas para teste)")

# Variante 1 — Azul / turquesa (texto mais claro, números turquesa)
st.markdown("""
    <div style="padding:8px 16px;display:flex;align-items:center;gap:20px;
                color:#6a7b7b;font-size:14px;">
        <div><span style="color:#0fa3a3;font-weight:700;">50%</span> dos clientes estão entre <span style="color:#0fa3a3;font-weight:700;">51</span> e <span style="color:#0fa3a3;font-weight:700;">72</span> anos</div>
        <div style="border-left:1px solid rgba(106,123,123,0.12);padding-left:12px;">
            <span style="color:#0fa3a3;font-weight:700;">80%</span> dos clientes estão entre <span style="color:#0fa3a3;font-weight:700;">38</span> e <span style="color:#0fa3a3;font-weight:700;">77</span> anos
        </div>
        <div style="border-left:1px solid rgba(106,123,123,0.12);padding-left:12px;">Mediana: <span style="color:#0fa3a3;font-weight:700;">64 anos</span></div>
        <div style="border-left:1px solid rgba(106,123,123,0.12);padding-left:12px;">Faixa mais comum: <span style="color:#0fa3a3;font-weight:700;">71 a 76 anos</span></div>
    </div>
""", unsafe_allow_html=True)

# Variante 2 — Verde suave (texto mais claro, números verde-escuro)
st.markdown("""
    <div style="padding:8px 16px;display:flex;align-items:center;gap:20px;
                color:#6b7a70;font-size:14px;">
        <div><span style="color:#1f7a4a;font-weight:700;">50%</span> dos clientes estão entre <span style="color:#1f7a4a;font-weight:700;">51</span> e <span style="color:#1f7a4a;font-weight:700;">72</span> anos</div>
        <div style="border-left:1px solid rgba(107,122,112,0.12);padding-left:12px;">
            <span style="color:#1f7a4a;font-weight:700;">80%</span> dos clientes estão entre <span style="color:#1f7a4a;font-weight:700;">38</span> e <span style="color:#1f7a4a;font-weight:700;">77</span> anos
        </div>
        <div style="border-left:1px solid rgba(107,122,112,0.12);padding-left:12px;">Mediana: <span style="color:#1f7a4a;font-weight:700;">64 anos</span></div>
        <div style="border-left:1px solid rgba(107,122,112,0.12);padding-left:12px;">Faixa mais comum: <span style="color:#1f7a4a;font-weight:700;">71 a 76 anos</span></div>
    </div>
""", unsafe_allow_html=True)

# Variante 3 — Lavanda (texto mais claro, números magenta)
st.markdown("""
    <div style="padding:8px 16px;display:flex;align-items:center;gap:20px;
                color:#7a6e81;font-size:14px;">
        <div><span style="color:#a9007a;font-weight:700;">50%</span> dos clientes estão entre <span style="color:#a9007a;font-weight:700;">51</span> e <span style="color:#a9007a;font-weight:700;">72</span> anos</div>
        <div style="border-left:1px solid rgba(122,110,129,0.12);padding-left:12px;">
            <span style="color:#a9007a;font-weight:700;">80%</span> dos clientes estão entre <span style="color:#a9007a;font-weight:700;">38</span> e <span style="color:#a9007a;font-weight:700;">77</span> anos
        </div>
        <div style="border-left:1px solid rgba(122,110,129,0.12);padding-left:12px;">Mediana: <span style="color:#a9007a;font-weight:700;">64 anos</span></div>
        <div style="border-left:1px solid rgba(122,110,129,0.12);padding-left:12px;">Faixa mais comum: <span style="color:#a9007a;font-weight:700;">71 a 76 anos</span></div>
    </div>
""", unsafe_allow_html=True)

# Variante 4 — Cinza frio (texto mais claro, números azul-escuro)
st.markdown("""
    <div style="padding:8px 16px;display:flex;align-items:center;gap:20px;
                color:#787c7f;font-size:14px;">
        <div><span style="color:#0b5394;font-weight:700;">50%</span> dos clientes estão entre <span style="color:#0b5394;font-weight:700;">51</span> e <span style="color:#0b5394;font-weight:700;">72</span> anos</div>
        <div style="border-left:1px solid rgba(120,124,127,0.12);padding-left:12px;">
            <span style="color:#0b5394;font-weight:700;">80%</span> dos clientes estão entre <span style="color:#0b5394;font-weight:700;">38</span> e <span style="color:#0b5394;font-weight:700;">77</span> anos
        </div>
        <div style="border-left:1px solid rgba(120,124,127,0.12);padding-left:12px;">Mediana: <span style="color:#0b5394;font-weight:700;">64 anos</span></div>
        <div style="border-left:1px solid rgba(120,124,127,0.12);padding-left:12px;">Faixa mais comum: <span style="color:#0b5394;font-weight:700;">71 a 76 anos</span></div>
    </div>
""", unsafe_allow_html=True)

# Variante 5 — Terracota suave (texto mais claro, números terracota)
st.markdown("""
    <div style="padding:8px 16px;display:flex;align-items:center;gap:20px;
                color:#8a7b73;font-size:14px;">
        <div><span style="color:#c75a2b;font-weight:700;">50%</span> dos clientes estão entre <span style="color:#c75a2b;font-weight:700;">51</span> e <span style="color:#c75a2b;font-weight:700;">72</span> anos</div>
        <div style="border-left:1px solid rgba(138,123,115,0.12);padding-left:12px;">
            <span style="color:#c75a2b;font-weight:700;">80%</span> dos clientes estão entre <span style="color:#c75a2b;font-weight:700;">38</span> e <span style="color:#c75a2b;font-weight:700;">77</span> anos
        </div>
        <div style="border-left:1px solid rgba(138,123,115,0.12);padding-left:12px;">Mediana: <span style="color:#c75a2b;font-weight:700;">64 anos</span></div>
        <div style="border-left:1px solid rgba(138,123,115,0.12);padding-left:12px;">Faixa mais comum: <span style="color:#c75a2b;font-weight:700;">71 a 76 anos</span></div>
    </div>
""", unsafe_allow_html=True)