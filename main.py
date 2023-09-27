import streamlit as st
import pandas as pd
import numpy as np

import streamlit as st
import pandas as pd
from io import StringIO
from docx import Document
import io

import urllib
from collections import defaultdict

def getAdsSeries(text):
  ads = text[:text.rfind('-')]
  last = text[text.rfind('-')+1:]
  if last in ['视频', '轮播', '绿白黑视频']:
    text = ads
    ads = text[:text.rfind('-')]
    last = text[text.rfind('-')+1:]
  return ads, last

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)
    # st.write(dataframe)

    all_date = sorted(df['day'].unique())
    df = df[df['utm_campaign_content'].notna()]
    df['utm_campaign_content'] = df['utm_campaign_content'].apply(lambda x: urllib.parse.unquote(x))
    df = df[['utm_campaign_content', 'day', 'total_carts', 'total_checkouts', 'total_orders_placed']]
    df['ads'] = df['utm_campaign_content'].apply(lambda x: getAdsSeries(x)[0])
    df['series'] = df['utm_campaign_content'].apply(lambda x: getAdsSeries(x)[1])

    # remove untracked data
    df = df[df['ads'] != 'Facebook_U']
    df = df[df['ads'] != 'Shoppingpmax']
    df = df[df['ads'] != 'sag_organi']

    # get data with at least one type of activities
    df_focus = df.loc[~((df['total_carts'] == 0) & (df['total_checkouts'] == 0) & (df['total_orders_placed'] == 0))]

    ads_groups = df.groupby(['ads'])

    ads_dict = defaultdict(list)
    for ads in ads_groups.groups:
        ads_dict[ads] = ads_groups.get_group(ads)['series'].unique()

    document = Document()
    document.add_heading('数据', 0)

    for ads in ads_groups.groups:
        document.add_paragraph(f'{ads}, {len(ads_dict[ads])}个标签')
        tags = ', '.join(ads_dict[ads])
        document.add_paragraph(f'标签: {tags}')
        if ads in df_focus['ads'].unique():
            ads_focus = df_focus[df_focus['ads'] == ads]
            for date in all_date:
                if date in ads_focus['day'].unique():
                    date_focus = ads_focus[ads_focus['day'] == date]
                    value = []
                    for idx, row in date_focus.iterrows():
                        value.append(
                            f"{row['series']}-{row['total_carts']}-{row['total_checkouts']}-{row['total_orders_placed']}")

                    document.add_paragraph(f"{date}: {', '.join(value)}")
        document.add_paragraph()

    file_stream = io.BytesIO()
    document.save(file_stream)
    st.download_button('下载', file_stream,file_name='data.docx')
