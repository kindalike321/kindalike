import pandas as pd
import streamlit as st

# ===============================
# 1. 챔피언 데이터
# ===============================
my_champions = {
    "AD": [
        "암베사", "자헨", "우르곳", "일라오이", "레넥톤",
        "가렌", "자르반", "올라프", "세트", "잭스",
        "문도", "다리우스", "판테온"
    ],
    "AP": [
        "라이즈", "케넨", "바루스", "스웨인", "그웬",
        "신지드", "에코", "티모", "오로라", "워윅",
        "모데카이저", "말파이트"
    ]
}

enemy_champions = [   
    "가렌", "갱플랭크", "그라가스", "그웬",
    "나르", "나서스", "녹턴",
    "다리우스",
    "라이즈", "럼블", "레넥톤", "렝가", "룰루", "리븐", "리신",
    "마오카이", "말파이트", "모데카이저", "문도",
    "바루스", "베인", "볼리베어", "블라디미르", "비에고", "뽀삐",
    "사이온", "사일러스", "세주아니", "세트", "쉔", "스웨인", "스카너", "신지드", "신짜오", "스몰더",
    "아칼리", "아크샨", "아트록스", "암베사", "야스오", "오공", "오로라", "오른", "올라프", "요네",
    "요릭", "우디르", "우르곳", "워윅", "이렐리아", "일라오이",
    "자크", "자헨", "잭스", "제드", "제이스",
    "초가스",
    "카르마", "카밀", "카시오페아", "카이사", "케넨", "케일", "퀸", "크산테", "클레드", 
    "탐켄치", "트런들", "트린다미어", "티모",
    "판테온", "피들스틱", "피오라",
    "하이머딩거"
]

# ===============================
# 2. 점수와 선호도
# ===============================
preference = {  # 챔피언별 선호도
    "암베사": 1.5, "자헨": 1.2, "우르곳": 0.6, "일라오이": 1.3, "레넥톤": 1.0,
    "가렌": 1.3, "자르반": 1.2, "올라프": 1.1, "세트": 1.3, "잭스": 0.9,
    "문도": 1.0, "다리우스": 1.2, "판테온": 1.1,
    "라이즈": 1.3, "케넨": 1.0, "바루스": 0.8, "스웨인": 0.8, "그웬": 1.5,
    "신지드": 1.0, "에코": 0.9, "티모": 1.2, "오로라": 1.0, "워윅": 0.9,
    "모데카이저": 1.2, "말파이트": 1.0
}

score_desc = {
    -100: "본인과의 매치업이라 어차피 못뽑음.",
    -1: "불리. 절대 뽑으면 안됨.",
     0: "라인전 반반, 후반밸류 더 좋음",
     1: "라인전 좋음",
     2: "라인전, 한타, 후반까지 압살"
}

# ===============================
# 3. 데이터 로드
# ===============================
@st.cache_data(ttl=0)
def load_data():
    try:
        return pd.read_csv("banData.csv", encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv("banData.csv", encoding="cp949")

df = load_data()
df.set_index(df.columns[0], inplace=True)
df = df.apply(pd.to_numeric, errors="coerce")  # 숫자로 강제 변환

# ===============================
# 4. 초성 처리
# ===============================
CHOSUNG_LIST = [
    "ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ",
    "ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"
]

def get_chosung(word):
    result = ""
    for char in word:
        if "가" <= char <= "힣":
            code = ord(char) - ord("가")
            result += CHOSUNG_LIST[code // 588]
        else:
            result += char
    return result

def resolve_input(user_input, all_champions):
    user_input = user_input.strip()
    if user_input in all_champions:
        return user_input
    for champ in all_champions:
        if get_chosung(champ) == user_input:
            return champ
    return None

all_enemies = set(df.index.tolist())

# ===============================
# 5. 점수 → 별 변환
# ===============================
def score_to_stars(score, max_stars=2.4):
    stars = round(score / 2 * max_stars)
    stars = max(0, stars)
    return "★" * stars

def colorize(champ):
    for t in my_champions:
        if champ in my_champions[t]:
            if t == "AD":
                # 연한 빨강 + 배경색/패딩 적용
                return f"<span style='color:white; background-color:#ff7f7f; padding:2px 5px; border-radius:4px; font-weight:bold'>{champ}</span>"
            else:  # AP
                # 연한 파랑 + 배경색/패딩 적용
                return f"<span style='color:white; background-color:#1f77b4; padding:2px 5px; border-radius:4px'>{champ}</span>"
    return champ


# ===============================
# 6. 추천 로직
# ===============================
def single_counter(enemy, top_n=5):
    row = df.loc[enemy].dropna()
    row = row[row > 0]
    # 선호도 반영
    row = row * row.index.map(lambda x: preference.get(x,1.0))
    return row.sort_values(ascending=False).head(top_n)

def common_counter(enemies, top_n=5):
    sub = df.loc[enemies]
    valid = sub.dropna(axis=1, how="any")
    valid = valid.loc[:, (valid > 0).all()]
    scores = valid.sum()
    scores = scores * scores.index.map(lambda x: preference.get(x,1.0))
    return scores.sort_values(ascending=False).head(top_n)

# ===============================
# 7. Streamlit UI
# ===============================
st.title("탑 후픽 추천받아요")

enemy_input = st.text_input(
    "상대 챔피언 입력 (공백으로 구분, 초성도 가능)",
    value="",  # 초기값 항상 빈 문자열
    placeholder="예: 가렌 다리우스 ㄹㄴㅌ"
)

if enemy_input:
    raw_inputs = [x.strip() for x in enemy_input.split() if x.strip()]
    enemies = []

    for r in raw_inputs:
        resolved = resolve_input(r, all_enemies)
        if resolved:
            enemies.append(resolved)
        elif (r == "ㄴㅁㅎ" or r == "노무현" or r == "운지"):
            st.warning(f"잉지는 진솔이를 사랑해!")
        else:
            st.warning(f"'{r}' 는 제대로 된 이름이 아니에요  ;ㅅ;  ")

    if enemies:
        st.divider()
        # 단일 카운터
        st.subheader("챔프별 카운터 추천")
        for e in enemies:
            st.markdown("<div style='font-size:1.7em; font-weight:bold'>" +
                        f"{e} <span style='font-size:0.6em; color:gray'>에게는요...</span></div>",
                        unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:0.3px'></div>", unsafe_allow_html=True)
            res = single_counter(e)
            if res.empty:
                st.write("추천 없음")
            else:
                for champ, val in res.items():
                    stars = score_to_stars(val)
                    colored = colorize(champ)
                    # 이름과 별 사이 공백 3칸
                    st.markdown(f"{colored}&nbsp;&nbsp;&nbsp;{stars}", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom:7px'></div>", unsafe_allow_html=True)

        # 공통 카운터
        if len(enemies) > 1:
            st.divider()
            st.subheader("공통 카운터 추천")
            common = common_counter(enemies)
            if common.empty:
                st.write("추천 없음")
            else:
                for champ, val in common.items():
                    stars = score_to_stars(val)
                    colored = colorize(champ)
                    st.markdown(f"{colored}&nbsp;&nbsp;&nbsp;{stars}", unsafe_allow_html=True)


# ===============================
# streamlit run "C:/Users/kinda/OneDrive/바탕 화면/배네핏/ban.py"
# ===============================

