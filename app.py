import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
import re
from itertools import combinations
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Conciliador Seguro", 
    page_icon="🛡️", 
    layout="wide"
)

# --- INSERÇÃO DO GOOGLE ANALYTICS ---
# O script é inserido via markdown para rastrear acessos no domínio .streamlit.app
st.markdown(
    """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-FZ55YE6JGV"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-FZ55YE6JGV');
    </script>
    """,
    unsafe_allow_html=True
)

# --- FUNÇÕES DE SEGURANÇA E CÁLCULO ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def parse_and_clean_numbers(raw_text: str):
    """
    Sanitização de Input: Extrai apenas números positivos.
    Previne injeção de scripts e limpa formatações como 'R$' ou espaços.
    """
    if not raw_text: return []
    text_cleaned = raw_text.replace(',', '.')
    # Regex para capturar apenas padrões numéricos válidos
    potential_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text_cleaned)
    
    valid_numbers = []
    for num_str in potential_numbers:
        try:
            val = float(num_str)
            if 0 < val < 1000000000: # Limite de segurança contra números astronômicos
                valid_numbers.append(val)
        except ValueError: continue
    return valid_numbers

def find_subset_sum(numbers, target, max_len, progress_bar, status_text):
    """
    Algoritmo de análise combinatória com trava de segurança de 60 segundos.
    """
    start_time = time.time()
    MAX_WAIT = 60 

    for r in range(1, max_len + 1):
        # Proteção contra travamento do servidor (DoS acidental)
        if time.time() - start_time > MAX_WAIT:
            st.error(f"⚠️ **Busca interrompida.** O cálculo excedeu o limite de segurança de {MAX_WAIT}s.")
            return "timeout"
            
        status_text.text(f"🔍 Analisando combinações de {r} nota(s)...")
        progress_bar.progress(r / max_len)
        
        for combo in combinations(numbers, r):
            if sum(combo) == target:
                st.session_state.tempo = time.time() - start_time
                return list(combo)
    return None

# --- ESTILIZAÇÃO INTERFACE ---
st.markdown("""
    <style>
    .stCard { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #eee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Filtros e Segurança")
    max_depth = st.slider(
        "Profundidade Máxima", 1, 20, 12, 
        help="Define quantas notas o sistema pode somar entre si para chegar ao resultado."
    )
    st.divider()
    st.info("💡 Dica: Se não encontrar resultados, verifique os centavos ou aumente a profundidade.")

# --- NAVEGAÇÃO PRINCIPAL ---
selected = option_menu(
    menu_title=None, 
    options=["Conciliador", "Sobre"], 
    icons=["calculator", "info-circle"], 
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "nav-link-selected": {"background-color": "#007BFF"}
    }
)

if selected == "Conciliador":
    st.title("⚖️ Conciliador Financeiro Seguro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            target_val = st.number_input("Valor Total do Depósito (R$)", min_value=0.00, format="%.2f")
            notes_raw = st.text_area("Lista de Notas em Aberto", height=200, placeholder="Cole aqui os valores das notas (um por linha ou separados por espaço)")
            
            valid_notes = parse_and_clean_numbers(notes_raw)
            if valid_notes:
                st.caption(f"✅ **{len(valid_notes)}** notas identificadas com sucesso.")

            if st.button("🚀 Iniciar Conciliação Inteligente", use_container_width=True):
                if not valid_notes or target_val <= 0:
                    st.warning("⚠️ Por favor, insira o valor do depósito e pelo menos uma nota válida.")
                else:
                    # Cálculo em centavos (inteiros) para evitar erros de ponto flutuante
                    target_int = int(round(target_val * 100))
                    notes_int = [int(round(n * 100)) for n in valid_notes]
                    
                    p_bar = st.progress(0)
                    s_msg = st.empty()
                    
                    res = find_subset_sum(notes_int, target_int, max_depth, p_bar, s_msg)
                    
                    p_bar.empty()
                    s_msg.empty()
                    
                    if res == "timeout":
                        pass
                    elif res:
                        st.balloons()
                        st.success(f"### 🎉 Combinação encontrada em {st.session_state.tempo:.2f}s!")
                        final_res = [x / 100 for x in res]
                        st.write("**Notas identificadas:**")
                        st.dataframe(
                            final_res, 
                            column_config={"value": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")},
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Nenhuma combinação encontrada. Verifique se falta alguma nota ou aumente a Profundidade Máxima na lateral.")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("🔒 Camadas de Proteção")
        st.markdown("""
        * **Sanitização:** Bloqueio automático de caracteres não numéricos.
        * **Timeout:** Otimização para não sobrecarregar o navegador/servidor.
        * **Privacidade:** Os dados são voláteis (não salvos em banco de dados).
        """)
        st.image("https://cdn-icons-png.flaticon.com/512/1162/1162456.png", width=100)

# --- ABA SOBRE ---
else:
    st.title("📖 Sobre o Projeto")
    st.divider()
    
    col_sobre, col_img = st.columns([1.5, 1])
    
    with col_sobre:
        st.markdown("""
        ### 🎯 Objetivo
        Esta ferramenta foi criada para automatizar o fechamento de caixa e conciliação bancária. 
        Muitas vezes, um depósito engloba várias notas, e descobrir manualmente quais são pode levar horas.
        
        ### 🧠 Lógica de Processamento
        O sistema utiliza **análise combinatória exata**. Para garantir precisão de 100%:
        1. Converte todos os valores para centavos (inteiros).
        2. Testa combinações matemáticas baseadas na profundidade escolhida.
        3. Retorna a primeira soma exata encontrada.
        """)

    with col_img:
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 25px; border-radius: 15px; border: 1px solid #ddd;">
            <h4 style="margin-top:0;">👨‍💻 Desenvolvedor</h4>
            <p><strong>Rafael (Taff4)</strong></p>
            <p style="font-size: 0.9em;">Especialista em automação de processos financeiros e desenvolvimento Python.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") 
        st.link_button("🌐 Ver Código no GitHub", "https://github.com/Taff4/conciliador-notas", use_container_width=True)

    st.divider()
    st.subheader("❓ Perguntas Frequentes")
    
    with st.expander("🛡️ Meus dados financeiros estão expostos?"):
        st.write("Não. O Streamlit Cloud processa os dados em memória RAM temporária. Assim que você atualiza a página ou fecha a aba, os dados são destruídos.")
        
    with st.expander("⚡ Por que existe um limite de 60 segundos?"):
        st.write("Combinações matemáticas crescem exponencialmente. Sem um limite de tempo, uma lista muito grande poderia travar sua aba do navegador ou consumir recursos excessivos do servidor gratuito.")
