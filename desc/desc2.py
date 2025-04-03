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
        
        if 'DESCRITORES_2025' not in xls.sheet_names:
            logger.error("Planilha 'DESCRITORES_2025' não encontrada")
            return None

        df = pd.read_excel(xls, sheet_name='DESCRITORES_2025')
        
        # Remover coluna 'Unnamed: 0' se existir
        if 'Unnamed: 0' in df.columns:
            df.drop(columns=['Unnamed: 0'], inplace=True)
        
        # Verificar colunas obrigatórias
        required_columns = {
            'DESCRITOR': str,
            'MÉDIA ACERTOS (%)': (float, int),
            'COMPONENTE': str,
            'ETAPA': str,
            'DESCRIÇÃO': str
        }

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"Colunas obrigatórias faltando: {missing_cols}")
            return None

        # Converter porcentagens se necessário
        if df['MÉDIA ACERTOS (%)'].dtype == object:
            df['MÉDIA ACERTOS (%)'] = (
                df['MÉDIA ACERTOS (%)']
                .str.replace('%', '')
                .str.replace(',', '.')
                .astype(float))
            
        return df
            
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return None

# Componente de métricas em cards estilizados
def show_metrics_cards(df):
    """Exibe métricas em cards estilizados com destaque para valores abaixo de 50%"""
    try:
        avg_score = df['MÉDIA ACERTOS (%)'].mean()
        max_score = df['MÉDIA ACERTOS (%)'].max()
        min_score = df['MÉDIA ACERTOS (%)'].min()
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
            <p style="margin: 0; color: #666;">Total de descritores: {count}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 2 - Melhor Descritor
        col2.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Melhor Descritor</h3>
            <h1 style="margin: 10px 0; color: green;">{max_score:.1f}%</h1>
            <p style="margin: 0; color: #666;">Alto desempenho</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 3 - Pior Descritor
        col3.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Pior Descritor</h3>
            <h1 style="margin: 10px 0; color: {min_color};">{min_score:.1f}%</h1>
            <p style="margin: 0; color: #666;">{'Necessita atenção' if min_score < 50 else 'Desempenho regular'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 4 - Quantidade
        col4.markdown(f"""
        <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1)">
            <h3 style="margin: 0; color: #333;">Total Analisado</h3>
            <h1 style="margin: 10px 0; color: #1a73e8;">{count}</h1>
            <p style="margin: 0; color: #666;">Descritores filtrados</p>
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
            'width': 1300,  # Gráficos mais largos
            'text_auto': '.1f',
            'labels': {'MÉDIA ACERTOS (%)': 'Média de Acertos (%)'},
            'color_discrete_sequence': px.colors.qualitative.Plotly
        }

        # Gráfico 1 - Desempenho por Ano e Componente
        st.subheader("📈 Desempenho Médio por Ano e Componente")
        grouped_data = df.groupby(['ETAPA', 'COMPONENTE'])['MÉDIA ACERTOS (%)'].mean().reset_index()
        
        fig1 = px.bar(
            grouped_data,
            x='ETAPA', 
            y='MÉDIA ACERTOS (%)', 
            color='COMPONENTE', 
            barmode='group',
            **common_config,
            title="Média de Acertos por Ano e Componente Curricular"
        )
        
        # Ajustes de layout para o primeiro gráfico
        fig1.update_layout(
            hovermode="x unified",
            xaxis_title="Ano Escolar",
            yaxis_title="Média de Acertos (%)",
            legend_title="Componente Curricular",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),  # Fonte maior
            title_font_size=20,
            uniformtext_minsize=12,  # Tamanho mínimo do texto
            uniformtext_mode='hide'  # Esconder texto que não cabe
        )
        
        # Aumentar tamanho dos rótulos
        fig1.update_traces(
            textfont_size=14,
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
                file_name="desempenho_por_ano_componente.png",
                mime="image/png",
                help="Download do gráfico como imagem PNG"
            )

        # Gráfico 2 - Desempenho por Descritor
        st.subheader("📊 Desempenho por Descritor")
        
        # Opções de agrupamento
        group_by = st.radio(
            "Agrupar por:",
            options=['ETAPA', 'COMPONENTE'],
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
        sorted_df = df.sort_values(
            'MÉDIA ACERTOS (%)', 
            ascending=(sort_order == 'Menores médias')
        )
        
        # Criar gráfico
        fig2 = px.bar(
            sorted_df,
            x='DESCRITOR', 
            y='MÉDIA ACERTOS (%)', 
            color=group_by,
            hover_data=['DESCRIÇÃO', 'Nº QUESTÃO', 'COMPONENTE'],
            **common_config,
            title=f"Desempenho por Descritor (Agrupado por {group_by})"
        )
        
        fig2.update_layout(
            xaxis_title="Descritor",
            yaxis_title="Média de Acertos (%)",
            legend_title=group_by.capitalize(),
            xaxis={'categoryorder':'total descending' if sort_order == 'Maiores médias' else 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14),
            title_font_size=20,
            showlegend=True
        ).update_traces(
            marker_color=np.where(fig2.data[0].y < 50, 'red', 'blue')  # Vermelho para <50%, azul para >=50%)
        )
                
        # Aumentar tamanho dos rótulos e destaque para <50%
        fig2.update_traces(
            textfont_size=14,
            textposition="outside",
            marker_color=[
                'red' if x < 50 else px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] 
                for i, x in enumerate(sorted_df['MÉDIA ACERTOS (%)'])
        ])
        
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
        
        styled_df = df.style.format({'MÉDIA ACERTOS (%)': '{:.1f}%'})\
            .applymap(color_low, subset=['MÉDIA ACERTOS (%)'])
        
        # Exibir tabela com configurações
        st.dataframe(
            styled_df,
            column_config={
                "MÉDIA ACERTOS (%)": st.column_config.ProgressColumn(
                    "Média de Acertos",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
                "DESCRIÇÃO": st.column_config.TextColumn(
                    "Descrição do Descritor",
                    width="large"
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
    
    st.title("📊 Dashboard de Desempenho Educacional")
    st.markdown("Análise dinâmica dos resultados por descritor, componente curricular e ano escolar")

    # Configuração do caminho do arquivo
    st.sidebar.title("Configuração")
    file_path = st.sidebar.text_input(
        "Caminho do arquivo Excel:",
        value="desc/data/desempenho_grafico_descritores_2025.xlsx"
    )

    # Carregar dados
    df = load_data(file_path)
    if df is None:
        st.error("""
        Não foi possível carregar os dados. Verifique:
        1. Se o caminho do arquivo está correto
        2. Se o arquivo tem a planilha 'DESCRITORES_2025'
        3. Se as colunas obrigatórias estão presentes
        """)
        return

    # Filtros
    st.sidebar.title("Filtros")
    
    # Filtro por etapa/ano
    anos = st.sidebar.multiselect(
        "Selecione o(s) ano(s):",
        options=sorted(df['ETAPA'].unique()),
        default=sorted(df['ETAPA'].unique())
    )

    # Filtro por componente curricular
    componentes = st.sidebar.multiselect(
        "Selecione o(s) componente(s) curricular(es):",
        options=sorted(df['COMPONENTE'].unique()),
        default=sorted(df['COMPONENTE'].unique())
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
        (df['ETAPA'].isin(anos)) & 
        (df['COMPONENTE'].isin(componentes)) &
        (df['MÉDIA ACERTOS (%)'] >= min_score) &
        (df['MÉDIA ACERTOS (%)'] <= max_score)
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

if __name__ == "__main__":
    main()