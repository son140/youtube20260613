import streamlit as st
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import requests
import os
import re

st.set_page_config(
page_title="YouTube Comment Analyzer",
layout="wide"
)

st.title("YouTube Comment Analyzer")
st.caption("댓글 분석 · 키워드 · 워드클라우드")

api_key = st.text_input(
"YouTube API Key",
type="password"
)

video_url = st.text_input(
"YouTube URL"
)

FONT_PATH = "NotoSansKR.ttf"

def prepare_font():

```
if os.path.exists(FONT_PATH):
    return

url = (
    "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR-Regular.ttf"
)

r = requests.get(
    url,
    timeout=20
)

with open(
    FONT_PATH,
    "wb"
) as f:

    f.write(
        r.content
    )
```

def extract_video_id(url):

```
if "youtu.be/" in url:

    return (
        url
        .split("youtu.be/")[1]
        .split("?")[0]
    )

parsed = urlparse(
    url
)

q = parse_qs(
    parsed.query
)

if "v" in q:

    return q["v"][0]

return None
```

def get_comments(youtube, video_id):

```
comments = []

request = (
    youtube
    .commentThreads()
    .list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
)

while request:

    response = request.execute()

    items = response.get(
        "items",
        []
    )

    for item in items:

        text = (
            item
            ["snippet"]
            ["topLevelComment"]
            ["snippet"]
            ["textDisplay"]
        )

        comments.append(
            text
        )

    request = (
        youtube
        .commentThreads()
        .list_next(
            request,
            response
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

    if api_key == "":

        st.error(
            "API Key 입력"
        )

        st.stop()

    video_id = extract_video_id(
        video_url
    )

    if video_id is None:

        st.error(
            "유효한 유튜브 링크 입력"
        )

        st.stop()

    prepare_font()

    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key
    )

    comments = get_comments(
        youtube,
        video_id
    )

    if len(comments) == 0:

        st.warning(
            "댓글을 찾지 못함"
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
        width=1800,
        height=900,
        background_color="white",
        font_path=FONT_PATH
    ).generate(
        text
    )

    fig, ax = plt.subplots(
        figsize=(14, 8)
    )

    ax.imshow(
        wc
    )

    ax.axis(
        "off"
    )

    st.subheader(
        "Word Cloud"
    )

    st.pyplot(
        fig
    )

    top = (
        Counter(
            text.split()
        )
        .most_common(20)
    )

    st.subheader(
        "Top Keywords"
    )

    st.dataframe(
        pd.DataFrame(
            top,
            columns=[
                "Word",
                "Count"
            ]
        ),
        use_container_width=True
    )

    st.subheader(
        "Representative Comments"
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
