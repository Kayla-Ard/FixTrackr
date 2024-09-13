from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Clears all tables from the database."

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                sql = """
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
                """
                cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS("Successfully dropped all tables."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error occurred: {e}"))