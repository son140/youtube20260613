import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
import requests
import os
from urllib.parse import urlparse, parse_qs

st.set_page_config(
page_title="YouTube Comment Analyzer",
layout="wide"
)

st.markdown("""

<style>

.stApp{
background:#fafafa;
}

.block{
background:white;
padding:24px;
border-radius:18px;
box-shadow:0 6px 24px rgba(0,0,0,.08);
}

</style>

""", unsafe_allow_html=True)

st.markdown("""

<div class="block">

# YouTube Comment Analyzer

유튜브 링크만 넣으면 댓글을 분석합니다.

</div>

""", unsafe_allow_html=True)

api_key = st.text_input(
"YouTube API Key",
type="password"
)

url = st.text_input(
"YouTube URL"
)

FONT = "NotoSansKR.ttf"

if not os.path.exists(FONT):

```
font_url = (
    "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Regular.ttf"
)

r = requests.get(font_url)

with open(
    FONT,
    "wb"
) as f:

    f.write(r.content)
```

def get_video_id(link):

```
if "youtu.be/" in link:

    return (
        link
        .split("youtu.be/")[1]
        .split("?")[0]
    )

parsed = urlparse(link)

q = parse_qs(
    parsed.query
)

if "v" in q:

    return q["v"][0]

return None
```

def get_comments(youtube, video):

```
comments = []

req = (
    youtube
    .commentThreads()
    .list(
        part="snippet",
        videoId=video,
        maxResults=100,
        textFormat="plainText"
    )
)

while req:

    res = req.execute()

    for item in res["items"]:

        txt = (
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

        comments.append(
            txt
        )

    req = (
        youtube
        .commentThreads()
        .list_next(
            req,
            res
        )
    )

return comments
```

def clean(text):

```
return re.sub(
    r"[^\w가-힣 ]",
    "",
    text
)
```

if st.button(
"분석 시작",
use_container_width=True
):

```
try:

    if not api_key:

        st.error(
            "API Key 입력"
        )

        st.stop()

    video = get_video_id(
        url
    )

    if video is None:

        st.error(
            "유효한 유튜브 링크"
        )

        st.stop()

    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key
    )

    comments = get_comments(
        youtube,
        video
    )

    if len(comments) == 0:

        st.warning(
            "댓글 없음"
        )

        st.stop()

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

        font_path=FONT,

        width=1800,

        height=900,

        background_color="white"

    ).generate(
        text
    )

    fig, ax = plt.subplots(
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

    words = (
        Counter(
            text.split()
        )
        .most_common(
            20
        )
    )

    st.subheader(
        "키워드"
    )

    st.dataframe(
        pd.DataFrame(
            words,
            columns=[
                "단어",
                "횟수"
            ]
        )
    )

    st.subheader(
        "대표 댓글"
    )

    for c in comments[:10]:

        st.write(
            "•",
            c
        )

except Exception as e:

    st.error(
        str(e)
    )
```
