# 🛡️ Conciliador Financeiro Seguro

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://conciliador-notas-j6zs7xlhec5cqht6kwv6nh.streamlit.app/)

<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1OGbyru3T_W05m-wZA0LnuDbMDAVu5f5I" alt="Demonstração do Conciliador Financeiro" width="100%">
</p>>

O **Conciliador Financeiro Seguro** é uma ferramenta de alta performance desenvolvida para automatizar a identificação de lotes de notas fiscais. Utilizando algoritmos avançados de busca, a aplicação resolve o desafio de encontrar quais combinações de valores (positivos ou negativos) resultam num montante específico de depósito ou pagamento.

## 🔗 Acesse a aplicação
[Clique aqui para utilizar o Conciliador](https://conciliador-notas-j6zs7xlhec5cqht6kwv6nh.streamlit.app/)

## 🚀 Diferenciais Técnicos
Diferente de abordagens simples de "força bruta", esta ferramenta foi projetada para cenários reais de alta complexidade:

* **Algoritmo de Programação Dinâmica:** Processamento ultra rápido que utiliza memorização para resolver o *Subset Sum Problem*, permitindo analisar dezenas de notas em segundos.
* **Modo Auditoria (Busca Profunda):** Capacidade de localizar múltiplas combinações diferentes para o mesmo valor alvo, essencial para identificar falsos positivos em grandes volumes de dados.
* **Precisão de Centavos:** Cálculos realizados inteiramente em escala de inteiros (centavos) para anular erros de arredondamento comuns em sistemas de ponto flutuante.
* **Tratamento de Abatimentos:** Suporte total para valores negativos, permitindo conciliar notas de crédito e devoluções no mesmo lote.
* **Margem de Tolerância:** Ajuste fino para encontrar combinações mesmo com pequenas variações de juros ou descontos.

## ✨ Funcionalidades
* **Sanitização Automática:** Extrai apenas os números de textos sujos (copiados de folhas de cálculo ou PDFs), ignorando símbolos como "R$".
* **Camadas de Segurança:** Sistema de *timeout* (60s) e limite de resultados para proteção de memória e processamento.
* **Interface Corporativa:** Design limpo e direto, focado em produtividade e análise de dados.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.x
- **Interface:** Streamlit
- **Componentes:** `streamlit-option-menu`
- **Lógica:** Algoritmos de Backtracking Otimizado e Programação Dinâmica.

## 💻 Instalação Local
1. Clone o repositório:
   ```bash
   git clone [https://github.com/Taff4/conciliador-notas.git](https://github.com/Taff4/conciliador-notas.git)
2. Instale as dependências: `pip install streamlit streamlit-option-menus`
3. Inicie a aplicação: `streamlit run app.py`
