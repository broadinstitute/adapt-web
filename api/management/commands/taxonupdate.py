import requests
import zipfile
from tqdm import tqdm

from io import BytesIO

from django.core.management.base import BaseCommand, CommandError
from api.views import TaxonRankViewSet


NCBI_TAX_URL = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"
NCBI_NEIGHBORS_URL = "https://www.ncbi.nlm.nih.gov/genomes/GenomesGroup.cgi?taxid=10239&cmd=download2"

class Command(BaseCommand):
    help = 'Updates taxonomy database with NCBI\'s most recent information'

    def handle(self, *args, **options):
        self.stdout.write('Getting taxon data...')
        # Get taxdump folder and unzip
        ncbi_tax_folder_zip = requests.get(NCBI_TAX_URL)
        viral_taxa = set()
        name_to_taxid = {}
        with zipfile.ZipFile(BytesIO(ncbi_tax_folder_zip.content)) as ncbi_tax_folder:
            # Determine what number the Viruses division is
            # Was 9 as of 2021/02/15, use as default
            viral_division = 9
            try:
                with ncbi_tax_folder.open('division.dmp') as tax_division:
                    for row in tax_division:
                        # Note-no headers, so required to use position in list
                        cells = row.decode("utf-8") .split("\t|\t")
                        if cells[1] == "VRL":
                            viral_division = cells[0]
                            break
            except KeyError: # File does not exist
                pass

            # Determine which tax IDs are viruses
            # Note-files have no headers, so required to use position in list
            with ncbi_tax_folder.open('nodes.dmp') as tax_nodes:
                for row in tax_nodes:
                    cells = row.decode("utf-8").split("\t|\t")
                    if cells[4] == viral_division:
                        viral_taxa.add(cells[0])

            # Determine what the names for the tax IDs are
            with ncbi_tax_folder.open('names.dmp') as tax_names:
                for row in tax_names:
                    cells = row.decode("utf-8").split("\t|\t")
                    taxid = cells[0]
                    name = cells[1]
                    if taxid in viral_taxa:
                        name_to_taxid[name] = int(taxid)
                        # if cells[3].startswith("scientific name"):
                        #     viral_nodes[cells[0]]["latin_name"] = name
                        # else:
                        #     viral_nodes[cells[0]]["description"].append(name + ";")

        ncbi_neighbors_table = requests.get(NCBI_NEIGHBORS_URL)
        prev_name = None
        prev_seg = None
        self.stdout.write('Getting viral and segment data (may take a while)...')
        for row in tqdm(ncbi_neighbors_table.content.decode("utf-8").split("\r\n")):
            if row.startswith("##"):
                continue
            cells = row.split("\t")
            # hosts = cells[2]
            name = cells[4]
            segment = cells[5]
            if name == prev_name and segment == prev_seg:
                continue
            # if "vertebrate" in hosts or "human" in hosts:
            if name in name_to_taxid:
                taxid = name_to_taxid[name]
                taxonrank_obj = TaxonRankViewSet.save_or_get_taxid(taxid)
                if segment != "segment  ":
                    # Remove "segment " (8 characters) from segment name
                    segment_name = segment[8:]
                    segment_taxonrank = TaxonRankViewSet.save_by_rank(segment_name, 'segment', parent=taxonrank_obj)
            prev_name = name
            prev_seg = segment

        self.stdout.write(self.style.SUCCESS('Successfully updated taxons'))
