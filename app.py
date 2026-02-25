import streamlit as st
from streamlit_option_menu import option_menu
import re
from itertools import combinations
import time
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliador Seguro", page_icon="🛡️", layout="wide")

# --- FUNÇÕES DE SEGURANÇA E CÁLCULO ---
def parse_and_clean_numbers(raw_text: str):
    if not raw_text: return []
    
    # Remove pontos de milhar e converte vírgula decimal em ponto
    # Ex: 1.250,50 -> 1250.50
    text_cleaned = raw_text.replace('.', '').replace(',', '.')
    
    # Busca padrões numéricos
    potential_numbers = re.findall(r'\d+(?:\.\d+)?', text_cleaned)
    
    valid_numbers = []
    for num_str in potential_numbers:
        try:
            val = float(num_str)
            if 0 < val < 1_000_000_000:
                valid_numbers.append(val)
        except ValueError: continue
    return valid_numbers

def find_subset_sum(numbers, target, max_len, progress_bar, status_text):
    start_time = time.time()
    MAX_WAIT = 60  

    # Filtro inteligente: notas maiores que o alvo são descartadas para reduzir combinações
    numbers = sorted([n for n in numbers if n <= target], reverse=True)

    for r in range(1, max_len + 1):
        if time.time() - start_time > MAX_WAIT:
            return "timeout"
            
        status_text.text(f"🔍 Analisando combinações de {r} nota(s)...")
        progress_bar.progress(r / max_len)
        
        for combo in combinations(numbers, r):
            if sum(combo) == target:
                st.session_state.tempo = time.time() - start_time
                return list(combo)
    
    return None

# --- INTERFACE ---
st.markdown("""<style>.stCard { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configurações")
    max_depth = st.slider("Profundidade Máxima", 1, 20, 10, 
                         help="Quantas notas o sistema tentará combinar por vez.")
    st.info("Limite de 60s por busca para segurança do servidor.")

selected = option_menu(None, ["Conciliador", "Sobre"], 
    icons=["shield-check", "info-circle"], orientation="horizontal")

if selected == "Conciliador":
    st.title("⚖️ Conciliador Financeiro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_val = st.number_input("Valor total esperado (R$)", min_value=0.00, format="%.2f", step=0.01)
        notes_raw = st.text_area("Cole a lista de valores das notas", height=200, placeholder="150,00\n200.50\n50,00")
        
        valid_notes = parse_and_clean_numbers(notes_raw)
        if valid_notes:
            st.caption(f"✅ {len(valid_notes)} valores identificados.")

        if st.button("🚀 Buscar Combinação"):
            if not valid_notes or target_val <= 0:
                st.warning("Verifique o valor total e as notas inseridas.")
            else:
                # Conversão para centavos (Inteiros)
                target_int = int(round(target_val * 100))
                notes_int = [int(round(n * 100)) for n in valid_notes]
                
                p_bar = st.progress(0)
                s_msg = st.empty()
                st.session_state.tempo = 0 # Inicializa
                
                res = find_subset_sum(notes_int, target_int, max_depth, p_bar, s_msg)
                
                p_bar.empty()
                s_msg.empty()
                
                if res == "timeout":
                    st.error("⚠️ Tempo limite atingido. Tente reduzir a 'Profundidade' ou filtrar as notas manualmente.")
                elif res:
                    st.balloons()
                    st.success(f"### Encontrado em {st.session_state.tempo:.2f}s!")
                    
                    # Converte de volta e exibe
                    final_res = [x / 100 for x in res]
                    df_res = pd.DataFrame(final_res, columns=["Valor da Nota"])
                    st.table(df_res.style.format("R$ {:.2f}"))
                    
                    # Botão de download
                    csv = df_res.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar Resultado (CSV)", csv, "conciliacao.csv", "text/csv")
                else:
                    st.error("Nenhuma combinação exata encontrada para esses valores.")

    with col2:
        st.markdown("### 🔒 Segurança")
        st.info("""
        - **Cálculo Preciso:** Usamos inteiros para evitar erros de centavos.
        - **Privacidade:** Nada é salvo. Os dados residem apenas na sua sessão atual.
        - **Performance:** O algoritmo prioriza as notas maiores para chegar ao resultado mais rápido.
        """)

else:
    st.title("📖 Sobre o Projeto")
    st.markdown("""
    ### O desafio da Conciliação
    Muitas vezes recebemos um depósito bancário único que engloba várias faturas. 
    Este sistema automatiza a "tentativa e erro" de descobrir quais faturas somadas chegam ao valor exato.
    
    **Exemplo:**
    - Depósito: R$ 300,00
    - Notas: [100, 150, 200, 50]
    - Resultado: [100, 150, 50] ou [100, 200]
    """)
    st.link_button("🌐 GitHub do Desenvolvedor", "https://github.com/Taff4/conciliador-notas")
