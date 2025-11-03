import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
import re
from itertools import combinations
import time

# ======================================================================================
# CONFIGURAÇÃO DA PÁGINA E FUNÇÕES AUXILIARES
# ======================================================================================

st.set_page_config(
    page_title="Conciliador de Notas",
    page_icon="📄",
    layout="wide"
)


# Função para carregar animações Lottie
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.RequestException:
        pass
    return None


# Função para limpar e validar a entrada de números
def parse_and_clean_numbers(raw_text: str):
    text_with_dots = raw_text.replace(',', '.')
    potential_numbers = re.findall(r'[\d\.]+', text_with_dots)
    valid_numbers = []
    for num_str in potential_numbers:
        try:
            valid_numbers.append(float(num_str))
        except ValueError:
            pass
    return valid_numbers


# Função de cálculo
def find_subset_sum(numbers, target, max_len, progress_bar, status_text):
    start_time = time.time()
    for r in range(1, max_len + 1):
        progress_percentage = r / max_len
        status_text.text(f"Analisando combinações de {r} nota(s)...")
        progress_bar.progress(progress_percentage)
        for combo in combinations(numbers, r):
            if sum(combo) == target:
                end_time = time.time()
                st.session_state.tempo_execucao = f"{end_time - start_time:.2f} segundos"
                return list(combo)
    end_time = time.time()
    st.session_state.tempo_execucao = f"{end_time - start_time:.2f} segundos"
    return None


# Carregar CSS customizado
st.markdown(
    """<style>.card{background-color:#FFFFFF;border-radius:10px;padding:25px;box-shadow:0 4px 8px 0 rgba(0,0,0,0.1);transition:0.3s;}.card:hover{box-shadow:0 8px 16px 0 rgba(0,0,0,0.2);}.stButton>button{border-radius:10px;border:2px solid #007BFF;background-color:#007BFF;color:white;transition:all 0.2s ease-in-out;font-weight:bold;}.stButton>button:hover{border-color:#0056b3;background-color:#0056b3;}</style>""",
    unsafe_allow_html=True)

# ======================================================================================
# INTERFACE DA APLICAÇÃO
# ======================================================================================

lottie_main = load_lottieurl("https://lottie.host/80f763a1-0538-4f80-9289-a36ef733157a/lE7aad9yTw.json")
lottie_searching = load_lottieurl("https://lottie.host/7e9232a5-4f40-4235-8097-d64c1e4b9cfa/13W4S62HVT.json")
lottie_success = load_lottieurl("https://lottie.host/43e7534c-687f-4f7f-8c34-68875704f4a3/2VAm7vVdQr.json")
lottie_error = load_lottieurl("https://lottie.host/9d3115c5-25e2-45e0-81f9-1e3c2331c26b/T4C4S62HVT.json")

# --- Barra de Navegação Horizontal ---
selected = option_menu(
    menu_title=None,
    options=["Conciliador", "Guia de Ajuda"],
    icons=["calculator-fill", "question-circle-fill"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "#007BFF", "font-size": "20px"},
        "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#E0EFFF"},
        # <<< CORREÇÃO APLICADA AQUI >>>
        "menu-title": {"display": "none"},
    }
)

