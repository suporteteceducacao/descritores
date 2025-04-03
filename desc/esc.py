import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import os
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações da página
def configure_page():
    st.set_page_config(
        layout="wide",
        page_title="Análise de Desempenho Educacional",
        page_icon="📊",
        initial_sidebar_state="expanded"
    )

# Função para converter gráficos para imagem PNG
def plotly_to_png(fig):
    """Converte um gráfico Plotly para imagem PNG em bytes"""
    try:
        return fig.to_image(format="png", scale=2)
    except Exception as e:
        logger.error(f"Erro ao converter gráfico para PNG: {e}")
        return None

# Função para carregar dados do Excel
def load_data(file_path):
    """
    Carrega dados do arquivo Excel com tratamento de erros
    Retorna DataFrame ou None em caso de erro
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return None

        xls = pd.ExcelFile(file_path)
        
        # Verificar se a planilha existe
        if '5°_ANO_E_9°_ANO' not in xls.sheet_names:
            logger.error("Planilha '5°_ANO_E_9°_ANO' não encontrada")
            return None

        df = pd.read_excel(xls, sheet_name='5°_ANO_E_9°_ANO')
        
        # Verificar colunas obrigatórias
        required_columns = {
            'ESCOLA': str,
            'DESEMPENHO': (float, int),
            'QUESTÃO': str,
            'DESCRITOR': str,
            'ETAPA': str,
            'COMP. CURRICULAR': str
        }

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"Colunas obrigatórias faltando: {missing_cols}")
            return None
            
        return df
            
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return None

# Componente de métricas em cards estilizados
def show_metrics_cards(df):
    """Exibe métricas em cards estilizados com destaque para valores abaixo de 50%"""
    try:
        avg_score = df['DESEMPENHO'].mean()
        max_score = df['DESEMPENHO'].max()
        min_score = df['DESEMPENHO'].min()
        count = len(df)
        
        # Definir cores com base nos valores
        avg_color = "red" if avg_score < 50 else "green"
        min_color = "red" if min_score < 50 else "green"
        
        # Layout dos cards
        col1, col2, col3, col4 = st.columns(4)
        
        # Card 1 - Média Geral
        col1.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Média Geral</h3>
            <h1 style="margin: 10px 0; color: {avg_color};">{avg_score:.1f}%</h1>
            <p style="margin: 0; color: #666;">Total de questões: {count}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 2 - Melhor Desempenho
        col2.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Melhor Desempenho</h3>
            <h1 style="margin: 10px 0; color: green;">{max_score:.1f}%</h1>
            <p style="margin: 0; color: #666;">Alto desempenho</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 3 - Pior Desempenho
        col3.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Baixo Desempenho</h3>
            <h1 style="margin: 10px 0; color: {min_color};">{min_score:.1f}%</h1>
            <p style="margin: 0; color: #666;">{'Necessita atenção' if min_score < 50 else 'Desempenho regular'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 4 - Quantidade
        col4.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Total Analisado</h3>
            <h1 style="margin: 10px 0; color: #1a73e8;">{count}</h1>
            <p style="margin: 0; color: #666;">Questões filtradas</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Adicionar espaço
        st.markdown("<br>", unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Erro ao exibir métricas: {e}")
        st.error("Erro ao calcular métricas")

# Componente de gráficos aprimorados
def create_enhanced_plots(df):
    """Cria e exibe os gráficos principais com melhorias visuais"""
    try:
        # Configurações comuns para os gráficos
        common_config = {
            'height': 700,
            'width': 1300,
            'text_auto': '.1f',
            'labels': {'DESEMPENHO': 'Desempenho (%)'},
            'color_discrete_sequence': px.colors.qualitative.Plotly
        }

        # Gráfico 1 - Desempenho por Escola e Componente
        st.subheader("📈 Desempenho Médio por Escola e Componente")
        
        # Agrupar por escola e componente
        grouped_data = df.groupby(['ESCOLA', 'COMP. CURRICULAR'])['DESEMPENHO'].mean().reset_index()
        
        fig1 = px.bar(
            grouped_data,
            x='ESCOLA', 
            y='DESEMPENHO', 
            color='COMP. CURRICULAR', 
            barmode='group',
            **common_config,
            title="Média de Desempenho por Escola e Componente Curricular"
        )
        
        # Ajustes de layout para o primeiro gráfico
        fig1.update_layout(
            hovermode="x unified",
            xaxis_title="Escola",
            yaxis_title="Desempenho (%)",
            legend_title="Componente Curricular",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            title_font_size=20,
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )
        
        # Aumentar tamanho dos rótulos
        fig1.update_traces(
            textfont_size=18,
            textposition="outside",
            cliponaxis=False
        )
        
        # Exibir gráfico e opção de download
        col1, col2 = st.columns([5, 1])
        col1.plotly_chart(fig1, use_container_width=True)
        
        img_bytes = plotly_to_png(fig1)
        if img_bytes:
            col2.download_button(
                label="⬇️ JPEG",
                data=img_bytes,
                file_name="desempenho_por_escola_componente.png",
                mime="image/png",
                help="Download do gráfico como imagem PNG"
            )

        # Gráfico 2 - Desempenho por Descritor e Etapa
        st.subheader("📊 Desempenho por Descritor")
        
        # Opções de agrupamento
        group_by = st.radio(
            "Agrupar por:",
            options=['ETAPA', 'COMP. CURRICULAR'],
            horizontal=True,
            index=0,
            key="group_by_selector"
        )
        
        # Ordenação
        sort_order = st.radio(
            "Ordenar por:",
            options=['Maiores médias', 'Menores médias'],
            horizontal=True,
            index=0,
            key="sort_order"
        )
        
        # Preparar dados
        sorted_df = df.groupby(['DESCRITOR', group_by])['DESEMPENHO'].mean().reset_index()
        sorted_df = sorted_df.sort_values(
            'DESEMPENHO', 
            ascending=(sort_order == 'Menores médias')
        )
        
        # Criar gráfico
        fig2 = px.bar(
            sorted_df,
            x='DESCRITOR', 
            y='DESEMPENHO', 
            color=group_by,
            **common_config,
            title=f"Desempenho por Descritor (Agrupado por {group_by})"
        )
        
        fig2.update_layout(
            xaxis_title="Descritor",
            yaxis_title="Desempenho (%)",
            legend_title=group_by.capitalize(),
            xaxis={'categoryorder':'total descending' if sort_order == 'Maiores médias' else 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            title_font_size=20,
            showlegend=True
        )
                
        # Aumentar tamanho dos rótulos e destaque para <50%
        fig2.update_traces(
            textfont_size=18,
            textposition="outside",
            marker_color=np.where(sorted_df['DESEMPENHO'] < 50, 'red', px.colors.qualitative.Plotly[0])
        )
        
        # Exibir gráfico e opção de download
        col1, col2 = st.columns([5, 1])
        col1.plotly_chart(fig2, use_container_width=True)
        
        img_bytes = plotly_to_png(fig2)
        if img_bytes:
            col2.download_button(
                label="⬇️ JPEG",
                data=img_bytes,
                file_name="desempenho_por_descritor.png",
                mime="image/png",
                help="Download do gráfico como imagem PNG"
            )

    except Exception as e:
        logger.error(f"Erro ao criar gráficos: {e}")
        st.error("Erro ao gerar visualizações")

# Componente de tabela detalhada
def show_enhanced_data_table(df):
    """Exibe a tabela detalhada com melhorias visuais"""
    try:
        st.subheader("📋 Dados Detalhados")
        
        # Formatar a coluna de porcentagem e aplicar destaque
        def color_low(val):
            color = 'red' if val < 50 else 'black'
            return f'color: {color}; font-weight: bold'
        
        styled_df = df.style.format({'DESEMPENHO': '{:.1f}%'})\
            .applymap(color_low, subset=['DESEMPENHO'])
        
        # Exibir tabela com configurações
        st.dataframe(
            styled_df,
            column_config={
                "DESEMPENHO": st.column_config.ProgressColumn(
                    "Desempenho",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
                "ESCOLA": st.column_config.TextColumn(
                    "Escola",
                    width="large"
                ),
                "DESCRITOR": st.column_config.TextColumn(
                    "Descritor",
                    width="medium"
                )
            },
            hide_index=True,
            use_container_width=True,
            height=600
        )
        
        # Opções de download
        st.markdown("### Exportar Dados")
        col1, col2 = st.columns(2)
        col1.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='desempenho_filtrado.csv',
            mime='text/csv',
            help="Download dos dados atualmente filtrados"
        )
        col2.download_button(
            label="📥 Baixar dados completos (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='desempenho_completo.csv',
            mime='text/csv',
            help="Download de todos os dados disponíveis"
        )

    except Exception as e:
        logger.error(f"Erro ao exibir tabela: {e}")
        st.error("Erro ao exibir dados detalhados")

# Função principal
def main():
    configure_page()
    
    st.title("📊 Dashboard de Desempenho Avaliação Diagnóstica Municipal 2025.1")
    st.markdown("Análise dinâmica dos resultados por escola, descritor, componente curricular e etapa")

    # Configuração do caminho do arquivo
    st.sidebar.title("Configuração")
    file_path = st.sidebar.text_input(
        "Caminho do arquivo Excel:",
        value="desc/data/desempenho.xlsx"
    )

    # Carregar dados
    df = load_data(file_path)
    if df is None:
        st.error("""
        Não foi possível carregar os dados. Verifique:
        1. Se o caminho do arquivo está correto
        2. Se o arquivo tem a planilha '5°_ANO_E_9°_ANO'
        3. Se as colunas obrigatórias estão presentes
        """)
        return

    # Filtros
    st.sidebar.title("Filtros")
    
    # Filtro por escola usando selectbox
    escolas = st.sidebar.selectbox(
    "Selecione a escola:",
    options=sorted(df['ESCOLA'].unique())
    )
    
    # Mostrar nome da escola selecionada abaixo do título
    #st.sidebar.markdown(f"### 🏫 Escola selecionada: **{escolas}**")

    # Filtro por etapa/ano
    etapas = st.sidebar.selectbox(
        "Selecione a(s) etapa(s):",
        options=sorted(df['ETAPA'].unique())
    )

    # Filtro por componente curricular
    componentes = st.sidebar.multiselect(
        "Selecione o(s) componente(s) curricular(es):",
        options=sorted(df['COMP. CURRICULAR'].unique()),
        default=sorted(df['COMP. CURRICULAR'].unique())
    )

    # Filtro por intervalo de desempenho
    min_score, max_score = st.sidebar.slider(
        "Intervalo de desempenho (%):",
        min_value=0,
        max_value=100,
        value=(0, 100)
    )

    # Filtro por descritor específico
    descritores = st.sidebar.multiselect(
        "Selecione descritores específicos (opcional):",
        options=sorted(df['DESCRITOR'].unique())
    )

    # Aplicar filtros
    filtered_df = df[
        (df['ESCOLA'].isin([escolas]))&
        (df['ETAPA'].isin([etapas])) & 
        (df['COMP. CURRICULAR'].isin(componentes)) &
        (df['DESEMPENHO'] >= min_score) &
        (df['DESEMPENHO'] <= max_score)
    ]

    if descritores:
        filtered_df = filtered_df[filtered_df['DESCRITOR'].isin(descritores)]

    if filtered_df.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return

    # Exibir métricas em cards
    show_metrics_cards(filtered_df)
    
    # Abas para análise detalhada
    tab1, tab2 = st.tabs(["📈 Visualizações Gráficas", "📋 Dados Detalhados"])
    
    with tab1:
        create_enhanced_plots(filtered_df)
    
    with tab2:
        show_enhanced_data_table(filtered_df)

    # Rodapé
    st.markdown("---")
    st.markdown(f"📌 **Dashboard carregado a partir de:** `{file_path}`")
    st.markdown("ℹ️ Utilize os filtros no menu lateral para explorar os dados")

    # Rodapé com copyright
    st.markdown(
        """
        <style>
        .footer {
            font-size: 14px !important;
            text-align: center;
            color: #666;
            margin-top: 50px;
        }
        </style>
        <p class="footer"><br><br>© 2024 Dashborad Análise Avaliação Diagnóstica Municipal 2025 - Setor de Processamento e Monitoramento de Resultados.</p>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()