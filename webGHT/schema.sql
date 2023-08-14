DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS cred;
DROP TABLE IF EXISTS org_teams;
DROP TABLE IF EXISTS org_webhooks;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    permission TEXT NOT NULL
    -- `superadmin`: full permission
    -- `projectadmin`: full control repo (not delete)
    -- `member`: only view 
);

CREATE TABLE cred (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    org_name TEXT,
    token TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE org_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    team_name TEXT UNIQUE,
    FOREIGN KEY (org_id) REFERENCES cred (id)
);

CREATE TABLE org_webhooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    webhook_url TEXT UNIQUE,
    FOREIGN KEY (org_id) REFERENCES cred (id)
);