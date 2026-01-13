# keywords.py

# SI un de ces mots est dans le titre -> POUBELLE (Note = 0)
BLACKLIST = [
    "Back Office", "Middle Office", "Operations", "Settlement", "Clearing", 
    "Admin", "Assistant", "Office Manager", "Secrétariat",
    "Risk", "Risque", "Compliance", "Conformité", "KYC", "AML", "Audit", "Control", 
    "Legal", "Juridique", "Comptabilité", "Accounting", "Consolidation", "Tax",
    "Developer", "Développeur", "Software", "Helpdesk", "Support IT", "Full Stack"
]

# SI un de ces mots est dans le titre -> BONUS DE NOTE (+2 points)
GOLDLIST_JOBS = [
    "Sales", "Distribution", "Wholesale", "Institutionnel", "Institutional", 
    "Retail", "Business Development", "Investor Relations", "RFP",
    "Product Specialist", "Investment Specialist", "Client Portfolio Manager", "CPM",
    "Portfolio Management", "Gestion", "Investment", "Asset Management", 
    "Allocation", "Selection", "Fund", "Equity", "Fixed Income", "Credit", 
    "Private Equity", "Real Estate", "Analyste Financier"
]

# Mots clés pour la date (Bonus +1 point)
DATE_KEYWORDS = [
    "Mai", "May", "Juin", "June", "Avril", "April", 
    "05/2026", "06/2026", "04/2026", "Printemps", "Spring"
]

# Lieux cibles
LOCATIONS = [
    "Paris", "London", "Londres", "Bruxelles", "Brussels", 
    "Geneva", "Genève", "Zurich", "Luxembourg", "Dubai", "Monaco"
]
