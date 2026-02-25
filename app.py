import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
import re
from itertools import combinations
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliador Seguro", page_icon="🛡️", layout="wide")

# --- FUNÇÕES DE SEGURANÇA E CÁLCULO ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5) # Timeout para evitar travamento na carga
        return r.json() if r.status_code == 200 else None
    except:
        return None

def parse_and_clean_numbers(raw_text: str):
    """
    Sanitização de Input: Extrai apenas números positivos.
    Previne que textos maliciosos ou caracteres estranhos entrem no loop.
    """
    if not raw_text: 
        return []
    # Substitui vírgula por ponto e limpa caracteres que não sejam números ou ponto
    text_cleaned = raw_text.replace(',', '.')
    # Regex rigoroso: apenas dígitos seguidos opcionalmente por ponto e mais dígitos
    potential_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text_cleaned)
    
    valid_numbers = []
    for num_str in potential_numbers:
        try:
            val = float(num_str)
            if 0 < val < 1000000000: # Limite de 1 bilhão por nota (segurança de overflow)
                valid_numbers.append(val)
        except ValueError: 
            continue
    return valid_numbers

def find_subset_sum(numbers, target, max_len, progress_bar, status_text):
    """
    Cálculo com trava de segurança (Timeout de 60 segundos)
    """
    start_time = time.time()
    MAX_WAIT = 60  # Limite de segurança em segundos

    for r in range(1, max_len + 1):
        # Verifica se estourou o tempo de segurança
        if time.time() - start_time > MAX_WAIT:
            st.error(f"⚠️ **Busca interrompida por segurança.** O cálculo excedeu {MAX_WAIT}s. Tente diminuir a 'Profundidade da Busca'.")
            return "timeout"
            
        status_text.text(f"🔍 Analisando combinações de {r} nota(s)...")
        progress_bar.progress(r / max_len)
        
        for combo in combinations(numbers, r):
            # Verificação rápida de soma
            if sum(combo) == target:
                st.session_state.tempo = time.time() - start_time
                return list(combo)
    
    return None

# --- INTERFACE ---
st.markdown("""<style>.stCard { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Segurança e Filtros")
    # Limite máximo de 20 para evitar DoS acidental no servidor
    max_depth = st.slider("Profundidade Máxima", 1, 20, 12, 
                         help="Limite de quantas notas podem ser somadas. Valores altos exigem muito do servidor.")
    st.info("A busca será interrompida automaticamente após 60 segundos para preservar o sistema.")

selected = option_menu(None, ["Conciliador", "Sobre"], icons=["shield-check", "info-circle"], orientation="horizontal")

if selected == "Conciliador":
    st.title("⚖️ Conciliador Financeiro Seguro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            target_val = st.number_input("Valor do Depósito (R$)", min_value=0.00, format="%.2f")
            notes_raw = st.text_area("Valores das Notas (Cole aqui)", height=200, placeholder="Ex: 100,50\n200.00\n300")
            
            # Limpeza em tempo real
            valid_notes = parse_and_clean_numbers(notes_raw)
            if valid_notes:
                st.caption(f"✅ {len(valid_notes)} valores numéricos identificados com segurança.")

            if st.button("🚀 Iniciar Conciliação"):
                if not valid_notes or target_val <= 0:
                    st.warning("Insira dados válidos para prosseguir.")
                else:
                    # Transformar em inteiros (centavos) para evitar erros de precisão float
                    target_int = int(round(target_val * 100))
                    notes_int = [int(round(n * 100)) for n in valid_notes]
                    
                    p_bar = st.progress(0)
                    s_msg = st.empty()
                    
                    res = find_subset_sum(notes_int, target_int, max_depth, p_bar, s_msg)
                    
                    p_bar.empty()
                    s_msg.empty()
                    
                    if res == "timeout":
                        pass # Erro já exibido na função
                    elif res:
                        st.balloons()
                        st.success(f"### Combinação encontrada em {st.session_state.tempo:.2f}s!")
                        final_res = [x / 100 for x in res]
                        st.dataframe(final_res, column_config={"value": "Valor da Nota"})
                    else:
                        st.error("Nenhuma combinação encontrada. Tente aumentar a profundidade ou revise os valores.")

    with col2:
        st.markdown("### 🔒 Camadas de Proteção")
        st.write("""
        - **Sanitização:** O sistema ignora qualquer texto ou script malicioso.
        - **Timeout:** Proteção contra travamento de CPU.
        - **Volatilidade:** Seus dados não são gravados em disco.
        """)

# --- ABA DE AJUDA / SOBRE ---
else:
    st.title("📖 Sobre o Conciliador")
    st.markdown("---")
    
    col_sobre, col_img = st.columns([1.5, 1])
    
    with col_sobre:
        st.markdown("""
        ### 🎯 O que é esta ferramenta?
        Este **Conciliador de Notas** foi desenvolvido para resolver um problema comum no setor financeiro: 
        identificar quais notas fiscais compõem um pagamento de valor total quando não há uma lista clara.
        
        ### 🧠 Como funciona a Inteligência?
        A aplicação utiliza um algoritmo de **análise combinatória** para testar as possibilidades 
        dentro da sua lista de notas. 
        
        - **Busca Exata:** Ele não faz aproximações, ele busca o valor centavo por centavo.
        - **Processamento em Centavos:** Para evitar erros de arredondamento do Python, 
          todos os cálculos são convertidos internamente para inteiros (centavos).
        """)

    with col_img:
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 15px;">
            <h4>👨‍💻 Desenvolvedor</h4>
            <p><strong>Rafael (Taff4)</strong></p>
            <p>Projeto focado em automação financeira e produtividade.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") 
        st.link_button("🌐 Ver Repositório no GitHub", "https://github.com/Taff4/conciliador-notas")

    st.markdown("---")
    
    st.subheader("❓ Perguntas Frequentes")
    
    with st.expander("🛡️ Meus dados estão seguros?"):
        st.write("Sim! Os dados colados são processados apenas na memória temporária do servidor e desaparecem assim que você fecha a aba. Nada é armazenado em bancos de dados.")
        
    with st.expander("⚡ Por que a busca pode demorar?"):
        st.write("O tempo de busca cresce conforme o número de notas e a 'Profundidade' aumenta. Se você tem 50 notas e busca uma soma de 15 delas, o número de combinações possíveis é de bilhões!")
        
    with st.expander("📝 Formatação dos números"):
        st.write("A ferramenta é inteligente: você pode colar valores com vírgula (padrão BR) ou ponto (padrão US). Textos como 'R$' ou 'Total' são filtrados automaticamente.")
