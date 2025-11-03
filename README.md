# 📄 Conciliador de Notas

Uma aplicação web desenvolvida em Python com Streamlit para encontrar a combinação exata de notas fiscais que somam um valor total de pagamento. Ideal para conciliação financeira automatizada.

## ✨ Funcionalidades Principais

- **Interface Intuitiva:** Design limpo e amigável, focado na facilidade de uso.
- **Validação Inteligente:** Aceita valores com ponto ou vírgula e ignora textos (como "R$"), prevenindo erros.
- **Feedback em Tempo Real:** Mostra a quantidade de notas válidas enquanto o usuário digita.
- **Busca Flexível:** Permite que o usuário defina a "profundidade da busca" para casos mais complexos, com avisos de performance.
- **Guia de Ajuda Integrado:** Uma seção de ajuda explica passo a passo como utilizar a ferramenta.

## 🚀 Como Usar a Aplicação

1.  Acesse a aba **Conciliador**.
2.  No campo **Valor Total do Pagamento**, insira o valor exato recebido.
3.  No campo **Lista de Notas em Aberto**, cole a lista de valores das notas pendentes.
4.  (Opcional) Expanda as **Opções Avançadas** para ajustar a profundidade da busca se a combinação envolver muitas notas.
5.  Clique em **Iniciar Análise** e aguarde o resultado.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python
- **Frontend:** Streamlit
- **Bibliotecas:** streamlit-option-menu, streamlit-lottie, requests