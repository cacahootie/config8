
test:
	@echo 'MAKE: Running tests'
	@pytest -v
	@echo 'MAKE: Complete'

test-sql:
	@echo 'MAKE: Running tests'
	make update-schema
	@pytest -v config8/merger/test_psql_adapter.py
	@echo 'MAKE: Complete'

update-schema:
	@echo 'MAKE: Updating schema'
	@psql -d test_config8 -f test_data/test_sql/schema.sql
	@echo 'MAKE: Schema update complete'
