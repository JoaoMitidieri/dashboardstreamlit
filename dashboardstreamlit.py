# Importando os Pacotes
# Manipulação de dados
import pandas as pd
import numpy as np
import datetime as dt

# Visualização
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Estatística
import scipy
from scipy.stats import normaltest
from scipy.stats import chi2_contingency

# Ignore Warning
import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")
import streamlit as st
import datetime
from PIL import Image
# Carregando Dados
vendas = pd.read_excel('fato_vendas.xlsx')
vendedor = pd.read_excel('dim_vendedor.xlsx')
produtos = pd.read_excel('dim_produtos.xlsx')
fam_produtos = pd.read_excel('dim_familia_produtos.xlsx')
# Criação da coluna
col1 = st.columns(1)

# HTML e CSS para o título
html_title = """
    <style>
    .title-test {
        font-weight: bold;
        padding: 5px;
        border-radius: 6px;
        text-align: center;
    }
    </style>
    <h1 class="title-test">DASHBOARD BRIGHT BUY </h1>
"""

# Uso da coluna e inserção do HTML
with col1[0]:  # Ajuste aqui para referenciar o primeiro elemento da lista de colunas
    st.markdown(html_title, unsafe_allow_html=True)

# Análise Exploratória do Dataframe Vendas
indice_linha_em_branco = vendas[vendas['codigo_cliente'].isnull()].index[0]

linha_em_branco = vendas.iloc[indice_linha_em_branco]


# Deletando linha em branco, pois não foi possível descobrir qual codigo do clinte 
vendas = vendas.drop(indice_linha_em_branco)

# Vendas Duplicatas
# Use loc para exibir apenas as linhas duplicadas no DataFrame original
vendas_duplicatas = vendas.loc[vendas.duplicated(keep=False)]

vendas.drop_duplicates(keep = 'last', inplace = True)


# Mês
vendas['mes'] = vendas['data_venda'].dt.month
agrupado_por_mes = vendas.groupby('mes')['valor_monetario_total'].agg(['count', 'sum']).reset_index()

agrupado_por_mes = agrupado_por_mes.rename(columns={'count': 'quantidade_vendas', 'sum': 'valor_monetario_total'})
# Semana
vendas['semana'] = vendas['data_venda'].dt.isocalendar().week


# Agrupe por mês e calcule a contagem de vendas e o valor monetário total
agrupado_por_semana = vendas.groupby('semana')['valor_monetario_total'].agg(['count', 'sum']).reset_index()

# Renomeie as colunas para maior clareza
agrupado_por_semana = agrupado_por_semana.rename(columns={'count': 'quantidade_vendas', 'sum': 'valor_monetario_total'})


# Criando o gráfico
fig = go.Figure()

# Adicionando a barra para a quantidade de vendas
fig.add_trace(go.Bar(
    x=agrupado_por_mes['mes'],
    y=agrupado_por_mes['quantidade_vendas'],
    name='Quantidade Vendida',
    marker_color='indigo'
))

# Adicionando a linha para o valor monetário total
fig.add_trace(go.Scatter(
    x=agrupado_por_mes['mes'],
    y=agrupado_por_mes['valor_monetario_total'],
    name='Faturamento',
    mode='lines+markers',
    yaxis='y2',
    line=dict(width=3)
))

# Ajustando o layout
fig.update_layout(
    title='Quantidade de Vendas e Faturamento por Mês',
    xaxis=dict(
        title='Mês',
        tickvals=agrupado_por_mes['mes'],
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ),
    yaxis=dict(title='Quantidade de Vendas'),
    yaxis2=dict(
        title='Faturamento ',
        overlaying='y',
        side='right'
    ),
    legend=dict(
        y=1.2,
        x=1
    ),
    height=500,
    width=1200
)


fig1 = go.Figure(go.Scatter(
    x=agrupado_por_semana['semana'],
    y=agrupado_por_semana['valor_monetario_total'],
    mode='lines+markers',
    line=dict(color='indigo'),
    marker=dict(color='indigo'),
))

