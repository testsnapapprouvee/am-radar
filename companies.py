# companies.py

# Liste des entreprises cibles pour le Scoring (+3 points)
# On utilise des racines de noms pour capturer les variantes (ex: "Lazard" capture "Lazard Frères Gestion")

TARGET_COMPANIES = [
    # --- SWISS & PRIVATE BANKING (Geneva, Zurich, Monaco, Lux) ---
    "Reyl", "Mirabaud", "Safra Sarasin", "EFG", "Vontobel", "Bordier", 
    "UBP", "Union Bancaire Privée", "Lombard Odier", "Pictet", "Julius Baer", 
    "Syz", "Notz Stucki", "NS Partners", "Edmond de Rothschild", "Indosuez", 
    "CFM Indosuez", "Société Générale Private Banking", "Barclays Private Bank",

    # --- QUANTS & HEDGE FUNDS (London, Paris, US) ---
    "AQR", "Man Group", "Bridgewater", "Two Sigma", "Marshall Wace", 
    "Brevan Howard", "Millennium", "Citadel", "Point72", "BlueCrest", 
    "Capital Fund Management", "CFM", "TCI", "Rokos",

    # --- TOP ASSET MANAGERS & BANKS (Global) ---
    "Amundi", "BlackRock", "J.P. Morgan", "JP Morgan", "Goldman Sachs", 
    "Morgan Stanley", "AXA IM", "BNP Paribas", "Natixis", "Allianz", 
    "HSBC", "Candriam", "Generali", "Schroders", "Fidelity", "PIMCO", 
    "Invesco", "State Street", "Vanguard", "Wellington", "Lazard", 
    "T. Rowe Price", "Capital Group", "Franklin Templeton", "M&G", 
    "Legal & General", "Abrdn", "Columbia Threadneedle", "Janus Henderson",
    "Neuberger Berman", "AllianceBernstein",

    # --- BOUTIQUES & FRENCH SPECIALISTS ---
    "Rothschild", "Tikehau", "Carmignac", "Financière de l'Echiquier", "LFDE", 
    "DNCA", "Sycomore", "Moneta", "Comgest", "Tocqueville", "Richelieu", 
    "Mandarine", "Dorval", "OFI", "Groupama", "La Française", "Sanso", 
    "Gemway", "Varenne", "Oddo BHF",

    # --- PRIVATE EQUITY / REAL ASSETS ---
    "Blackstone", "KKR", "Carlyle", "Ardian", "Macquarie", "Partners Group"
]
