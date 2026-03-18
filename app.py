import streamlit as st
from streamlit_option_menu import option_menu
import re
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliador Seguro", page_icon="🛡️", layout="wide")

# --- FUNÇÕES DE SEGURANÇA E CÁLCULO ---
def parse_and_clean_numbers(raw_text: str):
    """ Extrator robusto: Lida com formatos BR (1.234,50), US (1,234.50) e negativos. """
    if not raw_text: 
        return []
    
    valid_numbers =[]
    tokens = re.findall(r'-?\s*\d+(?:[.,]\d+)*', raw_text)
    
    for token in tokens:
        token = token.replace(' ', '')
        
        if ',' in token and '.' in token:
            if token.rfind(',') > token.rfind('.'):
                clean_num = token.replace('.', '').replace(',', '.')
            else:
                clean_num = token.replace(',', '')
        elif ',' in token:
            clean_num = token.replace(',', '.')
        else:
            clean_num = token
            
        try:
            val = float(clean_num)
            if -1000000000 < val < 1000000000 and val != 0: 
                valid_numbers.append(val)
        except ValueError: 
            continue
            
    return valid_numbers

def find_subset_sum_fast(numbers, target, max_len, tolerance, progress_bar, status_text):
    """ Busca Rápida: Para na primeira combinação que encontrar (Programação Dinâmica) """
    start_time = time.time()
    MAX_WAIT = 300
    valid_nums = sorted(numbers, key=lambda x: abs(x), reverse=True)
    if not valid_nums: return None, None, 0

    sum_negatives = sum(n for n in valid_nums if n < 0)
    max_allowed_sum = target - sum_negatives + tolerance

    dp = {0:[]}
    total_nums = len(valid_nums)
    best_match = None
    closest_diff = float('inf')
    
    for i, num in enumerate(valid_nums):
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT:
            return "timeout", None, elapsed
            
        status_text.text(f"🔍 Busca Rápida: processando nota {i+1} de {total_nums}...")
        progress_bar.progress((i + 1) / total_nums)
        
        new_dp = dp.copy()
        for current_sum, combo in dp.items():
            new_sum = current_sum + num
            
            if new_sum <= max_allowed_sum and len(combo) < max_len:
                new_combo = combo + [num]
                if new_sum == target:
                    return new_combo, 0, time.time() - start_time
                
                diff = abs(new_sum - target)
                if diff <= tolerance:
                    if diff < closest_diff:
                        closest_diff = diff
                        best_match = new_combo
                
                if new_sum not in new_dp or len(new_combo) < len(new_dp[new_sum]):
                    new_dp[new_sum] = new_combo
        dp = new_dp
        
    elapsed = time.time() - start_time
    if best_match is not None:
        return best_match, closest_diff, elapsed
    return None, None, elapsed

def find_all_combinations(numbers, target, max_len, tolerance, progress_bar, status_text):
    """ Busca Profunda: Encontra MÚLTIPLAS combinações (Auditoria de Falsos Positivos) """
    start_time = time.time()
    MAX_WAIT = 60  
    MAX_RESULTS = 10 # Limite ajustado para 10 opções
    results =[]
    
    valid_nums = sorted(numbers, key=lambda x: abs(x), reverse=True)
    
    def backtrack(start, path, current_sum):
        if time.time() - start_time > MAX_WAIT:
            raise TimeoutError
        if len(results) >= MAX_RESULTS:
            return
            
        diff = abs(current_sum - target)
        if diff <= tolerance and len(path) > 0 and len(path) <= max_len:
            sorted_path = sorted(path)
            if not any(sorted_path == sorted(r[0]) for r in results):
                results.append((path, diff))
                
        if len(path) >= max_len:
            return
            
        for i in range(start, len(valid_nums)):
            backtrack(i + 1, path +[valid_nums[i]], current_sum + valid_nums[i])
            
    try:
        status_text.text("🔍 Busca Profunda: Varrendo todos os cenários possíveis (Isso pode demorar)...")
        progress_bar.progress(0.8) 
        backtrack(0,[], 0)
    except TimeoutError:
        return "timeout", results, time.time() - start_time
        
    return "done", results, time.time() - start_time