# Adicionando rótulos e ajustando o layout
fig1.update_layout(
    title='Faturamento por Semanas do Ano',
    xaxis=dict(
        title='Semanas',
        tickmode='array',
        tickvals=list(range(1, 53)),  # Gera uma lista de 1 a 52 para as semanas
        ticktext=[str(i) for i in range(1, 53)]  # Rótulos de 1 a 52 como strings
    ),
    yaxis=dict(title='Faturamento'),
    height=500,
    width=1000,
)





# Merge entre vendas e produtos usando 'codigo_produto'
vendas_produtos = pd.merge(vendas, produtos, on='codigo_produto')

# Merge entre vendas_produtos e fam_produtos usando 'codigo_familia'
resultado_final = pd.merge(vendas_produtos, fam_produtos, on='codigo_familia')

vendedor_indicadores = pd.merge(resultado_final, vendedor, on='codigo_vendedor')

maior_faturamento_vendedor = vendedor_indicadores.groupby('nome_vendedor')['valor_monetario_total'].sum().reset_index().sort_values(by='valor_monetario_total', ascending=False)

melhor_volume_vendas = vendedor_indicadores.groupby('nome_vendedor')['valor_monetario_total'].count().reset_index().sort_values(by='valor_monetario_total', ascending=False)

ticket_medio = vendedor_indicadores.groupby('nome_vendedor')['valor_monetario_total'].mean().reset_index().sort_values(by='valor_monetario_total', ascending=False)

# Criação do gráfico
fig4 = go.Figure()

fig4.add_trace(go.Indicator(
    mode='number',
    value=maior_faturamento_vendedor['valor_monetario_total'][1],
    number={'valueformat': ".2s"},
    title={
        'text': f"Melhor Vendedor(a) - {maior_faturamento_vendedor['nome_vendedor'][1]}<br><span style='font-size:100%'>Faturamento Anual</span>"
    }
))

# Adição de anotações com informações adicionais
fig4.add_annotation(
    x=0.5,
    y=0.2,
    xref='paper',
    yref='paper',
    text=(
        f"Volume de Vendas: {melhor_volume_vendas['valor_monetario_total'][1]} vendas<br>"
        f"Ticket Médio: R$ {round(ticket_medio['valor_monetario_total'][1], 2):,} reais"
    ),
    showarrow=False
)

# Configurações do layout
fig4.update_layout(height=450)

# Criação do gráfico
fig5 = go.Figure()

fig5.add_trace(go.Indicator(
    mode='number',
    value=maior_faturamento_vendedor['valor_monetario_total'][20],
    number={'valueformat': ".2s"},
    title={
        'text': f"2º Melhor Vendedor(a) - {maior_faturamento_vendedor['nome_vendedor'][20]}<br><span style='font-size:100%'>Faturamento Anual</span>"
    }
))

# Adição de anotações com informações adicionais
fig5.add_annotation(
    x=0.5,
    y=0.2,
    xref='paper',
    yref='paper',
    text=(
        f"Volume de Vendas: {melhor_volume_vendas['valor_monetario_total'][20]} vendas<br>"
        f"Ticket Médio: R$ {round(ticket_medio['valor_monetario_total'][20], 2):,} reais"
    ),
    showarrow=False
)


# Criação do gráfico
fig6 = go.Figure()

fig6.add_trace(go.Indicator(
    mode='number',
    value=maior_faturamento_vendedor['valor_monetario_total'][34],
    number={'valueformat': ".2s"},
    title={
        'text': f"3º Melhor Vendedor(a) - {maior_faturamento_vendedor['nome_vendedor'][34]}<br><span style='font-size:100%'>Faturamento Anual</span>"
    }
))

# Adição de anotações com informações adicionais
fig6.add_annotation(
    x=0.5,
    y=0.2,
    xref='paper',
    yref='paper',
    text=(
        f"Volume de Vendas: {melhor_volume_vendas['valor_monetario_total'][34]} vendas<br>"
        f"Ticket Médio: R$ {round(ticket_medio['valor_monetario_total'][34], 2):,} reais"
    ),
    showarrow=False
)

# Configurações do layout
fig6.update_layout(height=450)

# Criação do gráfico
fig7 = go.Figure()

fig7.add_trace(go.Indicator(
    mode='number',
    value=maior_faturamento_vendedor['valor_monetario_total'][7],
    number={'valueformat': ".2s"},
    title={
        'text': f" 4º Melhor Vendedor(a) - {maior_faturamento_vendedor['nome_vendedor'][7]}<br><span style='font-size:100%'>Faturamento Anual</span>"
    }
))

