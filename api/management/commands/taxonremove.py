from .serializers import *
from .models import *


class Command(BaseCommand):
    help = 'Remove unused taxonomies from our database'

    def handle(self, *args, **options):
        self.stdout.write('Running...')

        for tax in Taxon.objects.all():
            if not (tax.taxonrank.any_assays() or tax.taxonrank.any_child_assays()):
                tax.delete()
        for taxrank in TaxonRank.objects.all():
            if not (taxrank.any_assays() or taxrank.any_child_assays()):
                taxrank.delete()

        self.stdout.write(self.style.SUCCESS('Successfully removed unused taxons'))
