# ── Palavras-chave de ÁREA DE SAÚDE (pelo menos 1 obrigatória para qualificar)
HEALTH_KEYWORDS = [
    # PT
    "epidemiologia", "saúde pública", "saúde coletiva", "saúde publica",
    "saude publica", "saude coletiva", "nutrição", "nutricao", "nutricionista",
    "políticas de saúde", "politicas de saude", "vigilância em saúde",
    "vigilancia em saude", "avaliação nutricional", "dados em saúde",
    "dados em saude", "big data saúde", "coorte", "inquérito nutricional",
    "saúde infantil", "saude infantil", "mortalidade infantil",
    "doenças crônicas", "doencas cronicas", "obesidade", "desnutrição",
    "segurança alimentar", "seguranca alimentar", "sus", "atenção primária",
    "atencao primaria", "saúde mental", "saude mental",
    # EN
    "public health", "epidemiology", "nutrition", "nutritionist",
    "health data", "health policy", "population health", "global health",
    "health informatics", "clinical data", "health analytics",
    "maternal health", "child health", "chronic disease", "biostatistics",
    "health system",
]

# ── Palavras-chave de MÉTODO/DADOS (reforçam relevância mas não bastam sozinhas)
DATA_KEYWORDS = [
    "machine learning", "aprendizado de máquina", "inteligência artificial",
    "ia em saúde", "ciência de dados", "data science", "análise de dados",
    "bioestatística", "modelagem estatística", "r estatístico",
    "python saúde", "artificial intelligence", "health analytics",
]

# ── Palavras-chave de CARGO ACADÊMICO (reforçam mas não bastam sozinhas)
ROLE_KEYWORDS = [
    "professor", "professora", "pesquisador", "pesquisadora",
    "docente", "researcher", "lecturer", "faculty",
]

# Todos juntos para scoring geral
ALL_KEYWORDS = list(set(HEALTH_KEYWORDS + DATA_KEYWORDS + ROLE_KEYWORDS))

# Palavras-chave usadas nas buscas do Gupy
GUPY_KEYWORDS = [
    "epidemiologia", "saúde pública", "saude publica",
    "nutrição", "nutricionista", "políticas de saúde",
    "dados em saúde", "saúde coletiva", "bioestatística",
    "machine learning", "inteligência artificial", "ciência de dados",
    "data science", "health data", "epidemiology", "public health",
    "pesquisador saude", "professor saude",
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

GUPY_PRIORITY_SLUGS = ["itausocial", "leman", "impulsogovbr", "einstein", "ieps"]

SCORE_THRESHOLD = 1          # mínimo de pontos totais
MAX_JOB_AGE_DAYS = 365       # ignorar vagas sem deadline mais antigas que isso
PRIORITY_SCORE_BOOST = 5     # boost para empresas prioritárias
MAX_JOBS_PER_RUN = 15        # máximo de vagas por envio Discord
