# TP 4 — Fédération de données multi-SGBD avec PySpark

Big Data Engineering — Master — UCAD / DMI / FST (Prof. S. Ndiaye)

Ce TP joint dans **une seule SparkSession** quatre tables réparties dans **quatre SGBD
différents**, entre lesquels n'existe aucune clé étrangère :

| Équipe | Table | SGBD | Port | Base / schéma | Lignes |
|---|---|---|---|---|---|
| CRM | `clients` | MySQL 8.4 | 3306 | `ecommerce_crm` | 12 |
| Catalogue | `produits` | PostgreSQL 16 | **5433** | `ecommerce_catalogue` | 10 |
| Ventes | `commandes` | Oracle Database Free 23ai | 1521 | `SPARK_USER` (PDB `FREEPDB1`) | 30 |
| Finance | `paiements` | SQL Server 2022 Express | 1433 | `ecommerce_paiements` | 27 |

À partir de ces tables, le notebook :
1. construit la **vue fédérée** `ventes_federees` (22 lignes) ;
2. réalise un **audit d'intégrité** par anti-jointures, qui révèle 3 anomalies ;
3. calcule le **CA consolidé** (1 452 000 FCFA) par ville, par catégorie et par moyen de paiement ;
4. écrit le résultat dans l'entrepôt PostgreSQL `analytics.ventes_federees`.

## Structure du dépôt

```
├── docker-compose.yml        # les 4 SGBD en conteneurs
├── scripts/setup.sh          # Partie A : démarrage + exécution des 4 scripts d'init
├── sql/                      # init_tp4_{mysql,postgres,oracle,sqlserver}.sql (fournis, inchangés)
├── notebooks/
│   └── TP4_federation_multi_sgbd.ipynb   # complété et exécuté avec ses sorties
├── docs/
│   ├── AUDIT_TP4.md          # anomalies d'intégrité + tableau de relevés
│   └── sujet/                # énoncés PDF
└── requirements.txt
```

## Prérequis

- Docker Desktop. Sur Apple Silicon, l'option **Rosetta** doit être activée pour l'image SQL Server, qui est en amd64.
- Java 17, par exemple avec `brew install openjdk@17`.
- Python 3.10 à 3.12.

## Lancer le TP

```bash
# 1. Les 4 SGBD + données (rejouable). Décomptes attendus : 12 / 10 / 30 / 27
./scripts/setup.sh

# 2. Environnement Python
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 3. Notebook (JAVA_HOME doit pointer vers un JDK 17)
export JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
.venv/bin/jupyter lab notebooks/TP4_federation_multi_sgbd.ipynb
```

Les 4 pilotes JDBC sont téléchargés automatiquement dans `notebooks/jars/`, un dossier ignoré par Git.

Pour arrêter et tout supprimer : `docker compose down -v`.

## Écarts par rapport au sujet (environnement Mac Apple Silicon)

| Sujet | Ici | Raison |
|---|---|---|
| Oracle XE 21c, service `XEPDB1` | Oracle Database Free 23ai, service **`FREEPDB1`** | XE 21c n'existe pas en ARM |
| PostgreSQL sur le port 5432 | port **5433** | 5432 est déjà utilisé sur la machine hôte |
| SGBD installés sous Windows | conteneurs Docker | reproductibilité |

Ces paramètres sont regroupés dans la cellule 1.1 du notebook (`PORT_*` et `ORACLE_SERVICE`).
Les scripts SQL, le compte `spark_user` et les résultats sont identiques à ceux du sujet.

Deux effets visibles d'Oracle 23ai, sans conséquence sur les résultats :
- **`ORA-03405` en fin de script Oracle.** Oracle 23ai refuse le commentaire `-- attendu : 30` placé
  sur la même ligne que le `SELECT COUNT(*)` final. Les insertions ont déjà été validées par le
  `COMMIT`, et `setup.sh` revérifie les 4 décomptes avec le compte `spark_user`.
- **Typage des colonnes `NUMBER`.** `NUMBER(5)` et `NUMBER(12)` arrivent en `decimal(5,0)` et
  `decimal(12,0)`, et non en `decimal(38,10)`. La normalisation du notebook (`cast`) reste valable.

## Résultats clés

| Mesure | Valeur |
|---|---|
| Jointure commandes ⨝ clients | 29 |
| Jointure à 3 tables | 28 |
| Vue fédérée (4 SGBD) | 22 |
| Anomalies d'audit | CMD21, CMD22, PAY27 |
| Livrées sans paiement réussi | 0 |
| CA fédéré total | 1 452 000 FCFA |

Le détail se trouve dans [`docs/AUDIT_TP4.md`](docs/AUDIT_TP4.md).
