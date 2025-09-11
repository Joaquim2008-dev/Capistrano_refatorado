import streamlit as st
from pages.visao_analitica import pagina_visao_analitica
from pages.visao_geografica import pagina_visao_geografica

st.set_page_config(
    page_title="Dashboard Escritório de Advocacia",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para estilização
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    
    /* Esconder navegação automática */
    .css-1d391kg {display: none;}
    .css-1rsyhoq {display: none;}
    section[data-testid="stSidebar"] > div:first-child {
        margin-top: 0px;
    }
    
    /* Esconder elementos de navegação padrão */
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Ajustar espaçamento */
    .css-1lcbmhc.e1fqkh3o0 {
        margin-top: 0px;
    }
    
    /* Estilização do login */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    .login-header p {
        color: #666;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

def verificar_credenciais(usuario, senha):
    """Verifica se as credenciais estão corretas usando secrets.toml"""
    try:
        # Acessar usuários do secrets.toml
        usuarios = st.secrets["usuarios"]
        
        # Verificar se usuário existe e senha está correta
        if usuario in usuarios:
            if usuarios[usuario]["senha"] == senha:
                return True, usuarios[usuario].get("nome_completo", usuario)
        
        return False, None
        
    except Exception as e:
        st.error(f"Erro ao verificar credenciais: {e}")
        return False, None

def tela_login():
    """Tela de login do sistema"""
    
    # Container centralizado para o login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <h1>⚖️ Escritório de Advocacia</h1>
                <p>Sistema de Análise de Processos</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulário de login
        with st.form("login_form"):
            st.markdown("### 🔐 Acesso ao Sistema")
            
            usuario = st.text_input(
                "👤 Usuário:",
                placeholder="Digite seu usuário",
                help="Use seu nome de usuário cadastrado"
            )
            
            senha = st.text_input(
                "🔑 Senha:",
                type="password",
                placeholder="Digite sua senha",
                help="Digite sua senha de acesso"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                submit_button = st.form_submit_button(
                    "🚀 Entrar no Sistema",
                    use_container_width=True,
                    type="primary"
                )
            
            if submit_button:
                if usuario and senha:
                    # Verificar credenciais
                    credenciais_validas, nome_completo = verificar_credenciais(usuario, senha)
                    
                    if credenciais_validas:
                        # Login bem-sucedido
                        st.session_state.autenticado = True
                        st.session_state.usuario = usuario
                        st.session_state.nome_completo = nome_completo
                        st.session_state.pagina_atual = "Visão Analítica"  # Página padrão
                        
                        st.success(f"✅ Bem-vindo, {nome_completo}!")
                        st.rerun()
                        
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
                        st.warning("💡 Verifique suas credenciais e tente novamente")
                        
                else:
                    st.warning("⚠️ Por favor, preencha usuário e senha")
        
        # Informações adicionais
        st.markdown("---")
        
        with st.expander("ℹ️ Informações do Sistema"):
            st.info("""
            **📊 Funcionalidades:**
            - Visão Analítica: KPIs e análises detalhadas
            - Visão Geográfica: Mapas e distribuição territorial
            
            **🔧 Suporte:**
            Entre em contato com o administrador do sistema para:
            - Criação de novo usuário
            - Recuperação de senha
            - Problemas técnicos
            """)

def sidebar_sistema():
    """Sidebar com menu do sistema (quando logado)"""
    with st.sidebar:
        st.title("⚖️ Escritório de Advocacia")
        
        # Informações do usuário logado
        st.markdown("---")
        st.markdown(f"👤 **Usuário:** {st.session_state.nome_completo}")
        st.markdown(f"🔑 **Login:** {st.session_state.usuario}")
        
        # Menu de navegação
        st.markdown("---")
        st.header("📋 Menu")
        
        # Inicializar página atual se não existir
        if 'pagina_atual' not in st.session_state:
            st.session_state.pagina_atual = "Visão Analítica"
        
        # Botões de navegação
        if st.button("📊\n**Visão**\n**Analítica**", 
                    use_container_width=True, 
                    type="primary" if st.session_state.pagina_atual == "Visão Analítica" else "secondary"):
            st.session_state.pagina_atual = "Visão Analítica"
        
        if st.button("🗺️\n**Visão**\n**Geográfica**", 
                    use_container_width=True, 
                    type="primary" if st.session_state.pagina_atual == "Visão Geográfica" else "secondary"):
            st.session_state.pagina_atual = "Visão Geográfica"
    
        st.markdown("---")
        
        # Botão de logout
        st.markdown("---")
        if st.button("🚪 **Sair do Sistema**", use_container_width=True, type="secondary"):
            # Limpar session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("👋 Logout realizado com sucesso!")
            st.rerun()
        
        # Informações do sistema
        with st.expander("🔧 Sistema"):
            st.caption("**SprintD Legis**")
            st.caption("Versão: Beta 1.0")
            st.caption("Última atualização: Junho 2025")
            st.caption("Desenvolvido para Escritório de Advocacia")

def main():
    """Função principal com controle de autenticação"""
    
    # Verificar se usuário está autenticado
    if not st.session_state.get("autenticado", False):
        # Usuário não logado - mostrar tela de login
        tela_login()
    else:
        # Usuário logado - mostrar sistema
        sidebar_sistema()
        
        # Routing das páginas
        try:
            if st.session_state.pagina_atual == "Visão Analítica":
                pagina_visao_analitica()
            elif st.session_state.pagina_atual == "Visão Geográfica":
                pagina_visao_geografica()
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar página: {e}")
            st.info("💡 Tente recarregar os dados ou contate o administrador.")

if __name__ == "__main__":
    main()