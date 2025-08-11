.PHONY: test test-unit test-api test-models test-coverage test-fast install migrate shell clean

# Python/Django commands
PYTHON = pipenv run python
MANAGE = $(PYTHON) manage.py
PYTEST = pipenv run pytest

# Installation and setup
install:
	pipenv install --dev
	$(MANAGE) migrate
	@echo "✅ Installation complete!"

# Database commands
migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

migrate-check:
	$(MANAGE) makemigrations --check --dry-run

# Testing commands (using Django test runner for simplicity)
test:
	$(MANAGE) test apps --verbosity=2

test-models:
	$(MANAGE) test apps.form_builder.tests --verbosity=2

test-api:
	$(MANAGE) test apps.api.tests --verbosity=2

test-serializers:
	$(MANAGE) test apps.api.test_serializers --verbosity=2

test-coverage:
	DJANGO_SETTINGS_MODULE=formatic_project.settings pipenv run coverage run --source=apps --omit="*/migrations/*,*/tests/*,*/test_*.py,*/factories.py" manage.py test apps
	pipenv run coverage report
	pipenv run coverage html

test-specific:
	$(MANAGE) test $(TEST) --verbosity=2

# Quality assurance
lint:
	pipenv run flake8 apps/
	pipenv run black --check apps/

format:
	pipenv run black apps/
	pipenv run isort apps/

# Development commands  
shell:
	$(MANAGE) shell

runserver:
	$(MANAGE) runserver

# Database utilities
loaddata:
	$(MANAGE) loaddata apps/form_builder/fixtures/question_types.json

dumpdata:
	$(MANAGE) dumpdata form_builder.QuestionType --indent=2 > apps/form_builder/fixtures/question_types.json

# Clean up
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
	rm -f test-results.xml

# Help
help:
	@echo "Available commands:"
	@echo "  install         - Install dependencies and run migrations"
	@echo "  migrate         - Run Django migrations"
	@echo "  test            - Run all tests"
	@echo "  test-models     - Run model tests only"
	@echo "  test-api        - Run API tests only" 
	@echo "  test-serializers- Run serializer tests only"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  test-specific   - Run specific test (use TEST=apps.form_builder.tests.SomeTest)"
	@echo "  lint            - Check code style"
	@echo "  format          - Format code"
	@echo "  shell           - Django shell"
	@echo "  runserver       - Run development server"
	@echo "  clean           - Clean up temporary files"
	@echo ""
	@echo "Alternative test runner:"
	@echo "  python test.py [--models|--api|--serializers|--coverage|--verbose|--fast]"