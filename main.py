import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from urllib.parse import urlparse, parse_qs
import requests
import os

st.set_page_config(
    page_title="YouTube Comment Analyzer",
    layout="wide"
)

st.markdown("""
<style>

.stApp{
background:
linear-gradient(
180deg,
#fafafa,
#ffffff
);
}

.box{
background:white;
padding:28px;
border-radius:18px;
box-shadow:0 6px 24px rgba(0,0,0,.08);
}

</style>
""",
unsafe_allow_html=True)

st.markdown("""
<div class='box'>

# YouTube Comment Analyzer

댓글 기반 키워드 분석

</div>
""",
unsafe_allow_html=True)

API_KEY = st.text_input(
"YouTube API Key",
type="password"
)

url = st.text_input(
"유튜브 링크 입력"
)

FONT_URL = (
"https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Regular.ttf"
)

FONT_FILE = "NotoSansKR.ttf"

if not os.path.exists(FONT_FILE):

    r = requests.get(FONT_URL)

    with open(
        FONT_FILE,
        "wb"
    ) as f:

        f.write(
            r.content
        )


def get_id(link):

    if "youtu.be/" in link:

        return (
            link
            .split("/")
            [-1]
        )

    parsed = urlparse(
        link
    )

    return (
        parse_qs(
            parsed.query
        )
        .get(
            "v",
            [None]
        )[0]
    )


def fetch(youtube, vid):

    comments=[]

    request=(
        youtube
        .commentThreads()
        .list(

part="snippet",

videoId=vid,

maxResults=100,

textFormat="plainText"

)
)

    while request:

        response=request.execute()

        for item in response["items"]:

            comments.append(

item[
"snippet"
][
"topLevelComment"
][
"snippet"
][
"textDisplay"
]

)

        request=(
            youtube
            .commentThreads()
            .list_next(
                request,
                response
            )
        )

    return comments


def clean(text):

    return re.sub(
        r"[^\w가-힣 ]",
        "",
        text
    )


if st.button(
"분석 시작",
use_container_width=True
):

    try:

        youtube = build(
            "youtube",
            "v3",
            developerKey=API_KEY
        )

        video = get_id(
            url
        )

        comments = fetch(
            youtube,
            video
        )

        st.metric(
            "댓글 수",
            len(comments)
        )

        text = " ".join(
            [
                clean(i)
                for i
                in comments
            ]
        )

        wc = WordCloud(

font_path=FONT_FILE,

width=1800,

height=900,

background_color="white"

).generate(
text
)

        fig,ax=plt.subplots(
            figsize=(14,8)
        )

        ax.imshow(
            wc
        )

        ax.axis(
            "off"
        )

        st.subheader(
            "워드클라우드"
        )

        st.pyplot(
            fig
        )

        words=(
            Counter(
                text.split()
            )
            .most_common(
                20
            )
        )

        st.subheader(
            "상위 키워드"
        )

        st.dataframe(

pd.DataFrame(
words,
columns=[
"단어",
"횟수"
]
),

use_container_width=True

)

        st.subheader(
            "대표 댓글"
        )

        for c in comments[:10]:

            st.info(
                c
            )

    except Exception as e:

        st.error(
            str(e)
        )
