import streamlit as st
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import re
from collections import Counter
from urllib.parse import urlparse, parse_qs

st.set_page_config(
    page_title="YouTube Comment Intelligence",
    page_icon="▶",
    layout="wide"
)

st.markdown("""
<style>

.stApp{
background:
linear-gradient(
180deg,
#0f1117,
#171923
);
color:white;
}

.block{
background:#181b25;
padding:28px;
border-radius:22px;
}

.title{
font-size:42px;
font-weight:800;
}

.small{
color:#b7bccd;
}

</style>
""",
unsafe_allow_html=True)

API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


def get_video_id(url):

    if "youtu.be/" in url:
        return url.split("/")[-1]

    parsed = urlparse(url)

    if "v" in parse_qs(parsed.query):
        return parse_qs(parsed.query)["v"][0]

    return None


def fetch_comments(video_id):

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    while request:

        response = request.execute()

        for item in response["items"]:

            text = (
                item["snippet"]
                ["topLevelComment"]
                ["snippet"]
                ["textDisplay"]
            )

            comments.append(text)

        request = (
            youtube.commentThreads()
            .list_next(
                request,
                response
            )
        )

    return comments


def fetch_video(video_id):

    res = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()

    return res["items"][0]


def clean(text):

    text = re.sub(
        r"[^\w가-힣 ]",
        "",
        text
    )

    return text


def sentiment(comment):

    pos = [
        "좋",
        "최고",
        "재밌",
        "감동",
        "행복"
    ]

    neg = [
        "별로",
        "싫",
        "최악",
        "실망"
    ]

    score = 0

    for p in pos:
        if p in comment:
            score += 1

    for n in neg:
        if n in comment:
            score -= 1

    if score > 0:
        return "Positive"

    if score < 0:
        return "Negative"

    return "Neutral"


st.markdown("""
<div class="block">

<div class="title">
YouTube Comment Intelligence
</div>

<div class="small">
Deep analysis of audience reactions
</div>

</div>
""",
unsafe_allow_html=True)

url = st.text_input(
    "YouTube URL"
)

if st.button(
    "Analyze",
    use_container_width=True
):

    try:

        video_id = get_video_id(url)

        info = fetch_video(video_id)

        comments = fetch_comments(video_id)

        title = (
            info["snippet"]
            ["title"]
        )

        views = (
            info["statistics"]
            ["viewCount"]
        )

        st.subheader(title)

        st.write(
            f"Views: {views}"
        )

        df = pd.DataFrame(
            {
                "comment": comments
            }
        )

        df["sentiment"] = (
            df["comment"]
            .apply(
                sentiment
            )
        )

        c1,c2,c3 = st.columns(3)

        with c1:
            st.metric(
                "Comments",
                len(df)
            )

        with c2:
            st.metric(
                "Positive",
                (
                    df["sentiment"]
                    ==
                    "Positive"
                ).sum()
            )

        with c3:
            st.metric(
                "Negative",
                (
                    df["sentiment"]
                    ==
                    "Negative"
                ).sum()
            )

        st.markdown(
            "## Word Cloud"
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

            font_path="fonts/NanumGothic.ttf"

        ).generate(text)

        fig, ax = plt.subplots(
            figsize=(14,8)
        )

        ax.imshow(
            wc,
            interpolation="bilinear"
        )

        ax.axis("off")

        st.pyplot(fig)

        st.markdown(
            "## Frequent Keywords"
        )

        words = text.split()

        top = (
            Counter(words)
            .most_common(20)
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

        st.markdown(
            "## Representative Comments"
        )

        for c in comments[:10]:

            st.info(c)

    except Exception as e:

        st.error(str(e))
