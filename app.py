import io
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import streamlit as st
import pandas as pd
import numpy as np
import os
import pydeck as pdk
import io

st.set_page_config(page_title="Acha Buteco 2023", page_icon="🍺", layout="wide")
def main():
    df = pd.read_excel('dados_restaurantes.xlsx').sort_values('bairro')

    with st.sidebar:
        st.header('Busca por restaurantes')
        cidade = st.multiselect('Cidade', df['cidade'].unique(), default='Rio de Janeiro')
        regiao = st.multiselect('Região', sorted(df.query("cidade.isin(@cidade)")['regiao'].unique()), default=df.query("cidade.isin(@cidade)")['regiao'].unique())
        bairro = st.multiselect('Bairro', df.query("regiao == @regiao")['bairro'].unique())
        st.markdown('---')
        st.caption('O aplicativo não tem relação com a organização do evento. O objetivo é apenas facilitar a busca de restaurantes participantes. A marca "Comida di Buteco®" pertence aos seus atuais organizadores.')
        st.caption('Desenvolvido por Matheus C. Pestana <matheus.pestana@iesp.uerj.br>')

    st.title('Acha Buteco - 2023')
    st.subheader('Buscador de Butecos do Comida di Buteco® 2023')

    st.header('Restaurantes participantes')

    df_filtered = df.query("cidade.isin(@cidade) & regiao.isin(@regiao) & bairro.isin(@bairro)")

    mapa = pdk.Deck(map_style='light',
                    initial_view_state=pdk.ViewState(latitude=-22.909, longitude=-43.25, zoom=12.5, pitch=0),
                    layers=[
                        pdk.Layer(
                            'ScatterplotLayer',
                            data=df,
                            get_position='[longitude, latitude]',
                            get_color='[200, 30, 0, 160]',
                            get_radius=50,
                            auto_highlight=True,
                            pickable=True,
                        ),
                    ], height=1500, width=500,
                    tooltip={
        'html': '<b>Restaurante:</b> {restaurante}' + '<br>'
                + '<b>Endereço:</b> {endereco}' + '<br>'
                + '<b>Prato:</b> {nome_prato}' + '<br>'
                + '<b>Descrição:</b> {descricao_prato}',
        'style': {
            'color': 'white'
        }}
                    )
    st.pydeck_chart(mapa)

    st.header('Lista de Restaurantes')
    if not bairro:
        st.write('Utilize a busca no lado esquerdo para filtrar os restaurantes.')
    else:
        for i, row in df_filtered.iterrows():
            with st.expander(row['restaurante']):
                st.markdown(f"## Restaurante: {row['restaurante']}")
                st.markdown(f"### Endereço: {row['endereco']}")
                st.markdown(f"#### Prato: {row['nome_prato']}")
                st.markdown(f"##### {row['descricao_prato']}")
                st.markdown(f"###### Link original: {row['link']}")
                st.image(row['foto'], width=900)
                st.caption('Divulgação/Comida di Buteco® 2023')

    st.header('Tabela')
    if not bairro:
        st.write('Utilize a busca no lado esquerdo para filtrar os restaurantes.')
    else:
        st.dataframe(df_filtered.reset_index().drop(columns=('index')))

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_filtered.drop(columns=['latitude', 'longitude', 'foto']).to_excel(writer, sheet_name='Restaurantes Escolhidos', index=False)
            df.drop(columns=['latitude', 'longitude', 'foto']).to_excel(writer, sheet_name='Todos os Restaurantes', index=False)
            writer.save()
        buffer.seek(0)
        download = st.download_button(
            label="Download da tabela",
            data=buffer,
            file_name='Restaurantes.xlsx',
            mime='application/vnd.ms-excel'
        )

if __name__ == '__main__':
    main()
