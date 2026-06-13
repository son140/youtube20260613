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
st.caption("유튜브 링크 → 댓글 → 워드클라우드")

api_key = st.text_input(
    "YouTube API Key",
    type="password"
)

video_url = st.text_input(
    "YouTube URL"
)


def extract_video_id(url):

    if not url:
        return None

    if "youtu.be/" in url:

        return (
            url
            .split("youtu.be/")[1]
            .split("?")[0]
        )

    parsed = urlparse(url)

    query = parse_qs(
        parsed.query
    )

    return query.get(
        "v",
        [None]
    )[0]


def fetch_comments(youtube, video_id):

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    while request:

        response = request.execute()

        for item in response.get(
            "items",
            []
        ):

            comments.append(
                item["snippet"]
                ["topLevelComment"]
                ["snippet"]
                ["textDisplay"]
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


def clean(text):

    return re.sub(
        r"[^\w가-힣 ]",
        "",
        text
    )


if st.button("Analyze"):

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
                "올바른 유튜브 링크 입력"
            )

            st.stop()

        youtube = build(
            "youtube",
            "v3",
            developerKey=api_key
        )

        comments = fetch_comments(
            youtube,
            video_id
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
                for i in comments
            ]
        )

        try:

            wc = WordCloud(
                width=1600,
                height=800,
                background_color="white"
            ).generate(text)

            fig, ax = plt.subplots()

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

        except:

            st.warning(
                "워드클라우드 생성 실패"
            )

        keywords = (
            Counter(
                text.split()
            )
            .most_common(
                20
            )
        )

        st.subheader(
            "Top Keywords"
        )

        st.dataframe(
            pd.DataFrame(
                keywords,
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