if selected == "Conciliador":
    st.title("Conciliador de Notas")
    st.markdown("---")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        if lottie_main: st_lottie(lottie_main, height=250)
        st.subheader("Seu assistente de conciliação inteligente.")
        st.write("Preencha os dados ao lado para encontrar a combinação exata de notas fiscais.")

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        target_input = st.number_input("Valor Total do Pagamento", min_value=0.01, step=0.01, format="%.2f")
        numeros_input_str = st.text_area("Lista de Notas em Aberto", height=200, placeholder="Cole os valores aqui...")

        valid_numbers = []
        if numeros_input_str:
            valid_numbers = parse_and_clean_numbers(numeros_input_str)
            if valid_numbers:
                st.info(f"✅ **{len(valid_numbers)}** notas válidas inseridas.")

        with st.expander("⚙️ Opções Avançadas"):
            max_len_input = st.number_input(
                label="Profundidade Máxima da Busca", min_value=1, value=15, step=1,
                help="Define o número máximo de notas a serem combinadas."
            )
            if max_len_input > 18:
                st.warning(f"**Atenção:** Uma busca com profundidade **{max_len_input}** pode ser extremamente lenta.")

        buscar = st.button("🔍 Iniciar Análise", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if buscar:
        if not valid_numbers or target_input <= 0:
            st.warning("⚠️ Por favor, insira um valor total e uma lista de notas válida.")
        else:
            try:
                nums_int = [int(round(n * 100)) for n in valid_numbers]
                target_int = int(round(target_input * 100))

                result_placeholder = st.empty()
                with result_placeholder.container():
                    if lottie_searching: st_lottie(lottie_searching, height=200)
                    status_text = st.empty()
                    progress_bar = st.progress(0)

                resultado = find_subset_sum(nums_int, target_int, max_len_input, progress_bar, status_text)
                result_placeholder.empty()

                if resultado:
                    st.balloons()
                    col_res1, col_res2 = st.columns([1, 2])
                    with col_res1:
                        if lottie_success: st_lottie(lottie_success, height=200)
                    with col_res2:
                        st.success("Combinação Encontrada!")
                        resultado_final = [x / 100 for x in resultado]
                        st.metric(label="Soma Verificada", value=f"R$ {sum(resultado_final):,.2f}")
                        st.caption(f"Tempo de busca: {st.session_state.get('tempo_execucao', 'N/A')}")
                    st.write("**Notas que compõem o valor total:**")
                    st.dataframe(resultado_final, use_container_width=True, hide_index=True,
                                 column_config={"value": st.column_config.NumberColumn("Valor", format="R$ %.2f")})
                else:
                    col_res1, col_res2 = st.columns([1, 2])
                    with col_res1:
                        if lottie_error: st_lottie(lottie_error, height=180)
                    with col_res2:
                        st.error("Nenhuma combinação encontrada.")
                        st.caption(f"Tempo de busca: {st.session_state.get('tempo_execucao', 'N/A')}")
                        st.info(
                            f"Dica: A busca foi limitada a combinações de até **{max_len_input}** notas. Se suspeitar que a combinação é maior, aumente o valor em 'Opções Avançadas' e tente novamente.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante o cálculo: {e}")

if selected == "Guia de Ajuda":
    st.title("📖 Guia de Utilização")
    st.markdown("---")
    st.info("Utilize os menus abaixo para expandir e ver as instruções detalhadas de cada tópico.")
    with st.expander("🎯 Qual o objetivo desta ferramenta?"):
        st.write(
            """Esta aplicação automatiza a tarefa de **encontrar qual grupo de notas fiscais corresponde a um pagamento total recebido**. Ela testa milhares de combinações em segundos, eliminando a necessidade de conferência manual.""")
    with st.expander("🚀 Como usar o Conciliador? (Passo a Passo)"):
        st.markdown(
            """1. **Valor Total:** No campo `Valor Total do Pagamento`, insira o valor exato recebido.\n2. **Lista de Notas:** No campo `Lista de Notas em Aberto`, cole todos os valores das notas pendentes.\n3. **Opções Avançadas (Opcional):** Se necessário, ajuste a 'Profundidade Máxima da Busca' para um valor maior.\n4. **Analisar:** Clique no botão `Iniciar Análise` e aguarde o resultado.""")
    with st.expander("💡 Dicas e Perguntas Frequentes (FAQ)"):
        st.markdown(
            """- **Está demorando, é normal?** Sim, listas grandes (>30 notas) e uma profundidade de busca alta (acima de 15) podem levar vários minutos.\n- **Não encontrou nada, e agora?** Primeiro, verifique os números. Se estiverem corretos, vá em **'⚙️ Opções Avançadas'** e aumente o número no campo 'Profundidade Máxima da Busca'. **Faça isso com cautela!**\n- **A ferramenta ignora textos?** Sim. Se você colar 'Total: R$ 1.234,56', a ferramenta irá ler apenas o número `1234.56`.""")