# Adição de anotações com informações adicionais
fig7.add_annotation(
    x=0.5,
    y=0.2,
    xref='paper',
    yref='paper',
    text=(
        f"Volume de Vendas: {melhor_volume_vendas['valor_monetario_total'][7]} vendas<br>"
        f"Ticket Médio: R$ {round(ticket_medio['valor_monetario_total'][7], 2):,} reais"
    ),
    showarrow=False
)

# Configurações do layout
fig7.update_layout(height=450)

# Criação do gráfico
fig8 = go.Figure()

fig8.add_trace(go.Indicator(
    mode='number',
    value=maior_faturamento_vendedor['valor_monetario_total'][31],
    number={'valueformat': ".2s"},
    title={
        'text': f" 5º Melhor Vendedor(a) - {maior_faturamento_vendedor['nome_vendedor'][31]}<br><span style='font-size:100%'>Faturamento Anual</span>"
    }
))
# Adição de anotações com informações adicionais
fig8.add_annotation(
    x=0.5,
    y=0.2,
    xref='paper',
    yref='paper',
    text=(
        f"Volume de Vendas: {melhor_volume_vendas['valor_monetario_total'][31]} vendas<br>"
        f"Ticket Médio: R$ {round(ticket_medio['valor_monetario_total'][31], 2):,} reais"
    ),
    showarrow=False
)


# Substituindo 'Power Tools' por 'Tools'
resultado_final['descricaofamilia'] = resultado_final['descricaofamilia'].replace('Power Tools', 'Tools')
agrupado_por_familias = resultado_final.groupby('descricaofamilia')['valor_monetario_total'].sum().sort_values(ascending=False)

# Criar um gráfico de barras
fig9 = px.bar(agrupado_por_familias.reset_index(), 
             x='descricaofamilia',  # Usar o nome da coluna para as famílias de produtos
             y='valor_monetario_total',  # Coluna para o valor monetário total
             title="Faturamento por Famílias de Produtos",
             labels={'descricaofamilia': 'Família de Produtos', 'valor_monetario_total': 'Faturamento Total (R$)'})

# Ajustar o layout para aumentar a largura
fig9.update_layout(width=1100, height=600)  # Você pode ajustar estes valores conforme necessário

# Filtrando os dados para incluir apenas os meses de junho a dezembro
dados_filtrados = resultado_final[resultado_final['mes'].between(6, 12)]

# Agrupando por família e somando o valor monetário total
agrupado_por_familias1 = dados_filtrados.groupby('descricaofamilia')['valor_monetario_total'].sum().sort_values(ascending=False)

# Exibindo os cinco primeiros resultados
top_familias = agrupado_por_familias1.head()

fig10 = px.bar(top_familias.reset_index(), 
             x='valor_monetario_total',  # Coluna para o valor monetário total
             y='descricaofamilia',  # Usar o nome da coluna para as famílias de produtos
             orientation='h',  # Definir orientação horizontal
             title="Melhores Famílias de Produtos para Campanha de Dezembro",
             labels={'descricaofamilia': 'Família de Produtos', 'valor_monetario_total': 'Faturamento Total (R$)'})

# Ajustar o layout para definir a largura e a altura
fig10.update_layout(width=800, height=400)




num_meses_total = len(vendas['mes'].unique())
# Agrupe por cliente e conte o número de meses únicos
clientes_por_mes = vendas.groupby('codigo_cliente')['mes'].nunique().reset_index()

# Filtra os clientes que têm o número de meses únicos igual ao número total de meses
clientes_premium = clientes_por_mes[clientes_por_mes['mes'] == num_meses_total]['codigo_cliente']
fig11 = go.Figure()
fig11.add_trace(go.Indicator(
    mode='number',
    title = {
        "text": f"<span style='font-size:100%'>Clientes Frequentes</span><br><span style='font-size:60%'>Clientes que realizaram compras todos os meses</span>"
    },
    value = len(clientes_premium)
))

