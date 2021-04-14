from django.core.management.base import BaseCommand, CommandError
import os
import obonet
import networkx


class Command(BaseCommand):
    help = "Updates the Human Phenotype Ontology(HPO) url."

    def add_arguments(self, parser):
        parser.add_argument('hpo_url', type=str)

    def handle(self, *args, **options):
        try:
            hpo_url = options['hpo_url']
            obonet.read_obo(hpo_url)
        except (ValueError, networkx.exception.NetworkXError, KeyError, TypeError, FileNotFoundError):
            raise CommandError("Couldn't resolve url for building new HPO graph.")
        try:
            os.environ['HPO_GRAPH_PATH'] = hpo_url
            print(os.environ.get("HPO_GRAPH_PATH"))
            self.stdout.write(self.style.SUCCESS('Successfully updated HPO path.'))
        except EnvironmentError:
            raise CommandError("An error occurred. Update got interrupted please try again.")
