# 📄 Conciliador de Notas

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://conciliador-notas-j6zs7xlhec5cqht6kwv6nh.streamlit.app/)

Uma aplicação web inteligente desenvolvida em **Python** com **Streamlit** para automação financeira. Ela encontra a combinação exata de notas fiscais que somam um valor total de pagamento recebido.

## 🔗 Acesse a aplicação online
[Clique aqui para testar o Conciliador de Notas](https://conciliador-notas-j6zs7xlhec5cqht6kwv6nh.streamlit.app/)

## ✨ Funcionalidades Principais
* **Interface Intuitiva:** Design limpo focado na experiência do usuário.
* **Validação Inteligente:** Processa valores com ponto ou vírgula e ignora caracteres não numéricos (como "R$").
* **Feedback em Tempo Real:** Contador de notas válidas e barra de progresso durante a análise.
* **Busca Flexível:** Opções avançadas para definir a profundidade da busca de combinações.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.x
- **Frontend/Host:** Streamlit
- **Bibliotecas:** `streamlit-option-menu`, `streamlit-lottie`, `itertools` (para a lógica de combinações).

## 🚀 Como rodar localmente
1. Clone o repositório.
2. Instale as dependências: `pip install streamlit streamlit-option-menu streamlit-lottie requests`
3. Execute o comando: `streamlit run nome_do_seu_arquivo.py`