todos_clientes = vendas['codigo_cliente'].nunique()
contagem_retencao_cpf = vendas['codigo_cliente'].value_counts()
clientes_recorrentes = contagem_retencao_cpf[contagem_retencao_cpf > 1]
# Calcular o número de clientes não recorrentes
clientes_nao_recorrentes = len(contagem_retencao_cpf)- len(clientes_recorrentes)

# Dados para o gráfico de pizza
labels = ['Clientes Recorrentes', 'Clientes Não Recorrentes']
valores = [len(clientes_recorrentes), clientes_nao_recorrentes]
cores = ['lightcoral', 'lightskyblue']

# Criar um objeto go.Figure
fig12 = go.Figure()

# Adicionar o gráfico de pizza
fig12.add_trace(go.Pie(labels=labels, values=valores, textinfo='percent', 
                     marker=dict(colors=cores, line=dict(color='#000000', width=5)),
                     hole=0.5))

# Atualizar layout
fig12.update_layout(
    title='Proporção de Clientes Recorrentes',
    title_x=0.1,
    showlegend=True,
    legend=dict(x=0.6, y=0.2),
)
vendas['filial_venda'].value_counts()

vendas['filial_venda'].nunique()

filial = vendas.groupby(['filial_venda', 'mes'])['valor_monetario_total'].sum().reset_index()
tabela_pivot = filial.pivot(index='mes', columns='filial_venda', values='valor_monetario_total')
# Crie um objeto go.Figure
fig13 = go.Figure()

# Adicione barras empilhadas ao gráfico
for coluna in tabela_pivot.columns:
    fig13.add_trace(go.Bar(
        x=tabela_pivot.index,
        y=tabela_pivot[coluna],
        name=coluna
    ))

# Atualize o layout do gráfico
fig13.update_layout(
    title='Valor Monetário por Filial e Mês',
    xaxis=dict(title='Mês'),
    yaxis=dict(title='Valor Monetário Total'),
    barmode='stack'
)
# Adicionando rótulos ao eixo x
fig13.update_xaxes(tickvals=agrupado_por_mes['mes'], ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Aug', 'Set', 'Out', 'Nov', 'Dez'])


# Certifique-se de que os dados estão ordenados por mês
vendas.sort_values('mes', inplace=True)

# Calculando o faturamento total por mês
faturamento_mensal = vendas.groupby('mes')['valor_monetario_total'].sum()

# Calculando a Taxa Percentual de Crescimento Mensal
tpcm = faturamento_mensal.pct_change() * 100

# Substituindo NaN por 0 para o primeiro mês
tpcm = tpcm.fillna(0)
# Supondo que você tenha uma lista de meses correspondente
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Criando o gráfico de barras com a cor das barras alterada para violeta
fig14 = go.Figure(data=[
    go.Bar(x=meses, y=tpcm, marker_color='violet')  # Alterado para violeta
])

# Adicionando títulos e rótulos
fig14.update_layout(
    title='Taxa Percentual de Crescimento Mensal do Faturamento',
    xaxis_title='Mês',
    yaxis_title='Taxa de Crescimento (%)',
    template='plotly_white'  # Mantém o fundo branco do gráfico
)
# Ajustar o layout para definir a largura e a altura
fig10.update_layout(width=800, height=400)






# Definindo as colunas no Streamlit
col1, col2 = st.columns(2)

col1.plotly_chart(fig, use_container_width=True)
col2.plotly_chart(fig1, use_container_width=True)

st.divider()
col3, col4 = st.columns([0.3, 0.7])

with col3:
    st.plotly_chart(fig10, use_container_width=True)

with col4:
    st.plotly_chart(fig9, use_container_width=True)

st.divider()
col5, col6, col7, col8, col9 = st.columns([1,1,1,1,1])

col5.plotly_chart(fig4, use_container_width=True)
col6.plotly_chart(fig5, use_container_width=True)
col7.plotly_chart(fig6, use_container_width=True)
col8.plotly_chart(fig7, use_container_width=True)
col9.plotly_chart(fig8, use_container_width=True)

st.divider()


col10, col11, col12, col13 = st.columns([1,1,0.4,0.4])

col10.plotly_chart(fig14, use_container_width=True)
col11.plotly_chart(fig13, use_container_width=True)
col12.plotly_chart(fig11, use_container_width=True)
col13.plotly_chart(fig12, use_container_width=True)
