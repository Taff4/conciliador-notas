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
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def parse_and_clean_numbers(raw_text: str):
    """
    Sanitização: Agora aceita números negativos (abatimentos) usando o sinal de menos (-).
    """
    if not raw_text: 
        return[]
    text_cleaned = raw_text.replace(',', '.')
    # Regex atualizado para aceitar o sinal de "-" opcional no início do número
    potential_numbers = re.findall(r'-?\b\d+(?:\.\d+)?\b', text_cleaned)
    
    valid_numbers =[]
    for num_str in potential_numbers:
        try:
            val = float(num_str)
            # Aceita negativos, ignora zeros absolutos, trava limite de segurança
            if -1000000000 < val < 1000000000 and val != 0: 
                valid_numbers.append(val)
        except ValueError: 
            continue
    return valid_numbers

def find_subset_sum(numbers, target, max_len, tolerance, progress_bar, status_text):
    """
    Cálculo otimizado via DP com suporte a valores negativos e tolerância de centavos.
    """
    start_time = time.time()
    MAX_WAIT = 300

    # Otimização: Ordena pelo valor absoluto decrescente para chegar aos valores grandes mais rápido
    valid_nums = sorted(numbers, key=lambda x: abs(x), reverse=True)
    if not valid_nums:
        return None, None

    # Recalcula o limite máximo de soma permitida para não cortar caminhos caso haja notas negativas
    sum_negatives = sum(n for n in valid_nums if n < 0)
    max_allowed_sum = target - sum_negatives + tolerance

    dp = {0:[]}
    total_nums = len(valid_nums)
    
    best_match = None
    closest_diff = float('inf')
    
    for i, num in enumerate(valid_nums):
        if time.time() - start_time > MAX_WAIT:
            st.error(f"⚠️ **Busca interrompida por segurança.** O cálculo excedeu {MAX_WAIT}s.")
            return "timeout", None
            
        status_text.text(f"🔍 Programação Dinâmica: processando nota {i+1} de {total_nums}...")
        progress_bar.progress((i + 1) / total_nums)
        
        new_dp = dp.copy()
        for current_sum, combo in dp.items():
            new_sum = current_sum + num
            
            # Limite superior com folga para notas negativas
            if new_sum <= max_allowed_sum and len(combo) < max_len:
                
                # Checa se cravou o valor exato
                if new_sum == target:
                    st.session_state.tempo = time.time() - start_time
                    return combo + [num], 0
                
                # Checa se está dentro da margem de tolerância
                diff = abs(new_sum - target)
                if diff <= tolerance:
                    if diff < closest_diff:
                        closest_diff = diff
                        best_match = combo +[num]
                
                if new_sum not in new_dp or len(combo) + 1 < len(new_dp[new_sum]):
                    new_dp[new_sum] = combo + [num]
                    
        dp = new_dp
        
    # Se não achou exato, mas achou um na tolerância, retorna ele
    if best_match is not None:
        st.session_state.tempo = time.time() - start_time
        return best_match, closest_diff
        
    return None, None

# --- INTERFACE ---
st.markdown("""<style>.stCard { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Segurança e Filtros")
    max_depth = st.slider("Profundidade Máxima", 1, 60, 12, 
                         help="Limite de quantas notas podem ser somadas. Valores altos exigem muito do servidor.")
    st.info("A busca será interrompida automaticamente após 300 segundos para preservar o sistema.")

selected = option_menu(None,["Conciliador", "Sobre"], icons=["shield-check", "info-circle"], orientation="horizontal")

if selected == "Conciliador":
    st.title("⚖️ Conciliador Financeiro Seguro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            target_val = st.number_input("Valor do Depósito (R$)", min_value=0.00, format="%.2f")
            
            # NOVO CAMPO: Tolerância
            tolerance_val = st.number_input("Margem de Tolerância (R$)", min_value=0.00, max_value=50.00, value=0.00, step=0.01, 
                                            help="Útil para encontrar notas com pequenas diferenças de juros ou descontos.")
            
            notes_raw = st.text_area("Valores das Notas (Cole aqui)", height=200, placeholder="Ex: 100,50\n-15.00 (abatimento)\n300")
            
            valid_notes = parse_and_clean_numbers(notes_raw)
            if valid_notes:
                st.caption(f"✅ {len(valid_notes)} valores identificados (positivos e negativos).")

            if st.button("🚀 Iniciar Conciliação"):
                if not valid_notes or target_val <= 0:
                    st.warning("Insira dados válidos para prosseguir.")
                else:
                    target_int = int(round(target_val * 100))
                    tol_int = int(round(tolerance_val * 100))
                    notes_int =[int(round(n * 100)) for n in valid_notes]
                    
                    p_bar = st.progress(0)
                    s_msg = st.empty()
                    
                    # Agora a função recebe a tolerância e devolve a diferença (se houver)
                    res, diff = find_subset_sum(notes_int, target_int, max_depth, tol_int, p_bar, s_msg)
                    
                    p_bar.empty()
                    s_msg.empty()
                    
                    if res == "timeout":
                        pass
                    elif res:
                        st.balloons()
                        
                        # Mensagem condicional se usou tolerância
                        if diff == 0:
                            st.success(f"### Combinação EXATA encontrada em {st.session_state.tempo:.2f}s!")
                        else:
                            diff_reais = diff / 100
                            st.warning(f"### Combinação encontrada com diferença de R$ {diff_reais:.2f} (dentro da tolerância) em {st.session_state.tempo:.2f}s!")
                        
                        final_res = [x / 100 for x in res]
                        st.dataframe(final_res, column_config={"value": "Valor da Nota"})
                    else:
                        st.error("Nenhuma combinação encontrada. Revise os valores ou tente ajustar a 'Margem de Tolerância'.")

    with col2:
        st.markdown("### 🔒 Camadas de Proteção")
        st.write("""
        - **Sanitização:** Ignora textos maliciosos, mas aceita valores negativos para abatimentos (ex: -50.00).
        - **Tolerância:** Ajuste para cobrir juros/descontos.
        - **Timeout e Volatilidade:** Seus dados estão seguros e não sobrecarregam a máquina.
        """)

else:
    st.title("📖 Sobre o Conciliador")
    st.markdown("---")
    
    col_sobre, col_img = st.columns([1.5, 1])
    
    with col_sobre:
        st.markdown("""
        ### 🎯 O que é esta ferramenta?
        Este **Conciliador de Notas** identifica quais notas fiscais compõem um pagamento quando não há uma lista clara.
        
        ### 🧠 Como funciona a Inteligência?
        Utilizamos **Programação Dinâmica**, que corta caminhos lógicos inúteis para achar resultados em milissegundos.
        - Aceita números negativos (para devoluções/abatimentos).
        - Possui margem de tolerância ajustável para lidar com centavos de juros ou desconto bancário.
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
