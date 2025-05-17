# Documentação do Site de Análise de Vendas de Cerveja

## Visão Geral

Este documento fornece informações sobre o site interativo de análise de dados de vendas de cerveja desenvolvido com Streamlit e Plotly. O site simula o fluxo completo de um projeto de ciência de dados, desde a ingestão de dados até a geração de insights estratégicos.

## Estrutura do Site

O site está organizado em sete etapas didáticas:

1. **Ingestão de Dados**: Upload do arquivo CSV e visualização dos dados brutos.
2. **Limpeza e Pré-processamento**: Verificação de valores ausentes, outliers e tipos de dados.
3. **Análise Exploratória**: Estatísticas descritivas e análise inicial dos padrões de vendas.
4. **Visualizações Interativas**: Gráficos dinâmicos com filtros para explorar os dados.
5. **Análise de Correlações**: Relações entre vendas e fatores como estação, localidade e temperatura.
6. **Insights com IA**: Integração com ChatGPT para gerar insights estratégicos.
7. **Conclusões e Recomendações**: Resumo das descobertas e sugestões para otimização de vendas.

## Requisitos

- Arquivo CSV com dados de vendas de cerveja (formato semelhante ao exemplo fornecido)
- Chave API válida do ChatGPT para a geração de insights

## Como Usar

1. Acesse o site através do link fornecido
2. Insira sua chave API do ChatGPT na barra lateral
3. Faça upload do arquivo CSV ou use o arquivo de exemplo
4. Navegue pelas diferentes etapas do processo usando os botões ou a barra lateral
5. Explore as visualizações interativas usando os filtros disponíveis
6. Gere insights personalizados com o ChatGPT na etapa 6
7. Revise as conclusões e recomendações na etapa final

## Funcionalidades Principais

- **Upload de Arquivo**: Suporte para arquivos CSV com dados de vendas de cerveja
- **Validação de API**: Verificação da chave API do ChatGPT
- **Visualizações Interativas**: Gráficos dinâmicos com Plotly
- **Filtros Personalizados**: Seleção por cidade, bairro e estação
- **Análise de Correlação**: Identificação de padrões e relações nos dados
- **Integração com IA**: Geração de insights estratégicos com ChatGPT
- **Explicações Didáticas**: Informações sobre cada etapa do processo de ciência de dados

## Arquivos do Projeto

- `app.py`: Código principal do aplicativo Streamlit
- `vendas_cerveja_expandida.csv`: Arquivo de exemplo com dados de vendas

## Notas Importantes

- O acesso ao site é temporário e será disponível apenas durante a sessão de teste
- Para uso contínuo, o código pode ser executado localmente ou implantado em um servidor
- A chave API do ChatGPT é necessária apenas para a etapa 6 (Insights com IA)
- Todas as visualizações são interativas e respondem aos filtros aplicados
