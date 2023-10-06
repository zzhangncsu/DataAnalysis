import streamlit as st
import pandas as pd
import numpy as np

import streamlit as st
import pandas as pd
from io import StringIO
from docx import Document
import io
from docx.shared import RGBColor

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
    df = pd.read_csv(uploaded_file)

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

    tab1, tab2, tab3 = st.tabs(["文档", "统计", "图标"])
    with tab1:
        document = Document()
        document.add_heading('数据', 0)

        for ads in ads_groups.groups:
            if ads in df_focus['ads'].unique():
                document.add_paragraph(f'{ads}, {len(ads_dict[ads])}个标签')
                tags = ', '.join(ads_dict[ads])
                document.add_paragraph(f'标签: {tags}')
                ads_focus = df_focus[df_focus['ads'] == ads]
                for date in all_date:
                    if date in ads_focus['day'].unique():
                        date_focus = ads_focus[ads_focus['day'] == date]
                        value = []
                        date_focus = date_focus.sort_values(by=['total_orders_placed'], ascending=False)
                        p = document.add_paragraph()
                        p.add_run(f"{date}: ")
                        count = 0
                        for idx, row in date_focus.iterrows():
                            run = p.add_run(f"{row['series']}-{row['total_carts']}-{row['total_checkouts']}-{row['total_orders_placed']}")
                            if row['total_orders_placed'] > 0:
                                font = run.font
                                font.color.rgb = RGBColor(10, 150, 10)
                            if count != len(date_focus) - 1:
                                p.add_run(", ")
                            count += 1
                document.add_paragraph()

        document.add_paragraph("^(*￣(oo)￣)^")

        file_stream = io.BytesIO()
        document.save(file_stream)
        st.download_button('下载', file_stream, file_name='data.docx')

    with tab2:
        aggre_dict = defaultdict(defaultdict)
        for ads in ads_groups.groups:
            aggre_dict[ads]['total_carts'] = ads_groups.get_group(ads)['total_carts'].sum()
            aggre_dict[ads]['total_checkouts'] = ads_groups.get_group(ads)['total_checkouts'].sum()
            aggre_dict[ads]['total_orders_placed'] = ads_groups.get_group(ads)['total_orders_placed'].sum()
            aggre_dict[ads]['days'] = len(ads_groups.get_group(ads)['day'].unique())
            aggre_dict[ads]['tags'] = ads_groups.get_group(ads)['series'].unique()
        aggre_df = pd.DataFrame.from_dict(aggre_dict).T
        st.dataframe(aggre_df)

        option = st.selectbox(
            '广告系列',aggre_df.index)

        aggre_date_dict = defaultdict(lambda: defaultdict(dict))
        for ads in ads_groups.groups:
            ads_day_groups = ads_groups.get_group(ads).groupby('day')
            for day in ads_day_groups.groups:
                aggre_date_dict[ads][day]['total_carts'] = ads_day_groups.get_group(day)['total_carts'].sum()
                aggre_date_dict[ads][day]['total_checkouts'] = ads_day_groups.get_group(day)['total_checkouts'].sum()
                aggre_date_dict[ads][day]['total_orders_placed'] = ads_day_groups.get_group(day)[
                    'total_orders_placed'].sum()
        df_prod = pd.DataFrame.from_dict(aggre_date_dict[option]).T

        df_group_tag = ads_groups.get_group(option).groupby(['series']).sum(['total_carts', 'total_checkouts', 'total_orders_placed'])
        df_group_tag.index.names = ['Tags']
        st.dataframe(df_group_tag)
        st.dataframe(df_prod)
        #
        st.bar_chart(df_prod)
    with tab3:
        st.image("https://cdn.midjourney.com/1eea2b76-9e24-4a3f-ac81-ebdb7fd84389/0_2.png")
        st.image("https://cdn.midjourney.com/0eed04e8-49da-4b19-9701-460f7824371c/0_0.png")
        st.image("https://blog.lvhglobal.com/content/images/2018/10/hawaii-sunset-main.png")
        st.image("https://cdn.midjourney.com/608bee51-598d-48bb-a6ac-3276c41b0f7c/0_1.png")



