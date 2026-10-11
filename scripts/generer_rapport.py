"""Genere le rapport PDF du TP4 : docs/RAPPORT_TP4.pdf

Usage : .venv/bin/python scripts/generer_rapport.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

SORTIE = Path(__file__).resolve().parent.parent / "docs" / "RAPPORT_TP4.pdf"

CONTRIBUTEURS = ["Deschant Kounou", "Ulrich Kpassi-Gobi"]
DEPOT = "https://github.com/deschantkn/tp4-federation-multi-sgbd"

BLEU = colors.HexColor("#1565C0")
BLEU_PALE = colors.HexColor("#E3F2FD")
GRIS = colors.HexColor("#555555")

styles = getSampleStyleSheet()
TITRE = ParagraphStyle("titre", parent=styles["Title"], fontSize=20,
                       leading=24, textColor=BLEU, spaceAfter=4)
SOUS_TITRE = ParagraphStyle("sous_titre", parent=styles["Normal"],
                            alignment=TA_CENTER, fontSize=11, textColor=GRIS)
H1 = ParagraphStyle("h1", parent=styles["Heading2"], textColor=BLEU,
                    spaceBefore=12, spaceAfter=6)
CORPS = ParagraphStyle("corps", parent=styles["BodyText"], fontSize=10,
                       leading=14, spaceAfter=6)
PUCE = ParagraphStyle("puce", parent=CORPS, leftIndent=14, bulletIndent=4,
                      spaceAfter=3)
CODE = ParagraphStyle("code", parent=CORPS, fontName="Courier", fontSize=8.5,
                      leading=11, backColor=colors.HexColor("#F5F5F5"),
                      borderPadding=6, spaceBefore=4, spaceAfter=10)
CELLULE = ParagraphStyle("cellule", parent=CORPS, fontSize=9, leading=11,
                         spaceAfter=0)


def tableau(lignes, largeurs, aligner_droite=()):
    """Tableau a en-tete bleu ; les cellules texte sont des Paragraph."""
    # seuls les textes longs sont des Paragraph (retour a la ligne) ; les
    # nombres restent des chaines pour pouvoir etre alignes a droite
    data = [[Paragraph(c, CELLULE) if i and isinstance(c, str) and len(c) > 18
             else c for c in ligne]
            for i, ligne in enumerate(lignes)]
    t = Table(data, colWidths=largeurs, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BLEU),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BLEU_PALE]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, BLEU),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for col in aligner_droite:
        style.append(("ALIGN", (col, 0), (col, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t


def puces(items):
    return [Paragraph(i, PUCE, bulletText="•") for i in items]


def pied_de_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(2 * cm, 1.2 * cm,
                      "TP 4 - Fédération de données multi-SGBD - "
                      + " & ".join(CONTRIBUTEURS))
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def construire():
    s = []

    # --- En-tete ---
    s.append(Paragraph("TP 4 - Fédération de données multi-SGBD avec PySpark",
                       TITRE))
    s.append(Paragraph("Big Data Engineering - UCAD / FST / DMI - "
                       "Prof. S. Ndiaye", SOUS_TITRE))
    s.append(Spacer(1, 10))
    s.append(tableau(
        [["Contributeurs", "Dépôt GitHub"],
         [" & ".join(CONTRIBUTEURS), f'<link href="{DEPOT}">{DEPOT}</link>']],
        [6 * cm, 11 * cm]))
    s.append(Spacer(1, 6))

    # --- 1. Contexte ---
    s.append(Paragraph("1. Contexte et objectif", H1))
    s.append(Paragraph(
        "Une plateforme e-commerce sénégalaise répartit ses données entre "
        "quatre équipes, chacune avec son propre SGBD, sans aucune clé "
        "étrangère entre les systèmes. La direction demande pourtant un "
        "chiffre d'affaires consolidé par ville, par catégorie de produit et "
        "par moyen de paiement. Aucun SGBD ne sait interroger les trois "
        "autres : <b>Spark</b>, avec quatre pilotes JDBC dans une seule JVM, "
        "joue le rôle de moteur de fédération.", CORPS))
    s.append(tableau(
        [["Équipe", "Table", "SGBD", "Base / schéma", "Lignes"],
         ["CRM", "clients", "MySQL 8.4", "ecommerce_crm", "12"],
         ["Catalogue", "produits", "PostgreSQL 16", "ecommerce_catalogue", "10"],
         ["Ventes", "commandes", "Oracle Free 23ai", "SPARK_USER (FREEPDB1)", "30"],
         ["Finance", "paiements", "SQL Server 2022", "ecommerce_paiements", "27"]],
        [2.6 * cm, 2.6 * cm, 3.4 * cm, 5.4 * cm, 1.6 * cm], aligner_droite=(4,)))

    # --- 2. Environnement ---
    s.append(Paragraph("2. Environnement mis en place", H1))
    s += puces([
        "Les quatre SGBD tournent en <b>conteneurs Docker</b> "
        "(<font face='Courier'>docker-compose.yml</font>) ; le script "
        "<font face='Courier'>scripts/setup.sh</font> rejoue la Partie A "
        "(exécution des 4 scripts <font face='Courier'>init_tp4_*.sql</font> "
        "avec le compte administrateur) et contrôle les décomptes "
        "12 / 10 / 30 / 27.",
        "PySpark 3.5.1 sur Java 17 ; une seule <font face='Courier'>"
        "SparkSession</font> reçoit les 4 pilotes JDBC via "
        "<font face='Courier'>spark.jars</font>.",
        "Adaptations à un Mac Apple Silicon : Oracle XE 21c n'existant pas "
        "en ARM, nous utilisons <b>Oracle Database Free 23ai</b> (service "
        "FREEPDB1) ; PostgreSQL est exposé sur le port <b>5433</b>. Les "
        "scripts SQL et les résultats sont identiques au sujet.",
    ])

    # --- 3. Demarche ---
    s.append(Paragraph("3. Démarche", H1))
    demarche = puces([
        "<b>Lecture</b> des 4 tables par une fonction unique "
        "<font face='Courier'>lire_jdbc(url, table, pilote)</font> : seuls "
        "l'URL, le nom de table et la classe du pilote changent.",
        "<b>Normalisation du dialecte Oracle</b> : colonnes renvoyées en "
        "MAJUSCULES (passées en minuscules) et types NUMBER ramenés en "
        "decimal (convertis en int / long). Sur notre instance, "
        "NUMBER(12) donne decimal(12,0) ; decimal(38,10) n'apparaît que "
        "pour un NUMBER sans précision.",
        "<b>Vue fédérée</b> : chaque DataFrame est exposé en vue temporaire, "
        "puis joint en SQL standard, de 2 à 4 SGBD.",
        "<b>Audit d'intégrité</b> par anti-jointures "
        "(<font face='Courier'>LEFT ANTI JOIN</font>), analyses consolidées, "
        "puis écriture du résultat dans l'entrepôt PostgreSQL "
        "<font face='Courier'>analytics.ventes_federees</font>.",
    ])
    s += demarche[:-1]
    s.append(KeepTogether([demarche[-1], Paragraph(
        "SELECT co.commande_id, cl.nom, cl.ville, pr.nom AS produit,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pr.categorie, "
        "pa.moyen_paiement, co.montant_fcfa<br/>"
        "FROM commandes co<br/>"
        "JOIN clients&nbsp;&nbsp; cl ON co.client_id&nbsp;&nbsp; = cl.client_id"
        "&nbsp;&nbsp;&nbsp;&nbsp;-- Oracle x MySQL<br/>"
        "JOIN produits&nbsp; pr ON co.produit_id&nbsp; = pr.produit_id"
        "&nbsp;&nbsp;-- x PostgreSQL<br/>"
        "JOIN paiements pa ON co.commande_id = pa.commande_id -- x SQL Server<br/>"
        "WHERE co.statut = 'livree' AND pa.statut_paiement = 'reussi'",
        CODE)]))

    # --- 4. Resultats ---
    s.append(KeepTogether([
        Paragraph("4. Résultats : de 30 commandes à 22 ventes fédérées", H1),
        tableau(
            [["Étape", "Lignes", "Explication"],
             ["Commandes (Oracle)", "30", "point de départ"],
             ["+ clients (MySQL)", "29", "CMD21 : client C999 inconnu du CRM"],
             ["+ produits (PostgreSQL)", "28", "CMD22 : produit P999 inconnu du catalogue"],
             ["+ paiements réussis, commandes livrées", "22",
              "retrait des 3 annulées (CMD07, CMD15, CMD30) et des 3 en cours "
              "(CMD12, CMD26, CMD28)"]],
            [5.4 * cm, 1.6 * cm, 9.6 * cm], aligner_droite=(1,)),
    ]))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "La jointure interne élimine silencieusement les lignes sans "
        "correspondance : sans audit, ces pertes passeraient inaperçues.",
        CORPS))

    # --- 5. Audit ---
    s.append(KeepTogether([
        Paragraph("5. Audit d'intégrité inter-SGBD", H1),
        tableau(
            [["Anomalie", "Source", "Problème", "Impact métier"],
             ["CMD21", "Oracle - commandes", "client C999 absent de MySQL",
              "15 000 FCFA encaissés (PAY18) mais exclus du CA par ville ; "
              "client impossible à contacter ou facturer."],
             ["CMD22", "Oracle - commandes", "produit P999 absent de PostgreSQL",
              "50 000 FCFA encaissés (PAY19) mais exclus du CA par catégorie ; "
              "stock et marge non calculables."],
             ["PAY27", "SQL Server - paiements", "commande CMD99 absente d'Oracle",
              "99 000 FCFA encaissés sans vente : écart comptable, "
              "remboursement ou fraude potentielle."]],
            [1.8 * cm, 3.2 * cm, 4.2 * cm, 7.4 * cm]),
    ]))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Contrôle complémentaire : les commandes <i>livrées sans paiement "
        "réussi</i> sont au nombre de <b>0</b>. Ce résultat vide prouve la "
        "cohérence entre livraisons et encaissements. Le détail figure dans "
        "<font face='Courier'>docs/AUDIT_TP4.md</font>.", CORPS))

    # --- 6. Analyses ---
    s.append(KeepTogether([
        Paragraph("6. Analyses consolidées pour la direction", H1),
        Paragraph("CA fédéré total : <b>1 452 000 FCFA</b> (22 ventes).", CORPS),
        Table([[
            tableau([["Ville", "CA (FCFA)"], ["Dakar", "723 000"],
                     ["Thies", "362 000"], ["Ziguinchor", "103 000"],
                     ["Rufisque", "85 000"], ["Autres (5 villes)", "179 000"]],
                    [2.9 * cm, 2.1 * cm], aligner_droite=(1,)),
            tableau([["Catégorie", "CA (FCFA)"], ["Informatique", "740 000"],
                     ["Telephonie", "400 000"], ["Mode", "174 000"],
                     ["Beaute", "84 000"], ["Electromenager", "54 000"]],
                    [2.9 * cm, 2.1 * cm], aligner_droite=(1,)),
            tableau([["Paiement", "CA (FCFA)"], ["Wave", "537 000"],
                     ["Carte bancaire", "395 000"], ["Orange Money", "371 000"],
                     ["Espèces", "76 000"], ["Free Money", "73 000"]],
                    [2.9 * cm, 2.1 * cm], aligner_droite=(1,)),
        ]], colWidths=[5.5 * cm] * 3),
    ]))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Le mobile money (Wave + Orange Money, 908 000 FCFA) représente "
        "environ <b>63 %</b> du CA, ce qui est typique du e-commerce sénégalais. "
        "La table consolidée est écrite dans <font face='Courier'>"
        "analytics.ventes_federees</font> ; sa relecture renvoie bien 22 lignes.",
        CORPS))

    # --- 7. Pushdown ---
    s.append(KeepTogether([
        Paragraph("7. Sous le capot : le predicate pushdown", H1), Paragraph(
        "Le plan physique d'un filtre sur la table Oracle montre "
        "<font face='Courier'>PushedFilters: [*IsNotNull(STATUT), "
        "*EqualTo(STATUT,livree)]</font> et une lecture limitée à 2 colonnes. "
        "C'est donc Oracle qui filtre, et seules les lignes utiles "
        "traversent le réseau. Sur une table de centaines de millions de "
        "lignes, sans pushdown, Spark rapatrierait la table entière avant de "
        "filtrer.", CORPS)]))

    # --- 8. Discussion ---
    s.append(Paragraph("8. Discussion et conclusion", H1))
    s += puces([
        "<b>Limites de la fédération à la volée</b> : chaque exécution "
        "sollicite les 4 bases de production (charge, dépendance à la "
        "disponibilité de chacune, lectures non simultanées, pas "
        "d'historique). La réponse du cours (séances 6-7) est un pipeline "
        "ELT orchestré par <b>Airflow</b> vers un lakehouse <b>Delta Lake</b> "
        "(couches bronze / silver / gold, transactions ACID, time travel).",
        "<b>Gouvernance</b> : sans clé étrangère inter-SGBD, l'intégrité "
        "relève de l'organisation. Chaque domaine a besoin d'un responsable "
        "des données : le paiement orphelin PAY27 revient à la Finance, en "
        "lien avec les Ventes et le contrôle interne. Les anti-jointures "
        "d'audit doivent être automatisées à chaque chargement.",
        "<b>Bilan</b> : 4 SGBD en entrée, 1 table consolidée en sortie. "
        "Tous les relevés attendus sont obtenus : 22 lignes fédérées, "
        "1 452 000 FCFA de CA et 3 anomalies documentées.",
    ])
    return s


def main():
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(SORTIE), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=2 * cm,
        title="TP 4 - Fédération de données multi-SGBD avec PySpark",
        author=", ".join(CONTRIBUTEURS),
        subject="Big Data Engineering - UCAD")
    doc.build(construire(), onFirstPage=pied_de_page, onLaterPages=pied_de_page)
    print("Rapport genere :", SORTIE)


if __name__ == "__main__":
    main()
