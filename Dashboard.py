import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout ='wide')

def formata_numero(valor, prefixo= ''):
    for unidade in ['', 'mil']:
        if valor<1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value= True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}

response = requests.get(url, params= query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] =pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


##Tabelas
#aba1 - Tabelas de receitas
    
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index= True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values(['Preço'], ascending = False)

#aba2 - Tabelas de quantidade de vendas
qtd_estados = dados.groupby('Local da compra')[['Preço']].count()
qtd_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(qtd_estados, left_on='Local da compra', right_index= True).sort_values('Preço', ascending = False)

qtd_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].count().reset_index()
qtd_mensal['Ano'] = qtd_mensal['Data da Compra'].dt.year
qtd_mensal['Mes'] = qtd_mensal['Data da Compra'].dt.month_name()

qtd_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values(['Preço'], ascending = False)

#aba3 - Tabelas vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


##Graficos
#aba1
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template= 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False},
                                  title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y = (0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto= True,
                                title= 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

#aba2
fig_mapa_qtd = px.scatter_geo(qtd_estados,
                              lat = 'lat',
                              lon = 'lon',
                              scope= 'south america',
                              size = 'Preço',
                              template= 'seaborn',
                              hover_name= 'Local da compra',
                              hover_data= {'lat': False, 'lon': False},
                              title= 'Quantidade de vendas por estado')

fig_qtd_mensal = px.line(qtd_mensal,
                         x = 'Mes',
                         y = 'Preço',
                         markers = True,
                         range_y= (0, qtd_mensal.max()),
                         color = 'Ano',
                         line_dash= 'Ano',
                         title= 'Quantidade mensal')
fig_qtd_mensal.update_layout(yaxis_title = 'Quantidade')

fig_qtd_estados = px.bar(qtd_estados.head(),
                         x = 'Local da compra',
                         y = 'Preço',
                         text_auto = True,
                         title = 'Top estados (quantidade)')
fig_qtd_mensal.update_layout(yaxis_title = 'Quantidade')

fig_qtd_categorias = px.bar(qtd_categorias,
                                text_auto= True,
                                title= 'Quantidade por categoria')
fig_qtd_categorias.update_layout(yaxis_title = 'Quantidade')


## Visualização no Streamlit
coluna3 = st.columns(1)
with coluna3:
    coluna4, coluna5 = st.columns(5)
    with coluna4:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    with coluna5:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), use_)
        

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1,coluna2 = st.columns(2)
    with coluna1:        
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)

    with coluna2:        
        st.plotly_chart(fig_receita_mensal, use_container_width= True)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)


with aba2:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_qtd,use_container_width= True)
        st.plotly_chart(fig_qtd_estados, use_container_width= True)
       

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_mensal, use_container_width= True)
        st.plotly_chart(fig_qtd_categorias, use_container_width= True)
       
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width= True)
        
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (Quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)
