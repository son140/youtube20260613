import streamlit as st
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import re

st.set_page_config(
page_title="YouTube Comment Analyzer",
layout="wide"
)

st.title("YouTube Comment Analyzer")

with st.sidebar:

```
st.header("설정")

API_KEY = st.text_input(
    "YouTube API Key",
    type="password"
)
```

video_url = st.text_input(
"유튜브 링크 입력"
)

def extract_video_id(url):

```
if not url:
    return None

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

return q.get(
    "v",
    [None]
)[0]
```

def clean(text):

```
return re.sub(
    r"[^\w가-힣 ]",
    "",
    text
)
```

def fetch_comments(video):

```
youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

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

    for item in res.get(
        "items",
        []
    ):

        comments.append(

            item
            ["snippet"]
            ["topLevelComment"]
            ["snippet"]
            ["textDisplay"]

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

if st.button(
"분석 시작",
use_container_width=True
):

```
try:

    if API_KEY == "":

        st.error(
            "왼쪽에서 API Key 입력"
        )

        st.stop()

    if not API_KEY.startswith(
        "AIza"
    ):

        st.error(
            "API Key 형식 오류"
        )

        st.stop()

    video = extract_video_id(
        video_url
    )

    if video is None:

        st.error(
            "유효한 링크 입력"
        )

        st.stop()

    comments = fetch_comments(
        video
    )

    if len(comments) == 0:

        st.warning(
            "댓글 없음"
        )

        st.stop()

    st.success(
        "분석 완료"
    )

    st.metric(
        "댓글 수",
        len(comments)
    )

    merged = " ".join(
        [
            clean(i)
            for i in comments
        ]
    )

    try:

        wc = WordCloud(
            width=1600,
            height=800,
            background_color="white"
        ).generate(
            merged
        )

        fig, ax = plt.subplots()

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

    except:

        st.info(
            "워드클라우드 생성 생략"
        )

    st.subheader(
        "키워드"
    )

    top = (
        Counter(
            merged.split()
        )
        .most_common(
            20
        )
    )

    st.dataframe(
        pd.DataFrame(
            top,
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

        st.write(
            "•",
            c
        )

except Exception as e:

    st.error(
        str(e)
    )
```
