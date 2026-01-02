import pandas as pd
import streamlit as st

my_champions = \
{
    "AD": 
    [
        "암베사", "자헨", "우르곳", "일라오이", "레넥톤",
        "가렌", "자르반", "올라프", "세트", "잭스",
        "문도", "다리우스", "판테온"
    ],

    "AP": 
    [
        "라이즈", "케넨", "바루스", "스웨인", "그웬",
        "신지드", "에코", "티모", "오로라", "워윅",
        "모데카이저", "말파이트"
    ]
}

enemy_champions = \
[   
    #ㄱ
    "가렌", "갱플랭크", "그라가스", "그웬",
    #ㄴ
    "나르", "나서스", "녹턴",
    #ㄷ
    "다리우스",
    #ㄹ
    "라이즈", "럼블", "레넥톤", "렝가", "룰루", "리븐", "리신",
    #ㅁ
    "마오카이", "말파이트", "모데카이저", "문도",
    #ㅂ
    "바루스", "베인", "볼리베어", "블라디미르", "비에고", "뽀삐",
    #ㅅ
    "사이온", "사일러스", "세주아니", "세트", "쉔", "스웨인", "스카너", "신지드", "신짜오", "스몰더",
    #ㅇ
    "아칼리", "아크샨", "아트록스", "암베사", "야스오", "오공", "오로라", "오른", "올라프", "요네",
    "요릭", "우디르", "우르곳", "워윅", "이렐리아", "일라오이",
    #ㅈ
    "자크", "자헨", "잭스", "제드", "제이스",
    #ㅊ
    "초가스",
    #ㅋ
    "카르마", "카밀", "카시오페아", "카이사", "케넨", "케일", "퀸", "크산테", "클레드", 
    #ㅌ
    "탐켄치", "트런들", "트린다미어", "티모",
    #ㅍ
    "판테온", "피들스틱", "피오라",
    #ㅎ
    "하이머딩거"
]

score = \
{
    -100: "본인과의 매치업이라 어차피 못뽑음.",
    -1: "불리. 절대 뽑으면 안됨.",
     0: "라인전 반반, 후반밸류 더 좋음",
     1: "라인전 좋음",
     2: "라인전, 한타, 후반까지 그냥 압살. 강추."
}

#///////////////////////////////////////////////////////////////////////////////////#

# ===============================
# 1. 데이터 로드
# ===============================
@st.cache_data
def load_data():
    try:
        return pd.read_csv("matchup.csv", encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv("matchup.csv", encoding="cp949")

df = load_data()
df.set_index(df.columns[0], inplace=True)  # 첫 열을 index로
df = df.apply(pd.to_numeric, errors="coerce")  # 숫자로 강제 변환

# ===============================
# 2. 초성 처리
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
    # 1. 완전 이름 일치
    if user_input in all_champions:
        return user_input
    # 2. 초성 입력
    for champ in all_champions:
        if get_chosung(champ) == user_input:
            return champ
    return None

all_enemies = set(df.index.tolist())

# ===============================
# 3. 추천 로직
# ===============================
def single_counter(enemy, top_n=5):
    row = df.loc[enemy].dropna()
    row = row[row > 0]  # 음수 제거
    return row.sort_values(ascending=False).head(top_n)

def common_counter(enemies, top_n=5):
    sub = df.loc[enemies]
    # NaN 또는 음수 하나라도 있는 열 제거
    valid = sub.dropna(axis=1, how="any")
    valid = valid.loc[:, (valid > 0).all()]
    scores = valid.sum()
    return scores.sort_values(ascending=False).head(top_n)

# ===============================
# 4. Streamlit UI
# ===============================
st.title("탑 챔피언 카운터 추천기")
enemy_input = st.text_input(
    "상대 챔피언 입력 (공백 구분, 초성 가능)",
    placeholder="예: 가렌 다리우스 ㄹㅇㅈ"
)

if enemy_input:
    raw_inputs = [x.strip() for x in enemy_input.split() if x.strip()]
    enemies = []

    for r in raw_inputs:
        resolved = resolve_input(r, all_enemies)
        if resolved:
            enemies.append(resolved)
        else:
            st.warning(f"'{r}' 는 인식할 수 없는 입력입니다.")

    if enemies:
        st.divider()

        # 단일 카운터 출력
        st.subheader("단일 카운터 추천")
        for e in enemies:
            st.markdown(f"### {e}")
            res = single_counter(e)
            if res.empty:
                st.write("추천 없음")
            else:
                for champ, val in res.items():
                    st.write(f"{champ} (점수: {val})")

        # 공통 카운터 출력
        if len(enemies) > 1:
            st.divider()
            st.subheader("공통 카운터 추천")
            common = common_counter(enemies)
            if common.empty:
                st.write("추천 없음")
            else:
                for champ, val in common.items():
                    st.write(f"{champ} (총합 점수: {val})")