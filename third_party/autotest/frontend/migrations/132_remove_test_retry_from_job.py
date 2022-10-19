def migrate_up(mgr):
    mgr.execute("ALTER TABLE afe_jobs DROP COLUMN test_retry;")

def migrate_down(mgr):
    mgr.execute("ALTER TABLE afe_jobs ADD COLUMN test_retry int(11) NOT NULL DEFAULT '0';")

