# adapt-web/vue_frontend/src/pages
Page structure

Each page on the website is one of the folders in here. The page has 2 files: `App.vue` and `main.js`.
`App.vue` imports and organizes components on the page; `main.js` imports dependencies and renders the page.
`App.vue` contains the [Header](../components/README.md#header), then a container for the body, and the [Footer](../components/README.md#footer).
The body is a row with 3 columns to provide borders on the sides.

Note: Each component (except the modals and taxon levels) has a fade in transition either surrounding it in its class or in the page rendering itself to make it smoother.
TODO: The taxon levels probably could also be fade in.

## [About](About/App.vue)
[adapt.run](adapt.run)

Body components directly referenced:
 * [About](../components/README.md#about)

This is a one component page and is straightforward.

## [Designs](Designs/App.vue)
[adapt.run/designs](adapt.run/designs)

Body components directly referenced:
 * [Design](../components/README.md#modal)
 * [Assay Modal](../components/README.md#assay-modal)
 * [Modal](../components/README.md#modal)

Design is the main component on the page, and most of the rendering is done in that component.
The button itself is rendered directly on this page and is not a component (to make variable sharing easier).
The Assay Modal and Modal component are referenced at the end, but will not be rendered unless an event is emitted (`show-assays` for the Assay Modal and `show-msg` for the Modal) by this page.
Several functions to load data and communicate between components are in [`Designs/App.vue`](Designs/App.vue); see details for them in the file itself.

## RunADAPT
[adapt.run/run](adapt.run/run)

Body components directly referenced:
 * [Run ADAPT](../components/README.md#run-adapt)
 * [Modal](../components/README.md#modal)

This is almost a one component page; the Modal at the end is only rendered if the event `show-msg` is emitted by Run ADAPT.

## Results
[adapt.run/results](adapt.run/results)

Body components directly referenced:
 * [Results](../components/README.md#results)
 * [Assay Modal](../components/README.md#assay-modal)
 * [Modal](../components/README.md#modal)

This is also almost a one component page; the Assay Modal / Modal at the end is only rendered if the event `show-assays` / `show-msg` (respectively) is emitted by Results.
