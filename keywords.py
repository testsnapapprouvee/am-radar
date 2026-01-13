# keywords.py

# Si un de ces mots est dans le titre = REJET IMMÉDIAT
BLACKLIST = [
    "Alternance", "Apprenticeship", "Alternant", # Tu cherches un stage
    "CDI", "CDD", "Permanent", "Fixed Term",
    "Back-Office", "Comptabilité", "Accounting", "Middle-Office",
    "Legal", "Juridique", "Compliance", "Conformité", "Audit",
    "IT Support", "Helpdesk", "Developper", "Software Engineer",
    "HR", "Ressources Humaines", "Marketing", "Communication",
    "Operations", "Admin", "Assistant de direction", "Secretary",
    "Receptionist", "Maintenance", "Logistics", "Supply Chain",
    "Retail", "Vendeur", "Conseiller Clientèle" # Banque de détail
]

# Si un de ces mots est dans le titre = BONUS (+2 points)
# C'est ici qu'on met Sales, Advisory, Investment, etc.
GOLDLIST_JOBS = [
    "Asset Management", "Gestion d'actifs",
    "Sales", "Vente", "Business Development", "Distribution",
    "Investment", "Investissement", "Investor",
    "Portfolio", "Gestion de portefeuille",
    "Advisory", "Conseil", "Advisor",
    "Analyst", "Analyste", "Analysis",
    "Equity", "Actions", "Fixed Income", "Obligataire", "Credit",
    "Private Equity", "Dette Privée", "Real Estate",
    "Wealth Management", "Gestion de Fortune", "Private Banking", "Banque Privée",
    "Fund", "Fonds", "ESG", "Sustainable",
    "M&A", "Fusion Acquisition", "Valuation",
    "Product Specialist", "Spécialiste Produit",
    "Structured Products", "Produits Structurés"
]

# Si un de ces mots est dans la description = BONUS (+1 point)
DATE_KEYWORDS = [
    "Mai", "May",
    "Juin", "June",
    "Juillet", "July",
    "2026", "2025"
]

# Liste des villes cibles (Filtre souple)
LOCATIONS = [
    "Paris", "France",
    "Luxembourg",
    "Geneva", "Genève",
    "Zurich", "Zürich",
    "London", "Londres",
    "Monaco",
    "Dubai", "Dubaï",
    "Singapore", "Singapour",
]
