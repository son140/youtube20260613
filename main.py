import streamlit as st
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
from urllib.parse import urlparse, parse_qs
import re

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
#161a24
);
}

.card{
background:#171c28;
padding:28px;
border-radius:22px;
}

.big{
font-size:42px;
font-weight:800;
color:white;
}

.sub{
color:#aeb7c9;
}

</style>
""",
unsafe_allow_html=True)

st.markdown("""

<div class="card">

<div class="big">
YouTube Comment Intelligence
</div>

<div class="sub">
Deep Comment Analytics
</div>

</div>

""",
unsafe_allow_html=True)

api_key = st.text_input(
"YouTube API Key",
type="password"
)

url = st.text_input(
"YouTube URL"
)

def get_video_id(link):

    if "youtu.be/" in link:
        return link.split("/")[-1]

    parsed = urlparse(link)

    q = parse_qs(parsed.query)

    return q.get(
        "v",
        [None]
    )[0]


def clean(text):

    return re.sub(
        r"[^\w가-힣 ]",
        "",
        text
    )


def fetch(youtube, vid):

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=vid,
        maxResults=100,
        textFormat="plainText"
    )

    comments=[]

    while request:

        response=request.execute()

        for i in response["items"]:

            comments.append(

                i["snippet"]
                ["topLevelComment"]
                ["snippet"]
                ["textDisplay"]

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


if st.button(
"Analyze",
use_container_width=True
):

    try:

        youtube = build(
            "youtube",
            "v3",
            developerKey=api_key
        )

        video = get_video_id(url)

        comments = fetch(
            youtube,
            video
        )

        st.metric(
            "Comments",
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

            font_path=None,

            background_color="white"

        ).generate(text)

        fig,ax = plt.subplots(
            figsize=(14,8)
        )

        ax.imshow(wc)

        ax.axis(
            "off"
        )

        st.pyplot(fig)

        words = (
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
                words,
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

            st.info(c)

    except Exception as e:

        st.error(
            str(e)
        )
