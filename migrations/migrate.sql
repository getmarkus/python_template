-- Create the schema
CREATE SCHEMA IF NOT EXISTS "issue_analysis";

-- Create "issue" table in the issue_analysis schema
CREATE TABLE "issue_analysis"."issue" (
    "version" integer NOT NULL,
    "issue_number" integer NOT NULL,
    "issue_state" varchar NOT NULL,
    PRIMARY KEY ("issue_number")
);

