from nltk.corpus import stopwords

# Tanmay Juneja
NAME_PATTERN = [{"POS": "PROPN"}, {"POS": "PROPN"}]

NOT_ALPHA_NUMERIC = r"[^a-zA-Z\d]"

NUMBER = r"\d+"

# For finding date ranges
MONTHS_SHORT = (
    r"(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)"
)
MONTHS_LONG = r"(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)"
MONTH = r"(" + MONTHS_SHORT + r"|" + MONTHS_LONG + r")"
YEAR = r"(((20|19)(\d{2})))"

STOPWORDS = set(stopwords.words("english"))
