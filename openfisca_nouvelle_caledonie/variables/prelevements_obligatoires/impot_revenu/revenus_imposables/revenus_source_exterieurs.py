"""Revenus de surces extérieures à la Nouvelle Calédonie."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal

# REVENUS DE SOURCE EXTÉRIEURE À LA NOUVELLE-CALÉDONIE

# Si vous avez perçu des revenus de source métropolitaine (ex : revenus fonciers)
# expressément exonérés d’impôt en Nouvelle-Calédonie par la convention fiscale
# franco-calédonienne et/ou des revenus de source étrangère pour lesquels un impôt
# personnel sur le revenu a été acquitté, portez ces revenus ligne VA.
# Pour davantage de précisions, un dépliant d’information est à votre disposition dans
# nos locaux ou sur notre site dsf.gouv.nc


class revenus_de_source_exterieur(Variable):
    value_type = float
    unit = "currency"
    cerfa_field = "VA"
    entity = FoyerFiscal
    label = "Revenus de source extérieure à la Nouvelle-Calédonie"
    definition_period = YEAR