# --- INTERFACE ---
st.markdown("""<style>.stCard { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; }</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configurações")
    max_depth = st.slider("Profundidade Máxima", 1, 60, 12, help="Limite de quantas notas podem ser somadas.")
    
    st.markdown("---")
    st.subheader("Modo Auditoria")
    deep_search = st.toggle("Ativar Busca Profunda", value=False, help="Procura múltiplas combinações para verificar falsos positivos.")
    if deep_search:
        st.warning("⚠️ **Atenção:** A busca profunda exige muito do sistema. Ela retornará no máximo **10 combinações** e será interrompida em **60 segundos** por segurança.")

# MENU SUPERIOR COM 3 ABAS
selected = option_menu(None,["Conciliador", "Como Usar", "Sobre"], icons=["shield-check", "book", "info-circle"], orientation="horizontal")

# --- ABA 1: CONCILIADOR ---
if selected == "Conciliador":
    st.title("⚖️ Conciliador Financeiro Seguro")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            col_a, col_b = st.columns(2)
            with col_a:
                target_val = st.number_input("Valor do Depósito (R$)", min_value=0.00, format="%.2f")
            with col_b:
                tolerance_val = st.number_input("Margem de Tolerância (R$)", min_value=0.00, max_value=50.00, value=0.00, step=0.01, 
                                                help="Para diferenças de juros ou descontos.")
            
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
                    notes_int = [int(round(n * 100)) for n in valid_notes]
                    
                    p_bar = st.progress(0)
                    s_msg = st.empty()
                    
                    # ROTA DA BUSCA PROFUNDA
                    if deep_search:
                        status, results, elapsed = find_all_combinations(notes_int, target_int, max_depth, tol_int, p_bar, s_msg)
                        p_bar.empty()
                        s_msg.empty()
                        
                        if status == "timeout" and not results:
                            st.error("⚠️ O limite de 60 segundos foi atingido e nenhuma combinação foi encontrada.")
                        elif results:
                            if status == "timeout":
                                st.warning(f"⚠️ Tempo esgotado! Encontramos {len(results)} combinações antes de interromper (Tempo: {elapsed:.2f}s).")
                            else:
                                st.success(f"### Concluído! Encontramos {len(results)} combinação(ões) possível(is) em {elapsed:.2f}s!")
                            
                            for i, (res, diff) in enumerate(results):
                                with st.expander(f"📌 Opção {i+1} - {len(res)} notas (Diferença: R$ {diff/100:.2f})", expanded=True):
                                    st.dataframe([x / 100 for x in res], column_config={"value": "Valor da Nota"}, use_container_width=True)
                        else:
                            st.error("Nenhuma combinação encontrada. Revise os valores.")
                            
                    # ROTA DA BUSCA RÁPIDA (PADRÃO)
                    else:
                        res, diff, elapsed = find_subset_sum_fast(notes_int, target_int, max_depth, tol_int, p_bar, s_msg)
                        p_bar.empty()
                        s_msg.empty()
                        
                        if res == "timeout":
                            st.error("⚠️ Tempo limite esgotado. Tente ativar a Busca Profunda ou diminuir as notas.")
                        elif res:
                            if diff == 0:
                                st.success(f"### Combinação EXATA encontrada em {elapsed:.2f}s!")
                            else:
                                st.warning(f"### Combinação encontrada com diferença de R$ {diff/100:.2f} (dentro da tolerância) em {elapsed:.2f}s!")
                            
                            st.dataframe([x / 100 for x in res], column_config={"value": "Valor da Nota"})
                        else:
                            st.error("Nenhuma combinação encontrada. Revise os valores ou ajuste a 'Margem de Tolerância'.")

    with col2:
        st.markdown("### 🔒 Camadas de Proteção")
        st.write("""
        - **Sanitização:** Ignora textos maliciosos, aceita negativos (-).
        - **Tolerância:** Ajuste para cobrir juros/descontos.
        - **Timeout:** Proteção de memória do servidor.
        """)

# --- ABA 2: COMO USAR ---
elif selected == "Como Usar":
    st.title("📖 Manual do Financeiro: Como Usar")
    st.markdown("Bem-vindo ao manual do conciliador. O sistema é muito inteligente e não comete erros de matemática, mas ele tem algumas **regras lógicas** que a equipe financeira precisa conhecer para usar com perfeição.")
    
    st.markdown("---")
    
    st.subheader("1. O Risco dos Falsos Positivos (Múltiplas Combinações)")
    st.write("""
    A matemática do programa é exata, mas às vezes *mais de uma combinação* de notas pode dar o mesmo valor do depósito. 
    - **Exemplo:** O cliente depositou R$ 1.000,00. As notas A + B somam exatos R$ 1.000,00. Porém, por coincidência, as notas C + D + E do mesmo cliente também somam R$ 1.000,00.
    - **O que o sistema faz por padrão:** Para ser rápido, ele devolve a *primeira combinação válida* que encontrar e para de procurar. 
    - **Como evitar problemas:** O financeiro sempre precisa checar se as notas apontadas fazem sentido. Se houver dúvida, ative o botão **Ativar Busca Profunda** na barra lateral. O sistema vai forçar uma varredura para listar até 10 combinações diferentes que chegam no mesmo valor (ideal para auditoria!).
    """)
    
    st.subheader("2. Juros, Multas e Descontos (Margem de Tolerância)")
    st.write("""
    O algoritmo busca o valor **exato**. Se a soma das notas fiscais dá R$ 5.430,00, mas o cliente pagou R$ 5.429,90 (teve 10 centavos de desconto), o sistema não vai achar a combinação sozinho.
    - **A Solução:** Agora você pode usar o campo **Margem de Tolerância**. Se você colocar `R$ 0,50` nesse campo, o sistema vai achar as notas corretas e te avisar na tela: *"Combinação encontrada com diferença de R$ 0.10"*.
    """)

    st.subheader("3. Abatimentos e Notas de Crédito (Valores Negativos)")
    st.write("""
    Precisa calcular um adiantamento ou devolução? Basta colocar o sinal de menos (-) antes do número da nota na lista.
    - **Exemplo:** Cole `-150,00` na lista. O sistema vai entender que é um crédito e irá *subtrair* esse valor da soma final automaticamente. Textos na frente do número (ex: `-150.00 Devolução`) são ignorados com segurança.
    """)
    
    st.subheader("4. Por que o sistema não tem erro de centavos?")
    st.write("""
    Em computadores normais (ou planilhas), contas com decimais às vezes dão erro de dízima (ex: 0.1 + 0.2 = 0.30000000004). 
    Neste sistema, para evitar isso, nós pegamos todos os seus valores e multiplicamos por 100 antes de calcular. Ou seja, **o sistema faz todas as contas usando números inteiros (moedas de 1 centavo)**. Isso garante precisão matemática absoluta e zero risco de arredondamento incorreto.
    """)

# --- ABA 3: SOBRE ---
else:
    st.title("ℹ️ Sobre o Conciliador")
    st.markdown("---")
    
    col_sobre, col_img = st.columns([1.5, 1])
    
    with col_sobre:
        st.markdown("""
        ### 🎯 O que é esta ferramenta?
        Este **Conciliador de Notas** foi desenvolvido para resolver um problema comum no setor financeiro: 
        identificar quais notas fiscais compõem um pagamento de valor total quando não há uma lista clara ou o cliente pagou notas aglomeradas.
        
        ### 🧠 Como funciona a Inteligência?
        A aplicação utiliza um algoritmo avançado de **Programação Dinâmica (Dynamic Programming)** adaptado para o *Subset Sum Problem*.
        
        - **Corte de Caminhos (Pruning):** Ele não testa combinações cegamente. Ele memoriza rotas e corta caminhos matematicamente impossíveis na raiz, economizando memória.
        - **Processamento em Centavos:** Todos os cálculos são convertidos para inteiros na memória do servidor para anular erros flutuantes (Floating Point Math).
        """)

    with col_img:
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 15px;">
            <h4>👨‍💻 Desenvolvedor</h4>
            <p><strong>Rafael Lacerda</strong></p>
            <p>Projeto focado em automação financeira, inteligência processual e produtividade.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") 
        st.link_button("🌐 Ver Repositório no GitHub", "https://github.com/Taff4/conciliador-notas")
