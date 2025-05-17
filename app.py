import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import openai
import os
import json
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise de Vendas de Cerveja",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para aplicar estilo CSS personalizado
def local_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.8rem;
            color: #2563EB;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .step-header {
            font-size: 1.5rem;
            color: #3B82F6;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
            background-color: #EFF6FF;
            padding: 0.5rem;
            border-radius: 0.5rem;
        }
        .info-box {
            background-color: #DBEAFE;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .warning-box {
            background-color: #FEF3C7;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .success-box {
            background-color: #D1FAE5;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .stProgress > div > div > div > div {
            background-color: #3B82F6;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Título e introdução
st.markdown("<h1 class='main-header'>Análise de Vendas de Cerveja</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='info-box'>
Este aplicativo simula o fluxo completo de um projeto de ciência de dados, demonstrando visualmente cada etapa do processamento dos dados, como um cientista de dados faria: desde a ingestão do arquivo, limpeza, análise exploratória, até a construção de insights estratégicos.
</div>
""", unsafe_allow_html=True)

# Inicialização de variáveis de sessão
if 'data' not in st.session_state:
    st.session_state.data = None
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'insights' not in st.session_state:
    st.session_state.insights = None

# Barra lateral para navegação e configurações
with st.sidebar:
    st.markdown("## Navegação")
    
    # Chave API do ChatGPT
    api_key = st.text_input("Chave API do ChatGPT", type="password")
    
    if api_key:
        # Validar a chave API
        try:
            openai.api_key = api_key
            # Teste simples para verificar se a chave é válida
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Olá"}],
                max_tokens=5
            )
            st.session_state.api_key_valid = True
            st.success("✅ Chave API válida!")
        except Exception as e:
            st.session_state.api_key_valid = False
            st.error(f"❌ Chave API inválida: {str(e)}")
    
    # Etapas do processo
    st.markdown("### Etapas do Processo")
    steps = [
        "1. Ingestão de Dados",
        "2. Limpeza e Pré-processamento",
        "3. Análise Exploratória",
        "4. Visualizações Interativas",
        "5. Análise de Correlações",
        "6. Insights com IA",
        "7. Conclusões e Recomendações"
    ]
    
    for i, step in enumerate(steps, 1):
        if st.button(step, key=f"step_{i}"):
            st.session_state.current_step = i

# Função para chamar a API do ChatGPT
def get_chatgpt_insights(data_summary, question):
    if not st.session_state.api_key_valid:
        return "Por favor, insira uma chave API válida do ChatGPT para gerar insights."
    
    try:
        prompt = f"""
        Você é um analista de dados especializado em vendas de cerveja. Com base nos seguintes dados:
        
        {data_summary}
        
        {question}
        
        Forneça uma análise detalhada com insights estratégicos e recomendações práticas. 
        Organize sua resposta em tópicos claros e inclua sugestões específicas para otimização de vendas.
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao chamar a API do ChatGPT: {str(e)}"

# Função para carregar e processar o arquivo CSV
def load_data(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {str(e)}")
        return None

# Função para limpar e pré-processar os dados
def preprocess_data(df):
    # Cópia para não modificar o original
    df_clean = df.copy()
    
    # Verificar valores ausentes
    missing_values = df_clean.isnull().sum()
    
    # Verificar tipos de dados
    dtypes = df_clean.dtypes
    
    # Converter colunas se necessário
    if 'Vendas (litros)' in df_clean.columns:
        df_clean['Vendas (litros)'] = pd.to_numeric(df_clean['Vendas (litros)'], errors='coerce')
    
    # Verificar outliers nas vendas
    if 'Vendas (litros)' in df_clean.columns:
        Q1 = df_clean['Vendas (litros)'].quantile(0.25)
        Q3 = df_clean['Vendas (litros)'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df_clean[(df_clean['Vendas (litros)'] < lower_bound) | (df_clean['Vendas (litros)'] > upper_bound)]
    else:
        outliers = pd.DataFrame()
    
    return df_clean, missing_values, dtypes, outliers

# Função para gerar estatísticas descritivas
def generate_stats(df):
    if 'Vendas (litros)' in df.columns:
        stats = df['Vendas (litros)'].describe()
        
        # Estatísticas por marca
        brand_stats = df.groupby('Marca')['Vendas (litros)'].agg(['mean', 'median', 'std', 'sum']).reset_index()
        brand_stats.columns = ['Marca', 'Média', 'Mediana', 'Desvio Padrão', 'Total']
        
        # Estatísticas por estação
        season_stats = df.groupby('Estação')['Vendas (litros)'].agg(['mean', 'median', 'std', 'sum']).reset_index()
        season_stats.columns = ['Estação', 'Média', 'Mediana', 'Desvio Padrão', 'Total']
        
        # Estatísticas por cidade e bairro
        location_stats = df.groupby(['Cidade', 'Bairro'])['Vendas (litros)'].agg(['mean', 'sum']).reset_index()
        location_stats.columns = ['Cidade', 'Bairro', 'Média', 'Total']
        
        return stats, brand_stats, season_stats, location_stats
    else:
        return None, None, None, None

# Função para gerar visualizações
def create_visualizations(df):
    visualizations = {}
    
    if 'Vendas (litros)' in df.columns:
        # Vendas por marca
        fig_brands = px.bar(
            df.groupby('Marca')['Vendas (litros)'].sum().reset_index(),
            x='Marca',
            y='Vendas (litros)',
            title='Vendas Totais por Marca',
            color='Marca',
            template='plotly_white'
        )
        visualizations['brands'] = fig_brands
        
        # Vendas por estação
        fig_seasons = px.bar(
            df.groupby('Estação')['Vendas (litros)'].sum().reset_index(),
            x='Estação',
            y='Vendas (litros)',
            title='Vendas Totais por Estação',
            color='Estação',
            category_orders={"Estação": ["Verão", "Outono", "Inverno", "Primavera"]},
            template='plotly_white'
        )
        visualizations['seasons'] = fig_seasons
        
        # Vendas por cidade e bairro
        fig_locations = px.bar(
            df.groupby(['Cidade', 'Bairro'])['Vendas (litros)'].sum().reset_index(),
            x='Bairro',
            y='Vendas (litros)',
            color='Cidade',
            title='Vendas Totais por Localidade',
            barmode='group',
            template='plotly_white'
        )
        visualizations['locations'] = fig_locations
        
        # Vendas por marca e estação
        fig_brand_season = px.bar(
            df.groupby(['Marca', 'Estação'])['Vendas (litros)'].sum().reset_index(),
            x='Estação',
            y='Vendas (litros)',
            color='Marca',
            title='Vendas por Marca e Estação',
            barmode='group',
            category_orders={"Estação": ["Verão", "Outono", "Inverno", "Primavera"]},
            template='plotly_white'
        )
        visualizations['brand_season'] = fig_brand_season
        
        # Distribuição das vendas
        fig_dist = px.histogram(
            df,
            x='Vendas (litros)',
            nbins=20,
            title='Distribuição das Vendas',
            template='plotly_white'
        )
        visualizations['distribution'] = fig_dist
        
    return visualizations

# Função para analisar correlações
def analyze_correlations(df):
    correlations = {}
    
    if 'Vendas (litros)' in df.columns:
        # Correlação entre marca e vendas
        brand_corr = df.groupby('Marca')['Vendas (litros)'].mean().reset_index()
        brand_corr = brand_corr.sort_values('Vendas (litros)', ascending=False)
        
        # Correlação entre estação e vendas
        season_corr = df.groupby('Estação')['Vendas (litros)'].mean().reset_index()
        season_order = {"Estação": ["Verão", "Outono", "Inverno", "Primavera"]}
        season_corr = season_corr.set_index('Estação').reindex(season_order["Estação"]).reset_index()
        
        # Correlação entre localidade e vendas
        location_corr = df.groupby(['Cidade', 'Bairro'])['Vendas (litros)'].mean().reset_index()
        location_corr = location_corr.sort_values('Vendas (litros)', ascending=False)
        
        # Correlação entre marca e estação
        brand_season_corr = df.pivot_table(
            index='Marca',
            columns='Estação',
            values='Vendas (litros)',
            aggfunc='mean'
        ).reset_index()
        
        correlations['brand'] = brand_corr
        correlations['season'] = season_corr
        correlations['location'] = location_corr
        correlations['brand_season'] = brand_season_corr
        
        # Simulação de dados climáticos
        # Criando uma relação simulada entre estação e temperatura média
        temp_map = {
            'Verão': np.random.normal(30, 2, size=len(df[df['Estação'] == 'Verão'])),
            'Outono': np.random.normal(22, 2, size=len(df[df['Estação'] == 'Outono'])),
            'Inverno': np.random.normal(15, 2, size=len(df[df['Estação'] == 'Inverno'])),
            'Primavera': np.random.normal(25, 2, size=len(df[df['Estação'] == 'Primavera']))
        }
        
        df_climate = df.copy()
        df_climate['Temperatura'] = df_climate['Estação'].map(lambda x: np.random.choice(temp_map[x]))
        
        # Correlação entre temperatura e vendas
        climate_corr = df_climate.groupby('Temperatura').agg({'Vendas (litros)': 'mean'}).reset_index()
        climate_corr = climate_corr.sort_values('Temperatura')
        
        correlations['climate'] = climate_corr
        correlations['df_climate'] = df_climate
    
    return correlations

# Função para gerar visualizações de correlação
def create_correlation_visualizations(correlations):
    corr_viz = {}
    
    if correlations:
        # Visualização da correlação entre temperatura e vendas
        if 'climate' in correlations:
            fig_climate = px.scatter(
                correlations['climate'],
                x='Temperatura',
                y='Vendas (litros)',
                title='Relação entre Temperatura e Vendas',
                trendline='ols',
                template='plotly_white'
            )
            corr_viz['climate'] = fig_climate
        
        # Mapa de calor da correlação entre marca e estação
        if 'brand_season' in correlations:
            brand_season_pivot = correlations['brand_season'].set_index('Marca')
            fig_heatmap = px.imshow(
                brand_season_pivot,
                title='Mapa de Calor: Vendas por Marca e Estação',
                labels=dict(x="Estação", y="Marca", color="Vendas (litros)"),
                x=brand_season_pivot.columns,
                y=brand_season_pivot.index,
                color_continuous_scale='Blues',
                template='plotly_white'
            )
            corr_viz['heatmap'] = fig_heatmap
        
        # Visualização da correlação entre localidade e vendas
        if 'location' in correlations:
            fig_location = px.bar(
                correlations['location'].head(10),
                x='Bairro',
                y='Vendas (litros)',
                color='Cidade',
                title='Top 10 Localidades por Média de Vendas',
                template='plotly_white'
            )
            corr_viz['location'] = fig_location
        
        # Visualização da correlação entre estação e vendas
        if 'season' in correlations:
            fig_season = px.line(
                correlations['season'],
                x='Estação',
                y='Vendas (litros)',
                title='Média de Vendas por Estação',
                markers=True,
                template='plotly_white'
            )
            corr_viz['season'] = fig_season
            
        # Visualização da correlação entre marca e vendas por estação
        if 'df_climate' in correlations:
            fig_brand_temp = px.scatter(
                correlations['df_climate'],
                x='Temperatura',
                y='Vendas (litros)',
                color='Marca',
                title='Vendas por Temperatura e Marca',
                trendline='ols',
                template='plotly_white'
            )
            corr_viz['brand_temp'] = fig_brand_temp
    
    return corr_viz

# Função para gerar um resumo dos dados para o ChatGPT
def generate_data_summary(df, stats, brand_stats, season_stats, location_stats):
    summary = f"""
    Resumo dos dados de vendas de cerveja:
    
    Estatísticas gerais:
    - Total de registros: {len(df)}
    - Média de vendas: {stats['mean']:.2f} litros
    - Mediana de vendas: {stats['50%']:.2f} litros
    - Desvio padrão: {stats['std']:.2f} litros
    - Mínimo: {stats['min']:.2f} litros
    - Máximo: {stats['max']:.2f} litros
    
    Marcas presentes: {', '.join(df['Marca'].unique())}
    Cidades presentes: {', '.join(df['Cidade'].unique())}
    Bairros presentes: {', '.join(df['Bairro'].unique())}
    Estações do ano: {', '.join(df['Estação'].unique())}
    
    Top 3 marcas por vendas totais:
    {brand_stats.sort_values('Total', ascending=False).head(3)[['Marca', 'Total']].to_string(index=False)}
    
    Vendas por estação (total):
    {season_stats[['Estação', 'Total']].to_string(index=False)}
    
    Top 3 localidades por vendas totais:
    {location_stats.sort_values('Total', ascending=False).head(3)[['Cidade', 'Bairro', 'Total']].to_string(index=False)}
    """
    
    return summary

# Etapa 1: Ingestão de Dados
def step_1_data_ingestion():
    st.markdown("<h2 class='sub-header'>Etapa 1: Ingestão de Dados</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>O que é ingestão de dados?</b><br>
    A ingestão de dados é o processo de importar, transferir e carregar dados para uso ou armazenamento em um banco de dados ou sistema. 
    É o primeiro passo crucial em qualquer projeto de ciência de dados, pois determina a qualidade e a disponibilidade dos dados para análise.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload do Arquivo CSV")
        
        # Opção para usar o arquivo de exemplo ou fazer upload
        use_example = st.checkbox("Usar arquivo de exemplo", value=True)
        
        if use_example:
            file_path = "vendas_cerveja_expandida.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                st.session_state.data = df
                st.success(f"✅ Arquivo de exemplo carregado com sucesso: {len(df)} registros")
            else:
                st.error("❌ Arquivo de exemplo não encontrado")
        else:
            uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
            if uploaded_file is not None:
                df = load_data(uploaded_file)
                if df is not None:
                    st.session_state.data = df
                    st.success(f"✅ Arquivo carregado com sucesso: {len(df)} registros")
    
    with col2:
        if st.session_state.data is not None:
            st.markdown("### Visualização dos Dados Brutos")
            st.dataframe(st.session_state.data.head(10), use_container_width=True)
            
            st.markdown("### Informações do Dataset")
            st.write(f"**Número de registros:** {len(st.session_state.data)}")
            st.write(f"**Colunas:** {', '.join(st.session_state.data.columns)}")
    
    if st.session_state.data is not None:
        st.markdown("### Estrutura do Dataset")
        buffer = []
        buffer.append(f"**Dimensões:** {st.session_state.data.shape[0]} linhas x {st.session_state.data.shape[1]} colunas")
        
        for col in st.session_state.data.columns:
            unique_values = st.session_state.data[col].nunique()
            buffer.append(f"**{col}:** {unique_values} valores únicos")
        
        col1, col2 = st.columns(2)
        for i, item in enumerate(buffer):
            if i < len(buffer) // 2:
                col1.markdown(item)
            else:
                col2.markdown(item)
        
        if st.button("Avançar para Limpeza e Pré-processamento ▶️"):
            st.session_state.current_step = 2
            st.experimental_rerun()

# Etapa 2: Limpeza e Pré-processamento
def step_2_preprocessing():
    st.markdown("<h2 class='sub-header'>Etapa 2: Limpeza e Pré-processamento</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>Por que limpar e pré-processar dados?</b><br>
    A limpeza e o pré-processamento de dados são essenciais para garantir a qualidade e a confiabilidade das análises. 
    Dados brutos frequentemente contêm erros, valores ausentes ou inconsistências que podem comprometer os resultados. 
    Esta etapa prepara os dados para análise, removendo ruídos e garantindo que estejam em um formato adequado.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.data is not None:
        # Processar os dados
        df_clean, missing_values, dtypes, outliers = preprocess_data(st.session_state.data)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<h3 class='step-header'>Verificação de Valores Ausentes</h3>", unsafe_allow_html=True)
            if missing_values.sum() == 0:
                st.success("✅ Não foram encontrados valores ausentes no dataset!")
            else:
                st.warning(f"⚠️ Foram encontrados {missing_values.sum()} valores ausentes.")
                st.write(missing_values)
            
            st.markdown("<h3 class='step-header'>Tipos de Dados</h3>", unsafe_allow_html=True)
            st.write(dtypes)
        
        with col2:
            st.markdown("<h3 class='step-header'>Verificação de Outliers</h3>", unsafe_allow_html=True)
            if len(outliers) == 0:
                st.success("✅ Não foram detectados outliers significativos nas vendas.")
            else:
                st.warning(f"⚠️ Foram detectados {len(outliers)} possíveis outliers nas vendas.")
                st.dataframe(outliers.head())
            
            st.markdown("<h3 class='step-header'>Estatísticas Básicas</h3>", unsafe_allow_html=True)
            if 'Vendas (litros)' in df_clean.columns:
                st.write(df_clean['Vendas (litros)'].describe())
        
        st.markdown("<h3 class='step-header'>Dados Após Pré-processamento</h3>", unsafe_allow_html=True)
        st.dataframe(df_clean.head(10), use_container_width=True)
        
        # Atualizar os dados na sessão
        st.session_state.data = df_clean
        
        st.markdown("""
        <div class='success-box'>
        <b>Resultado do Pré-processamento:</b><br>
        Os dados foram verificados e estão prontos para análise. Foram realizadas verificações de valores ausentes, 
        tipos de dados e outliers. Os dados estão em um formato adequado para prosseguir com a análise exploratória.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Avançar para Análise Exploratória ▶️"):
            st.session_state.current_step = 3
            st.experimental_rerun()
    else:
        st.warning("⚠️ Por favor, carregue os dados na etapa anterior.")
        if st.button("Voltar para Ingestão de Dados ◀️"):
            st.session_state.current_step = 1
            st.experimental_rerun()

# Etapa 3: Análise Exploratória
def step_3_exploratory_analysis():
    st.markdown("<h2 class='sub-header'>Etapa 3: Análise Exploratória de Dados</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>O que é Análise Exploratória de Dados (EDA)?</b><br>
    A Análise Exploratória de Dados é o processo de examinar e investigar conjuntos de dados para descobrir padrões, 
    identificar anomalias, testar hipóteses e verificar suposições usando estatísticas e representações gráficas. 
    É uma etapa fundamental que ajuda a entender a estrutura e as características dos dados antes de aplicar técnicas mais avançadas.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.data is not None:
        # Gerar estatísticas
        stats, brand_stats, season_stats, location_stats = generate_stats(st.session_state.data)
        
        if stats is not None:
            st.markdown("<h3 class='step-header'>Estatísticas Descritivas Gerais</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.metric("Média de Vendas", f"{stats['mean']:.2f} litros")
                st.metric("Mínimo", f"{stats['min']:.2f} litros")
                st.metric("25%", f"{stats['25%']:.2f} litros")
            
            with col2:
                st.metric("Mediana", f"{stats['50%']:.2f} litros")
                st.metric("75%", f"{stats['75%']:.2f} litros")
                st.metric("Máximo", f"{stats['max']:.2f} litros")
            
            st.markdown("<h3 class='step-header'>Análise por Marca</h3>", unsafe_allow_html=True)
            st.dataframe(brand_stats, use_container_width=True)
            
            # Gráfico de barras para vendas totais por marca
            fig_brand = px.bar(
                brand_stats,
                x='Marca',
                y='Total',
                title='Vendas Totais por Marca',
                color='Marca',
                template='plotly_white'
            )
            st.plotly_chart(fig_brand, use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Análise por Estação</h3>", unsafe_allow_html=True)
            st.dataframe(season_stats, use_container_width=True)
            
            # Gráfico de barras para vendas totais por estação
            fig_season = px.bar(
                season_stats,
                x='Estação',
                y='Total',
                title='Vendas Totais por Estação',
                color='Estação',
                category_orders={"Estação": ["Verão", "Outono", "Inverno", "Primavera"]},
                template='plotly_white'
            )
            st.plotly_chart(fig_season, use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Análise por Localidade</h3>", unsafe_allow_html=True)
            st.dataframe(location_stats.sort_values('Total', ascending=False).head(10), use_container_width=True)
            
            # Gráfico de barras para vendas totais por localidade (top 10)
            fig_location = px.bar(
                location_stats.sort_values('Total', ascending=False).head(10),
                x='Bairro',
                y='Total',
                title='Top 10 Localidades por Vendas Totais',
                color='Cidade',
                template='plotly_white'
            )
            st.plotly_chart(fig_location, use_container_width=True)
            
            st.markdown("""
            <div class='success-box'>
            <b>Insights da Análise Exploratória:</b><br>
            A análise exploratória revelou padrões importantes nas vendas de cerveja por marca, estação do ano e localidade. 
            Estes insights iniciais fornecem uma base sólida para análises mais detalhadas e visualizações interativas na próxima etapa.
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Avançar para Visualizações Interativas ▶️"):
                st.session_state.current_step = 4
                st.experimental_rerun()
        else:
            st.error("❌ Não foi possível gerar estatísticas. Verifique se os dados contêm a coluna 'Vendas (litros)'.")
    else:
        st.warning("⚠️ Por favor, carregue os dados na primeira etapa.")
        if st.button("Voltar para Ingestão de Dados ◀️"):
            st.session_state.current_step = 1
            st.experimental_rerun()

# Etapa 4: Visualizações Interativas
def step_4_interactive_visualizations():
    st.markdown("<h2 class='sub-header'>Etapa 4: Visualizações Interativas</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>Por que visualizações interativas são importantes?</b><br>
    As visualizações interativas permitem explorar os dados de forma dinâmica, revelando padrões e relações que podem não ser evidentes em tabelas ou gráficos estáticos. 
    Elas facilitam a comunicação de insights complexos e permitem que os usuários explorem os dados de acordo com seus interesses específicos.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Filtros interativos
        st.markdown("<h3 class='step-header'>Filtros</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_cities = st.multiselect(
                "Selecione as Cidades",
                options=df['Cidade'].unique(),
                default=df['Cidade'].unique()
            )
        
        with col2:
            selected_neighborhoods = st.multiselect(
                "Selecione os Bairros",
                options=df['Bairro'].unique(),
                default=df['Bairro'].unique()
            )
        
        with col3:
            selected_seasons = st.multiselect(
                "Selecione as Estações",
                options=df['Estação'].unique(),
                default=df['Estação'].unique()
            )
        
        # Filtrar os dados
        filtered_df = df[
            (df['Cidade'].isin(selected_cities)) &
            (df['Bairro'].isin(selected_neighborhoods)) &
            (df['Estação'].isin(selected_seasons))
        ]
        
        if len(filtered_df) > 0:
            # Gerar visualizações
            visualizations = create_visualizations(filtered_df)
            
            st.markdown("<h3 class='step-header'>Vendas por Marca</h3>", unsafe_allow_html=True)
            st.plotly_chart(visualizations['brands'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Vendas por Estação</h3>", unsafe_allow_html=True)
            st.plotly_chart(visualizations['seasons'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Vendas por Localidade</h3>", unsafe_allow_html=True)
            st.plotly_chart(visualizations['locations'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Vendas por Marca e Estação</h3>", unsafe_allow_html=True)
            st.plotly_chart(visualizations['brand_season'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Distribuição das Vendas</h3>", unsafe_allow_html=True)
            st.plotly_chart(visualizations['distribution'], use_container_width=True)
            
            st.markdown("""
            <div class='success-box'>
            <b>Insights das Visualizações:</b><br>
            As visualizações interativas permitem explorar os dados de diferentes perspectivas, revelando padrões de vendas por marca, 
            estação do ano e localidade. Você pode usar os filtros acima para focar em segmentos específicos e descobrir insights mais detalhados.
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Avançar para Análise de Correlações ▶️"):
                st.session_state.current_step = 5
                st.experimental_rerun()
        else:
            st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.warning("⚠️ Por favor, carregue os dados na primeira etapa.")
        if st.button("Voltar para Ingestão de Dados ◀️"):
            st.session_state.current_step = 1
            st.experimental_rerun()

# Etapa 5: Análise de Correlações
def step_5_correlation_analysis():
    st.markdown("<h2 class='sub-header'>Etapa 5: Análise de Correlações</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>O que é análise de correlação?</b><br>
    A análise de correlação examina a relação entre diferentes variáveis para identificar padrões e dependências. 
    Uma correlação positiva indica que duas variáveis tendem a aumentar juntas, enquanto uma correlação negativa indica que uma variável tende a diminuir quando a outra aumenta. 
    Esta análise é crucial para entender os fatores que influenciam as vendas de cerveja.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.data is not None:
        # Analisar correlações
        correlations = analyze_correlations(st.session_state.data)
        
        if correlations:
            # Criar visualizações de correlação
            corr_viz = create_correlation_visualizations(correlations)
            
            st.markdown("<h3 class='step-header'>Relação entre Temperatura e Vendas</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div class='info-box'>
            <b>Nota:</b> Os dados de temperatura são simulados para demonstrar a análise de correlação com fatores climáticos.
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(corr_viz['climate'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Mapa de Calor: Vendas por Marca e Estação</h3>", unsafe_allow_html=True)
            st.plotly_chart(corr_viz['heatmap'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Top 10 Localidades por Média de Vendas</h3>", unsafe_allow_html=True)
            st.plotly_chart(corr_viz['location'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Média de Vendas por Estação</h3>", unsafe_allow_html=True)
            st.plotly_chart(corr_viz['season'], use_container_width=True)
            
            st.markdown("<h3 class='step-header'>Vendas por Temperatura e Marca</h3>", unsafe_allow_html=True)
            st.plotly_chart(corr_viz['brand_temp'], use_container_width=True)
            
            st.markdown("""
            <div class='success-box'>
            <b>Insights da Análise de Correlação:</b><br>
            A análise de correlação revela relações importantes entre as vendas de cerveja e fatores como temperatura, estação do ano e localidade. 
            Estas correlações fornecem insights valiosos para estratégias de marketing, gestão de estoque e segmentação de mercado.
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Avançar para Insights com IA ▶️"):
                st.session_state.current_step = 6
                st.experimental_rerun()
        else:
            st.error("❌ Não foi possível analisar correlações. Verifique se os dados contêm as colunas necessárias.")
    else:
        st.warning("⚠️ Por favor, carregue os dados na primeira etapa.")
        if st.button("Voltar para Ingestão de Dados ◀️"):
            st.session_state.current_step = 1
            st.experimental_rerun()

# Etapa 6: Insights com IA
def step_6_ai_insights():
    st.markdown("<h2 class='sub-header'>Etapa 6: Insights com IA</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>Como a IA pode ajudar na análise de dados?</b><br>
    A Inteligência Artificial pode processar grandes volumes de dados e identificar padrões complexos que podem passar despercebidos na análise humana. 
    Nesta etapa, utilizamos o ChatGPT para interpretar os resultados das análises anteriores e gerar insights estratégicos para otimização de vendas.
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.api_key_valid:
        st.warning("⚠️ Por favor, insira uma chave API válida do ChatGPT na barra lateral para gerar insights.")
    elif st.session_state.data is not None:
        # Gerar estatísticas para o resumo
        stats, brand_stats, season_stats, location_stats = generate_stats(st.session_state.data)
        
        if stats is not None:
            # Gerar resumo dos dados
            data_summary = generate_data_summary(
                st.session_state.data,
                stats,
                brand_stats,
                season_stats,
                location_stats
            )
            
            st.markdown("<h3 class='step-header'>Perguntas para o ChatGPT</h3>", unsafe_allow_html=True)
            
            # Opções de perguntas pré-definidas
            question_options = [
                "Quais são os principais insights estratégicos baseados nos dados de vendas?",
                "Como otimizar o estoque de cerveja com base nas tendências sazonais?",
                "Quais estratégias de marketing seriam mais eficazes para cada marca?",
                "Como segmentar o mercado com base nos padrões de consumo identificados?",
                "Quais são as oportunidades de crescimento em diferentes localidades?"
            ]
            
            selected_question = st.selectbox(
                "Selecione uma pergunta ou escreva a sua própria:",
                options=["Selecione uma pergunta..."] + question_options
            )
            
            custom_question = st.text_area(
                "Ou escreva sua própria pergunta:",
                height=100,
                placeholder="Ex: Quais são as melhores estratégias para aumentar as vendas durante o inverno?"
            )
            
            final_question = custom_question if custom_question else selected_question
            
            if final_question and final_question != "Selecione uma pergunta...":
                if st.button("Gerar Insights com IA"):
                    with st.spinner("Gerando insights com IA... Isso pode levar alguns segundos."):
                        insights = get_chatgpt_insights(data_summary, final_question)
                        st.session_state.insights = insights
            
            if st.session_state.insights:
                st.markdown("<h3 class='step-header'>Insights Gerados pela IA</h3>", unsafe_allow_html=True)
                st.markdown(st.session_state.insights)
                
                st.markdown("""
                <div class='success-box'>
                <b>Próximos Passos:</b><br>
                Os insights gerados pela IA podem ser utilizados para informar decisões estratégicas, como campanhas de marketing sazonais, 
                ajustes de estoque e segmentação de mercado. Na próxima etapa, apresentaremos um resumo das principais descobertas e recomendações.
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Avançar para Conclusões e Recomendações ▶️"):
                    st.session_state.current_step = 7
                    st.experimental_rerun()
        else:
            st.error("❌ Não foi possível gerar estatísticas. Verifique se os dados contêm a coluna 'Vendas (litros)'.")
    else:
        st.warning("⚠️ Por favor, carregue os dados na primeira etapa.")
        if st.button("Voltar para Ingestão de Dados ◀️"):
            st.session_state.current_step = 1
            st.experimental_rerun()

# Etapa 7: Conclusões e Recomendações
def step_7_conclusions():
    st.markdown("<h2 class='sub-header'>Etapa 7: Conclusões e Recomendações</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <b>Importância das conclusões e recomendações:</b><br>
    Esta etapa final sintetiza todas as descobertas e insights obtidos ao longo do processo de análise de dados. 
    As conclusões e recomendações transformam dados brutos em ações concretas que podem ser implementadas para otimizar as vendas de cerveja.
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.data is not None and st.session_state.insights:
        st.markdown("<h3 class='step-header'>Resumo do Projeto</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        Neste projeto, realizamos uma análise completa dos dados de vendas de cerveja, seguindo o fluxo de trabalho de um cientista de dados:
        
        1. **Ingestão de Dados**: Carregamos e examinamos a estrutura dos dados de vendas.
        
        2. **Limpeza e Pré-processamento**: Verificamos valores ausentes, outliers e garantimos a qualidade dos dados.
        
        3. **Análise Exploratória**: Calculamos estatísticas descritivas e identificamos padrões iniciais nos dados.
        
        4. **Visualizações Interativas**: Criamos gráficos dinâmicos para explorar os dados de diferentes perspectivas.
        
        5. **Análise de Correlações**: Examinamos relações entre vendas e fatores como estação do ano, localidade e temperatura.
        
        6. **Insights com IA**: Utilizamos o ChatGPT para interpretar os resultados e gerar insights estratégicos.
        """)
        
        st.markdown("<h3 class='step-header'>Principais Descobertas</h3>", unsafe_allow_html=True)
        
        # Gerar estatísticas
        stats, brand_stats, season_stats, location_stats = generate_stats(st.session_state.data)
        
        if stats is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top 3 Marcas por Vendas Totais")
                top_brands = brand_stats.sort_values('Total', ascending=False).head(3)
                for i, row in top_brands.iterrows():
                    st.metric(f"{i+1}. {row['Marca']}", f"{row['Total']:,.0f} litros")
            
            with col2:
                st.markdown("#### Estações por Vendas Totais")
                season_order = ["Verão", "Outono", "Inverno", "Primavera"]
                sorted_seasons = season_stats.set_index('Estação').loc[season_order].reset_index()
                for i, row in sorted_seasons.iterrows():
                    st.metric(f"{row['Estação']}", f"{row['Total']:,.0f} litros")
        
        st.markdown("<h3 class='step-header'>Insights Estratégicos da IA</h3>", unsafe_allow_html=True)
        st.markdown(st.session_state.insights)
        
        st.markdown("<h3 class='step-header'>Recomendações Finais</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        Com base em todas as análises realizadas, recomendamos:
        
        1. **Otimização de Estoque**: Ajustar o estoque de acordo com as tendências sazonais identificadas.
        
        2. **Campanhas de Marketing Direcionadas**: Desenvolver campanhas específicas para cada marca, considerando sua performance em diferentes estações e localidades.
        
        3. **Expansão Geográfica**: Focar em expandir a presença em bairros com alto potencial de vendas.
        
        4. **Promoções Sazonais**: Criar promoções especiais para as estações com menor volume de vendas.
        
        5. **Monitoramento Contínuo**: Implementar um sistema de monitoramento contínuo para acompanhar o desempenho das vendas e ajustar estratégias conforme necessário.
        """)
        
        st.markdown("""
        <div class='success-box'>
        <b>Conclusão do Projeto:</b><br>
        Este projeto demonstrou como a ciência de dados pode transformar dados brutos de vendas em insights estratégicos valiosos. 
        A combinação de técnicas estatísticas, visualizações interativas e inteligência artificial permite uma compreensão profunda dos padrões de vendas de cerveja, 
        fornecendo uma base sólida para decisões de negócios baseadas em dados.
        </div>
        """, unsafe_allow_html=True)
        
        # Botão para reiniciar o processo
        if st.button("Reiniciar Análise 🔄"):
            st.session_state.current_step = 1
            st.experimental_rerun()
    else:
        if not st.session_state.data:
            st.warning("⚠️ Por favor, carregue os dados na primeira etapa.")
        elif not st.session_state.insights:
            st.warning("⚠️ Por favor, gere insights com IA na etapa anterior.")
        
        if st.button("Voltar para Ingestão de Dados ◀️"):
            st.session_state.current_step = 1
            st.experimental_rerun()

# Executar a etapa atual
if st.session_state.current_step == 1:
    step_1_data_ingestion()
elif st.session_state.current_step == 2:
    step_2_preprocessing()
elif st.session_state.current_step == 3:
    step_3_exploratory_analysis()
elif st.session_state.current_step == 4:
    step_4_interactive_visualizations()
elif st.session_state.current_step == 5:
    step_5_correlation_analysis()
elif st.session_state.current_step == 6:
    step_6_ai_insights()
elif st.session_state.current_step == 7:
    step_7_conclusions()

# Rodapé
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray; font-size: 0.8rem;'>Análise de Vendas de Cerveja • Desenvolvido com Streamlit • {datetime.now().strftime('%Y-%m-%d')}</div>",
    unsafe_allow_html=True
)
