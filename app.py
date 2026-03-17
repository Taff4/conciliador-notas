import streamlit as st
from streamlit_option_menu import option_menu
import re
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliador Financeiro", layout="wide")

# --- FUNÇÕES DE CÁLCULO ---
def parse_and_clean_numbers(raw_text: str):
    if not raw_text: 
        return []
    text_cleaned = raw_text.replace(',', '.')
    potential_numbers = re.findall(r'-?\b\d+(?:\.\d+)?\b', text_cleaned)
    
    valid_numbers = []
    for num_str in potential_numbers:
        try:
            val = float(num_str)
            if -1000000000 < val < 1000000000 and val != 0: 
                valid_numbers.append(val)
        except ValueError: 
            continue
    return valid_numbers

def find_subset_sum_fast(numbers, target, max_len, tolerance, status_text):
    """ Busca Rápida: Para na primeira combinação encontrada """
    start_time = time.time()
    MAX_WAIT = 300
    valid_nums = sorted(numbers, key=lambda x: abs(x), reverse=True)
    if not valid_nums: return None, None

    sum_negatives = sum(n for n in valid_nums if n < 0)
    max_allowed_sum = target - sum_negatives + tolerance

    dp = {0: []}
    total_nums = len(valid_nums)
    best_match = None
    closest_diff = float('inf')
    
    for i, num in enumerate(valid_nums):
        if time.time() - start_time > MAX_WAIT:
            return "timeout", None
            
        status_text.text(f"Processando nota {i+1} de {total_nums}...")
        
        new_dp = dp.copy()
        for current_sum, combo in dp.items():
            new_sum = current_sum + num
            
            if new_sum <= max_allowed_sum and len(combo) < max_len:
                if new_sum == target:
                    st.session_state.tempo = time.time() - start_time
                    return combo + [num], 0
                
                diff = abs(new_sum - target)
                if diff <= tolerance:
                    if diff < closest_diff:
                        closest_diff = diff
                        best_match = combo + [num]
                
                if new_sum not in new_dp or len(combo) + 1 < len(new_dp[new_sum]):
                    new_dp[new_sum] = combo + [num]
        dp = new_dp
        
    if best_match is not None:
        st.session_state.tempo = time.time() - start_time
        return best_match, closest_diff
    return None, None

def find_all_combinations(numbers, target, max_len, tolerance, max_results):
    """ Busca Profunda: Encontra múltiplas combinações com checagem rápida de repetidos """
    start_time = time.time()
    MAX_WAIT = 60  
    results = []
    vistos = set()
    
    valid_nums = sorted(numbers, key=lambda x: abs(x), reverse=True)
    
    def backtrack(start, path, current_sum):
        if time.time() - start_time > MAX_WAIT:
            raise TimeoutError
        if len(results) >= max_results:
            return
            
        diff = abs(current_sum - target)
        if diff <= tolerance and 0 < len(path) <= max_len:
            caminho_ordenado = tuple(sorted(path))
            if caminho_ordenado not in vistos:
                vistos.add(caminho_ordenado)
                results.append((path, diff))
                
        if len(path) >= max_len:
            return
            
        for i in range(start, len(valid_nums)):
            backtrack(i + 1, path + [valid_nums[i]], current_sum + valid_nums[i])
            
    try:
        backtrack(0, [], 0)
    except TimeoutError:
        st.session_state.tempo = time.time() - start_time
        return "timeout", results
        
    st.session_state.tempo = time.time() - start_time
    return "done", results

