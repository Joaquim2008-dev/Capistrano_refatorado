import streamlit as st

# CSS PARA ESTILIZAÇÃO
def criar_css():
     css = st.markdown("""
        <style>
            /* ===== LAYOUT GERAL ===== */
            .block-container { padding-top:2rem; }
            .st-emotion-cache-z5fcl4 { gap: 0.5rem; }
            #MainMenu { visibility: hidden; }

            /* Colunas para espaçamento dos cards */
            div[data-testid="column"] {
            padding:0 8px !important;
            min-width:0 !important;
            }
            div[data-testid="column"] > div {
            margin:0 !important;
            padding:0 !important;
            width:100% !important;
            min-width:0 !important;
            box-sizing:border-box !important;
            }

            /* ===== ESTILO DOS CARDS (BOTÕES POPOVER) - TAMANHO REDUZIDO ===== */
            button[kind="secondary"][data-testid="stPopoverButton"] {
            width:100% !important;
            max-width:100% !important;
            min-width:0 !important;
            box-sizing:border-box !important;
            margin:0 0 8px 0 !important;
            height:85px !important;
            padding:10px 8px !important;
            background:linear-gradient(145deg,#1e3a8a 0%,#3b82f6 100%) !important;
            border:1px solid #3b82f6 !important;
            border-radius:8px !important;
            box-shadow:0 3px 12px rgba(59, 130, 246, 0.3) !important;
            color:#ecf0f1 !important;
            display:flex !important;
            flex-direction:column !important;
            justify-content:center !important;
            align-items:center !important;
            gap:4px !important;
            text-align:center !important;
            font-size:11px !important;
            line-height:1.25 !important;
            font-weight:500 !important;
            white-space:pre-line !important;
            position:relative !important;
            overflow:hidden !important;
            cursor:pointer !important;
            }
            button[kind="secondary"][data-testid="stPopoverButton"]::before {
            content:'';
            position:absolute;
            top:0; left:8px; right:8px;
            height:2px;
            background:linear-gradient(90deg,#60a5fa,#3b82f6,#1e40af,#1d4ed8);
            border-radius:8px 8px 0 0;
            }
            button[kind="secondary"][data-testid="stPopoverButton"]:hover {
            transform:translateY(-1px) !important;
            box-shadow:0 4px 16px rgba(59, 130, 246, 0.4) !important;
            border-color:#60a5fa !important;
            background:linear-gradient(145deg,#3b82f6 0%,#1e3a8a 100%) !important;
            }
            
            button[kind="secondary"][data-testid="stPopoverButton"] p {
            margin:1px 0 !important;
            padding:0 !important;
            line-height:1.1 !important;
            }
            
            button[kind="secondary"][data-testid="stPopoverButton"] p:nth-of-type(1) {
            font-size:10px !important;
            margin-bottom:1px !important;
            font-weight:600 !important;
            color:#bdc3c7 !important;
            text-transform:uppercase !important;
            letter-spacing:0.5px !important;
            }
            button[kind="secondary"][data-testid="stPopoverButton"] p:nth-of-type(2) {
            font-size:18px !important;
            font-weight:700 !important;
            margin-bottom:1px !important;
            color:#ecf0f1 !important;
            text-shadow:0 1px 2px rgba(0,0,0,0.4) !important;
            }
                    
            button[kind="secondary"][data-testid="stPopoverButton"] svg {
            display:none !important;
            }

            
        </style>
        """, unsafe_allow_html=True)
     return css


'''


            /* ===== ESTILO DO POPOVER (CONTEÚDO ABERTO) ===== */
            div[role="dialog"][data-testid="stPopover"] {
            width:700px !important;
            min-width:700px !important;
            max-width:700px !important;
            height:600px !important;
            min-height:600px !important;
            max-height:85vh !important;    
            margin:0 auto !important;
            padding:0 !important;
            }
            div[role="dialog"][data-testid="stPopover"] > div {
            width:700px !important;
            max-width:700px !important;
            height:100% !important;
            min-height:100% !important;
            box-sizing:border-box !important;
            padding:18px 24px 26px 24px !important;
            }
            div[role="dialog"][data-testid="stPopover"] .element-container {
            width:100% !important;
            max-width:100% !important;
            }
            div[role="dialog"][data-testid="stPopover"] [data-baseweb="tab-list"] {
            flex-wrap:wrap;
            }
            @media (max-width:750px){
            div[role="dialog"][data-testid="stPopover"],
            div[role="dialog"][data-testid="stPopover"] > div {
                width:95vw !important;
                min-width:95vw !important;
                max-width:95vw !important;
                height:90vh !important;
                min-height:90vh !important;
                max-height:90vh !important;
                padding:14px 16px 22px 16px !important;
            }
            

'''