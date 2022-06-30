# adapt-web/vue_frontend/src/components
Components

## Universal

### [Header](Header.vue)
Display header (logo, menu, and [Github corner](https://tholman.com/github-corners/))

### [Footer](Footer.vue)
Display footer (contact, acknowledgements, and logo)


## Common

### [Modal](Modal.vue)
Relay messages to the user, such as error messages or status messages.

The content is controlled by the root variables:
* `vm.$root.$data.modaltitle`: Sets the title of the modal
* `vm.$root.$data.modalmsg`: Sets the message within the modal
* `vm.$root.$data.modalvariant`: Sets the color of the modal; one of `danger`, `warning`, `info`, `success`, `dark`, and `light`

The modal is displayed when the event `show-msg` is emitted.

### [Assay Modal](AssayModal.vue)
Display and download assays

The content is controlled by the root variables:
* `vm.$root.$data.resulttable`: (Object) Assays to be displayed. An object with labels of either the run IDs or the primary keys of the taxa to display. Each label contains a list of clusters. Each cluster contains a list of assays.
* `vm.$root.$data.aln_sum`: (Object) The alignment summary for each label, if it exists
* `vm.$root.$data.aln`: (Object) Boolean for each label if the alignment exists
* `vm.$root.$data.ann`: (Object) The annotations for the alignment, if it exists
* `vm.$root.$data.labels`: (Array) All the labels to display (the result table may contain extras)
* `vm.$root.$data.runid`: (String) The run ID if it exists

The modal is displayed when the event `show-assays` is emitted.

#### [Genome](Genome.vue)
Visualize the alignment (and possibly annotations) an assay set uses

The content is controlled by the props:
* `cluster_id`: (String) The label that the genome is associated with.
* `alignmentLength`: (Number) How many bases are in the alignment
* `assays`: (Array) Assays for this alignment
* `annotations`: (Array) Annotations of the alignment

#### [Assay](Assay.vue)
Visualize a single assay

#### [Assay Table](AssayTable.vue)
Display the assays in text format

#### [Color Legend](ColorLegend.vue)
Display a legend for what the colors mean in the visualization


## About page

### [About](About.vue)
Describe and explain ADAPT


## Designs page

### [Design](Design.vue)
Display all the taxon that do not have a parent taxon

#### [Family](Family.vue)
Display a family

##### [Expand Family](ExpandFamily.vue)
Expand the subtaxa of a family (genuses/species)

#### [Genus](Genus.vue)
Display a genus

##### [Expand Genus](ExpandGenus.vue)
Expand the subtaxa of a genus (species)

#### [Species](Species.vue)
Display a species

##### [Expand Species](ExpandSpecies.vue)
Expand the subtaxa of a species (subspecies)

#### [Subspecies](Subspecies.vue)
Display a subspecies


## Run page
### [Run ADAPT](RunADAPT.vue)
Create a form that allows people to submit jobs to the backend server


## Results page
### [Results](Results.vue)
Create a form that allows people to view the results of their jobs
