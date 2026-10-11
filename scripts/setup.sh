#!/usr/bin/env bash
# Partie A du TP4 : demarre les 4 SGBD et execute les scripts init_tp4_*.sql
# avec le compte administrateur de chacun. Rejouable.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Demarrage des 4 SGBD"
docker compose up -d

echo "==> Attente des healthchecks (Oracle et SQL Server peuvent prendre 1-2 min)"
for svc in tp4-mysql tp4-postgres tp4-oracle tp4-sqlserver; do
  printf "    %-14s" "$svc"
  until [ "$(docker inspect -f '{{.State.Health.Status}}' "$svc")" = "healthy" ]; do
    sleep 3
  done
  echo "pret"
done

echo "==> MySQL      : init_tp4_mysql.sql"
docker exec tp4-mysql sh -c "mysql -uroot -p'RootTp4!' < /sql/init_tp4_mysql.sql" 2>/dev/null

echo "==> PostgreSQL : init_tp4_postgres.sql"
docker exec tp4-postgres psql -q -U postgres -f /sql/init_tp4_postgres.sql

echo "==> Oracle     : init_tp4_oracle.sql"
docker exec tp4-oracle sqlplus -s system/OracleTp4@//localhost:1521/FREEPDB1 @/sql/init_tp4_oracle.sql

echo "==> SQL Server : init_tp4_sqlserver.sql"
docker exec tp4-sqlserver /opt/mssql-tools18/bin/sqlcmd -C -S localhost \
  -U sa -P 'SqlServerTp4!' -i /sql/init_tp4_sqlserver.sql

echo "==> Verification des decomptes avec le compte spark_user (attendu : 12 / 10 / 30 / 27)"
n_my=$(docker exec tp4-mysql mysql -N -uspark_user -p'Ucad2026!' ecommerce_crm \
  -e "SELECT COUNT(*) FROM clients" 2>/dev/null)
n_pg=$(docker exec -e PGPASSWORD='Ucad2026!' tp4-postgres psql -tA -h localhost \
  -U spark_user -d ecommerce_catalogue -c "SELECT COUNT(*) FROM produits")
n_or=$(echo "SELECT COUNT(*) FROM commandes;" | docker exec -i tp4-oracle \
  sqlplus -s 'spark_user/"Ucad2026!"@//localhost:1521/FREEPDB1' | tr -dc '0-9')
n_ms=$(docker exec tp4-sqlserver /opt/mssql-tools18/bin/sqlcmd -C -S localhost \
  -U spark_user -P 'Ucad2026!' -d ecommerce_paiements -h -1 \
  -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM dbo.paiements" | tr -dc '0-9')
echo "    clients (MySQL)        : $n_my"
echo "    produits (PostgreSQL)  : $n_pg"
echo "    commandes (Oracle)     : $n_or"
echo "    paiements (SQL Server) : $n_ms"
[ "$n_my/$n_pg/$n_or/$n_ms" = "12/10/30/27" ] && echo "==> [ OK ] Partie A terminee" \
  || { echo "==> [ECHEC] decomptes inattendus"; exit 1; }
