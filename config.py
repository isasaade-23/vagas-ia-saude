KEYWORDS_PT = [
    "machine learning", "aprendizado de máquina", "inteligência artificial",
    "ciência de dados", "ciência de dados em saúde", "análise de dados",
    "bioestatística", "epidemiologia", "saúde pública", "saúde coletiva",
    "nutrição", "nutricionista", "políticas de saúde", "pesquisador",
    "professor", "data science", "dados em saúde", "vigilância em saúde",
    "avaliação nutricional", "modelagem estatística", "r estatístico",
    "python saúde", "big data saúde", "coorte", "inquérito",
]

KEYWORDS_EN = [
    "machine learning", "artificial intelligence", "data science",
    "health data", "public health", "epidemiology", "biostatistics",
    "nutrition", "health policy", "researcher", "professor",
    "health informatics", "clinical data", "population health",
    "global health", "nutritionist", "health analytics",
]

ALL_KEYWORDS = list(set(KEYWORDS_PT + KEYWORDS_EN))

GUPY_KEYWORDS = [
    "machine learning", "inteligência artificial", "ciência de dados",
    "epidemiologia", "saúde pública", "nutrição", "políticas de saúde",
    "pesquisador", "professor", "dados em saúde", "bioestatística",
    "data science", "health", "epidemiology",
]

PRIORITY_COMPANIES = {
    "itaú social": "Itaú Social",
    "itau social": "Itaú Social",
    "impulso gov": "Impulso Gov",
    "impulso.work": "Impulso Gov",
    "fundação leman": "Fundação Leman",
    "fundacao leman": "Fundação Leman",
    "einstein": "Einstein",
    "albert einstein": "Einstein",
    "ieps": "IEPS",
    "instituto de estudos para políticas de saúde": "IEPS",
    "umane": "Umane",
    "fiocruz": "Fiocruz",
    "fundação oswaldo cruz": "Fiocruz",
    "pastoral da criança": "Pastoral da Criança",
    "pastoral da crianca": "Pastoral da Criança",
}

# Gupy company slugs (subdomain at {slug}.gupy.io)
GUPY_PRIORITY_SLUGS = [
    "einstein",
    "itausocial",
    "fiocruz",
]

CONCURSO_KEYWORDS = [
    "professor", "pesquisador", "docente", "epidemiologia",
    "saúde pública", "nutrição", "saúde coletiva",
]

SCORE_THRESHOLD = 1          # mínimo para aparecer
PRIORITY_SCORE_BOOST = 5     # boost para empresas prioritárias
MAX_JOBS_PER_RUN = 15        # máximo de vagas por envio Discord
