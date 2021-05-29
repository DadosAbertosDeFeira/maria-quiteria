import django
from configurations.importer import install

install(check_options=True)
django.setup()
