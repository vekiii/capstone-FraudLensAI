-- Feature 005 T004: immutable canonical live facts. Apply once as a database administrator.
-- Amount bounds mirror transaction-event.schema.json: 0 <= amount < 10^13, scale <= 6.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'migration_owner') THEN
        EXECUTE 'CREATE ROLE migration_owner NOLOGIN';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'live_producer') THEN
        EXECUTE 'CREATE ROLE live_producer NOLOGIN';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cdc_connector') THEN
        EXECUTE 'CREATE ROLE cdc_connector NOLOGIN';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'live_worker') THEN
        EXECUTE 'CREATE ROLE live_worker NOLOGIN';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'label_curator') THEN
        EXECUTE 'CREATE ROLE label_curator NOLOGIN';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'registry_operator') THEN
        EXECUTE 'CREATE ROLE registry_operator NOLOGIN';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'live_api_reader') THEN
        EXECUTE 'CREATE ROLE live_api_reader NOLOGIN';
    END IF;
END
$$;

CREATE SCHEMA fraudlens AUTHORIZATION migration_owner;
REVOKE ALL ON SCHEMA fraudlens FROM PUBLIC;

SET ROLE migration_owner;

CREATE TABLE fraudlens.live_transactions (
    transaction_id VARCHAR(128) PRIMARY KEY
        CHECK (transaction_id ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$'),
    source_namespace VARCHAR(80) NOT NULL CHECK (length(btrim(source_namespace)) > 0),
    source_event_id VARCHAR(128) NOT NULL CHECK (length(btrim(source_event_id)) > 0),
    event_fact_digest CHAR(64) NOT NULL CHECK (event_fact_digest ~ '^[0-9a-f]{64}$'),
    event_time TIMESTAMPTZ NOT NULL CHECK (isfinite(event_time)),
    sender_bank VARCHAR(128) NOT NULL CHECK (length(btrim(sender_bank)) > 0),
    sender_account VARCHAR(128) NOT NULL CHECK (length(btrim(sender_account)) > 0),
    receiver_bank VARCHAR(128) NOT NULL CHECK (length(btrim(receiver_bank)) > 0),
    receiver_account VARCHAR(128) NOT NULL CHECK (length(btrim(receiver_account)) > 0),
    paid_amount NUMERIC NOT NULL
        CHECK (paid_amount >= 0 AND paid_amount < 10000000000000 AND scale(paid_amount) <= 6),
    paid_currency VARCHAR(17) NOT NULL CHECK (length(btrim(paid_currency)) > 0),
    received_amount NUMERIC NOT NULL
        CHECK (received_amount >= 0 AND received_amount < 10000000000000 AND scale(received_amount) <= 6),
    received_currency VARCHAR(17) NOT NULL CHECK (length(btrim(received_currency)) > 0),
    payment_format VARCHAR(80),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp() CHECK (isfinite(ingested_at)),
    CONSTRAINT live_transactions_source_identity_uq UNIQUE (source_namespace, source_event_id)
);

CREATE INDEX live_transactions_event_order_idx
    ON fraudlens.live_transactions (event_time, transaction_id);

CREATE TABLE fraudlens.ingestion_receipts (
    source_namespace VARCHAR(80) NOT NULL,
    source_event_id VARCHAR(128) NOT NULL,
    transaction_id VARCHAR(128) NOT NULL,
    event_fact_digest CHAR(64) NOT NULL CHECK (event_fact_digest ~ '^[0-9a-f]{64}$'),
    received_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp() CHECK (isfinite(received_at)),
    result VARCHAR(16) NOT NULL CHECK (result IN ('inserted')),
    PRIMARY KEY (source_namespace, source_event_id),
    CONSTRAINT ingestion_receipts_transaction_fk
        FOREIGN KEY (transaction_id) REFERENCES fraudlens.live_transactions (transaction_id),
    CONSTRAINT ingestion_receipts_source_fact_fk
        FOREIGN KEY (source_namespace, source_event_id)
        REFERENCES fraudlens.live_transactions (source_namespace, source_event_id)
);

CREATE FUNCTION fraudlens.reject_live_transaction_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = pg_catalog, fraudlens
AS $function$
BEGIN
    RAISE EXCEPTION 'live_transactions rows are immutable'
        USING ERRCODE = '55000';
END
$function$;

CREATE TRIGGER live_transactions_immutable
    BEFORE UPDATE OR DELETE ON fraudlens.live_transactions
    FOR EACH ROW EXECUTE FUNCTION fraudlens.reject_live_transaction_mutation();

CREATE FUNCTION fraudlens.record_live_transaction(
    p_transaction_id VARCHAR(128),
    p_source_namespace VARCHAR(80),
    p_source_event_id VARCHAR(128),
    p_event_fact_digest CHAR(64),
    p_event_time TIMESTAMPTZ,
    p_sender_bank VARCHAR(128),
    p_sender_account VARCHAR(128),
    p_receiver_bank VARCHAR(128),
    p_receiver_account VARCHAR(128),
    p_paid_amount NUMERIC,
    p_paid_currency VARCHAR(17),
    p_received_amount NUMERIC,
    p_received_currency VARCHAR(17),
    p_payment_format VARCHAR(80)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, fraudlens
AS $function$
DECLARE
    existing_fact fraudlens.live_transactions%ROWTYPE;
    inserted_rows BIGINT;
BEGIN
    INSERT INTO fraudlens.live_transactions (
        transaction_id, source_namespace, source_event_id, event_fact_digest, event_time,
        sender_bank, sender_account, receiver_bank, receiver_account,
        paid_amount, paid_currency, received_amount, received_currency, payment_format
    ) VALUES (
        p_transaction_id, p_source_namespace, p_source_event_id, p_event_fact_digest, p_event_time,
        p_sender_bank, p_sender_account, p_receiver_bank, p_receiver_account,
        p_paid_amount, p_paid_currency, p_received_amount, p_received_currency, p_payment_format
    ) ON CONFLICT DO NOTHING;

    GET DIAGNOSTICS inserted_rows = ROW_COUNT;
    IF inserted_rows = 1 THEN
        INSERT INTO fraudlens.ingestion_receipts (
            source_namespace, source_event_id, transaction_id, event_fact_digest, result
        ) VALUES (
            p_source_namespace, p_source_event_id, p_transaction_id, p_event_fact_digest, 'inserted'
        );
        RETURN TRUE;
    END IF;

    SELECT * INTO existing_fact
    FROM fraudlens.live_transactions
    WHERE (source_namespace = p_source_namespace AND source_event_id = p_source_event_id)
       OR transaction_id = p_transaction_id
    ORDER BY transaction_id
    LIMIT 1;

    IF FOUND
       AND existing_fact.transaction_id IS NOT DISTINCT FROM p_transaction_id
       AND existing_fact.source_namespace IS NOT DISTINCT FROM p_source_namespace
       AND existing_fact.source_event_id IS NOT DISTINCT FROM p_source_event_id
       AND existing_fact.event_fact_digest IS NOT DISTINCT FROM p_event_fact_digest
       AND existing_fact.event_time IS NOT DISTINCT FROM p_event_time
       AND existing_fact.sender_bank IS NOT DISTINCT FROM p_sender_bank
       AND existing_fact.sender_account IS NOT DISTINCT FROM p_sender_account
       AND existing_fact.receiver_bank IS NOT DISTINCT FROM p_receiver_bank
       AND existing_fact.receiver_account IS NOT DISTINCT FROM p_receiver_account
       AND existing_fact.paid_amount IS NOT DISTINCT FROM p_paid_amount
       AND existing_fact.paid_currency IS NOT DISTINCT FROM p_paid_currency
       AND existing_fact.received_amount IS NOT DISTINCT FROM p_received_amount
       AND existing_fact.received_currency IS NOT DISTINCT FROM p_received_currency
       AND existing_fact.payment_format IS NOT DISTINCT FROM p_payment_format THEN
        RETURN FALSE;
    END IF;

    RAISE EXCEPTION 'source event reused with different facts'
        USING ERRCODE = '23505';
END
$function$;

REVOKE ALL ON ALL TABLES IN SCHEMA fraudlens FROM PUBLIC;
REVOKE ALL ON FUNCTION fraudlens.reject_live_transaction_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION fraudlens.record_live_transaction(
    VARCHAR, VARCHAR, VARCHAR, CHAR, TIMESTAMPTZ, VARCHAR, VARCHAR, VARCHAR, VARCHAR,
    NUMERIC, VARCHAR, NUMERIC, VARCHAR, VARCHAR
) FROM PUBLIC;

GRANT USAGE ON SCHEMA fraudlens TO live_producer, cdc_connector, live_worker;
GRANT SELECT ON fraudlens.live_transactions TO cdc_connector, live_worker;
GRANT EXECUTE ON FUNCTION fraudlens.record_live_transaction(
    VARCHAR, VARCHAR, VARCHAR, CHAR, TIMESTAMPTZ, VARCHAR, VARCHAR, VARCHAR, VARCHAR,
    NUMERIC, VARCHAR, NUMERIC, VARCHAR, VARCHAR
) TO live_producer;

RESET ROLE;