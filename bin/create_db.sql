-- usado apenas para testes
CREATE DATABASE core;
CREATE USER ademir WITH PASSWORD 'xxx';

ALTER ROLE ademir SET client_encoding TO 'utf8';
ALTER ROLE ademir SET default_transaction_isolation TO 'read committed';
ALTER ROLE ademir SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE core TO ademir;

ALTER USER ademir CREATEDB;
