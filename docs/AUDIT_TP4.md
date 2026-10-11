# Audit d'intégrité inter-SGBD — TP 4

**Contributeurs :** Deschant Kounou · Ulrich Kpassi-Gobi

**Périmètre :** les 4 tables fédérées par Spark.
- `clients` : MySQL
- `produits` : PostgreSQL
- `commandes` : Oracle
- `paiements` : SQL Server

**Méthode :** aucune clé étrangère ne traverse les SGBD. L'intégrité référentielle est donc
vérifiée par **anti-jointures** (`LEFT ANTI JOIN`) dans Spark SQL : section 7 du notebook
[`notebooks/TP4_federation_multi_sgbd.ipynb`](../notebooks/TP4_federation_multi_sgbd.ipynb).

## Les trois anomalies détectées

| # | Identifiant | Table / SGBD source | Référence cassée | Montant | Impact métier |
|---|---|---|---|---|---|
| 1 | **CMD21** | `spark_user.commandes`, Oracle (Ventes) | client `C999` absent de `clients` (MySQL) | 15 000 FCFA, encaissés via Wave (PAY18) | Une vente livrée et payée n'est rattachée à aucun client : elle est **exclue du CA par ville** et le client ne peut être ni contacté, ni facturé, ni fidélisé. |
| 2 | **CMD22** | `spark_user.commandes`, Oracle (Ventes) | produit `P999` absent de `produits` (PostgreSQL) | 50 000 FCFA, encaissés via Free Money (PAY19) | La vente porte sur un article inconnu du catalogue : elle est **exclue du CA par catégorie**, le stock ne peut pas être décrémenté et la marge reste impossible à calculer. |
| 3 | **PAY27** | `dbo.paiements`, SQL Server (Finance) | commande `CMD99` absente de `commandes` (Oracle) | 99 000 FCFA, Wave, statut `reussi` | De l'argent a été **encaissé sans aucune vente correspondante**. C'est un écart de rapprochement comptable : erreur de saisie, remboursement à prévoir ou fraude potentielle. |

**Effet cumulé :** 15 000 + 50 000 = **65 000 FCFA** ont été réellement encaissés mais sont
absents de la vue fédérée, qui s'appuie sur des jointures internes. À l'inverse, **99 000 FCFA**
sont encaissés sans aucune vente pour les justifier.

**Contrôle complémentaire (exercice 8) :** la requête « commandes livrées sans paiement réussi »
renvoie **0 ligne**. Toutes les livraisons sont donc encaissées, ce qui confirme la cohérence
entre livraisons et encaissements dans le sens Ventes → Finance. Ce résultat vide est une preuve
d'audit, pas un échec de requête.

## Recommandations

1. **Corriger à la source :**
   - Le CRM crée ou retrouve le client de CMD21.
   - Le Catalogue référence P999, ou les Ventes corrigent la ligne de CMD22.
   - La Finance et les Ventes enquêtent sur PAY27 avec l'opérateur Wave.
2. **Industrialiser le contrôle :** rejouer ces anti-jointures à chaque chargement, par exemple
   avec une tâche Airflow de qualité de données, et alerter dès qu'une anomalie apparaît.
3. **Désigner un responsable (data owner) par domaine.** L'intégrité inter-SGBD relève de
   l'organisation et non d'un SGBD.

## Tableau de relevés

Valeurs recopiées de la section 11 du notebook, exécuté de bout en bout :

| Mesure | Valeur |
|---|---:|
| nb_clients (MySQL) | 12 |
| nb_produits (PostgreSQL) | 10 |
| nb_commandes (Oracle) | 30 |
| nb_paiements (SQL Server) | 27 |
| jointure commandes-clients | 29 |
| jointure 3 tables | 28 |
| vue federee (4 SGBD) | 22 |
| commandes sans client | 1 |
| commandes sans produit | 1 |
| paiements orphelins | 1 |
| livrees sans paiement reussi | 0 |
| CA federe total (FCFA) | 1 452 000 |

### Analyses consolidées (exercice 9)

| Regroupement | Tête de classement | CA (FCFA) |
|---|---|---:|
| Par ville | Dakar | 723 000 |
| Par catégorie | Informatique | 740 000 |
| Par moyen de paiement | Wave | 537 000 |

Le mobile money (Wave 537 000 + Orange Money 371 000 = 908 000 FCFA) représente **≈ 63 %** du CA
fédéré.

La table consolidée est écrite dans l'entrepôt PostgreSQL sous `analytics.ventes_federees`.
La relecture renvoie bien **22 lignes**.