# --- INTERFACE ---
st.markdown("""<style>.stCard { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Configurações")
    max_depth = st.slider("Profundidade Máxima", 1, 60, 12, help="Limite de notas somadas.")
    
    st.markdown("---")
    st.subheader("Modo Auditoria")
    deep_search = st.toggle("Ativar Busca Profunda", value=False, help="Procura múltiplas combinações.")
    
    if deep_search:
        max_results_ui = st.number_input("Máximo de Combinações", min_value=1, max_value=50, value=5)
        st.warning(f"A busca retornará no máximo {max_results_ui} combinações. Interrupção automática em 60 segundos por segurança.")
    else:
        max_results_ui = 1

selected = option_menu(None, ["Conciliador", "Como Usar", "Sobre"], orientation="horizontal")

# --- ABA 1: CONCILIADOR ---
if selected == "Conciliador":
    st.title("Conciliador Financeiro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            col_a, col_b = st.columns(2)
            with col_a:
                target_val = st.number_input("Valor do Depósito (R$)", min_value=0.00, format="%.2f")
            with col_b:
                tolerance_val = st.number_input("Margem de Tolerância (R$)", min_value=0.00, max_value=50.00, value=0.00, step=0.01)
            
            notes_raw = st.text_area("Valores das Notas", height=200, placeholder="Ex: 100.50\n-15.00\n300")
            
            valid_notes = parse_and_clean_numbers(notes_raw)
            if valid_notes:
                st.caption(f"{len(valid_notes)} valores identificados.")

            if st.button("Iniciar Conciliação"):
                if not valid_notes or target_val <= 0:
                    st.warning("Insira dados válidos para prosseguir.")
                else:
                    target_int = int(round(target_val * 100))
                    tol_int = int(round(tolerance_val * 100))
                    notes_int = [int(round(n * 100)) for n in valid_notes]
                    
                    s_msg = st.empty()
                    
                    if deep_search:
                        with st.spinner("Executando busca profunda. Isso pode levar até 60 segundos..."):
                            status, results = find_all_combinations(notes_int, target_int, max_depth, tol_int, max_results_ui)
                        
                        if status == "timeout" and not results:
                            st.error("Tempo limite atingido. Nenhuma combinação encontrada.")
                        elif results:
                            if status == "timeout":
                                st.warning(f"Tempo esgotado. {len(results)} combinações encontradas em {st.session_state.tempo:.2f}s.")
                            else:
                                st.success(f"Busca concluída. {len(results)} combinação(ões) encontrada(s) em {st.session_state.tempo:.2f}s.")
                            
                            for i, (res, diff) in enumerate(results):
                                with st.expander(f"Opção {i+1} - {len(res)} notas (Diferença: R$ {diff/100:.2f})", expanded=True):
                                    st.dataframe([x / 100 for x in res], column_config={"value": "Valor da Nota"}, use_container_width=True)
                        else:
                            st.error("Nenhuma combinação encontrada. Revise os valores.")
                            
                    else:
                        with st.spinner("Calculando..."):
                            res, diff = find_subset_sum_fast(notes_int, target_int, max_depth, tol_int, s_msg)
                        s_msg.empty()
                        
                        if res == "timeout":
                            st.error("Tempo limite esgotado. Tente ativar a Busca Profunda ou reduzir a quantidade de notas.")
                        elif res:
                            if diff == 0:
                                st.success(f"Combinação exata encontrada em {st.session_state.tempo:.2f}s.")
                            else:
                                st.warning(f"Combinação encontrada com diferença de R$ {diff/100:.2f} em {st.session_state.tempo:.2f}s.")
                            
                            st.dataframe([x / 100 for x in res], column_config={"value": "Valor da Nota"})
                        else:
                            st.error("Nenhuma combinação encontrada. Revise os valores ou a margem de tolerância.")

    with col2:
        st.markdown("### Camadas de Proteção")
        st.write("""
        - **Sanitização:** Ignora textos, aceita formatação com ponto ou vírgula e contabiliza valores negativos.
        - **Tolerância:** Ajuste opcional para cobrir variações de juros ou descontos.
        - **Timeout:** Prevenção contra sobrecarga e estouro de memória.
        """)

# --- ABA 2: COMO USAR ---
elif selected == "Como Usar":
    st.title("Manual de Uso")
    st.markdown("Orientações de lógica para a utilização correta da aplicação.")
    
    st.markdown("---")
    
    st.subheader("1. Múltiplas Combinações (Falsos Positivos)")
    st.write("""
    Matematicamente, é possível que mais de uma combinação de notas resulte no mesmo valor de depósito. 
    - O sistema retorna, por padrão, a primeira combinação válida encontrada para otimizar o tempo de resposta.
    - Para verificar outras possibilidades (auditoria), ative a **Busca Profunda** na barra lateral. O algoritmo listará opções alternativas.
    """)
    
    st.subheader("2. Margem de Tolerância")
    st.write("""
    Utilize a margem de tolerância caso haja divergências por centavos, juros ou pequenos descontos.
    - Exemplo: Ao definir R$ 0,50 de tolerância, o sistema aceitará combinações que divirjam até esse limite do valor exato buscado.
    """)

    st.subheader("3. Abatimentos (Valores Negativos)")
    st.write("""
    Para registrar adiantamentos, devoluções ou notas de crédito, inclua o sinal de menos (-) antes do valor. Textos adicionais na mesma linha serão ignorados durante o cálculo.
    """)
    
    st.subheader("4. Precisão Decimal")
    st.write("""
    Para evitar erros de arredondamento inerentes a cálculos computacionais de ponto flutuante, todos os valores inseridos são convertidos para números inteiros (multiplicados por 100) durante o processamento.
    """)

# --- ABA 3: SOBRE ---
else:
    st.title("Sobre o Sistema")
    st.markdown("---")
    
    col_sobre, col_img = st.columns([1.5, 1])
    
    with col_sobre:
        st.markdown("""
        ### Objetivo
        Ferramenta desenvolvida para identificar de forma automatizada quais notas fiscais ou lançamentos compõem um pagamento consolidado, agilizando a conciliação financeira.
        
        ### Metodologia
        A aplicação utiliza um algoritmo de Programação Dinâmica (Dynamic Programming) aplicado ao problema de soma de subconjuntos (Subset Sum Problem).
        
        - **Otimização:** O algoritmo descarta caminhos matematicamente inviáveis na raiz para economizar processamento.
        - **Prevenção de Erros:** O processamento em inteiros garante precisão absoluta nos cálculos.
        """)

    with col_img:
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 12px;">
            <h4>Desenvolvedor</h4>
            <p><strong>Rafael Lacerda Silva</strong></p>
            <p>Foco em automação de processos e análise de dados.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") 
        st.link_button("Acessar Repositório (GitHub)", "https://github.com/Taff4/conciliador-notas")
