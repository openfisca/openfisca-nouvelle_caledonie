"""Revenus fonciers."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal

# REVENUS FONCIERS

# Si vous avez disposé de revenus locatifs en 2024, vous devez renseigner obliga-
# toirement la déclaration catégorielle de couleur bleue, intitulée « déclaration des
# revenus fonciers ». Joignez-la à votre déclaration des revenus.
# Reportez le résultat des lignes F, H ou E de la déclaration catégorielle sur votre
# déclaration des revenus : à la ligne AA s’il s’agit d’un bénéfice ou à la ligne AG s’il
# s’agit d’un déficit.
# Reportez le résultat de la ligne J de la déclaration catégorielle à la ligne AD de votre
# déclaration des revenus pour leur imposition à la Contribution Calédonienne de
# Solidarité (CCS) au taux de 4 %


class revenus_fonciers_soumis_ir(Variable):
    value_type = float
    unit = "currency"
    cerfa_field = "AA"
    entity = FoyerFiscal
    label = "Revenus fonciers soumis à l'IR"
    definition_period = YEAR


class revenus_fonciers_soumis_ccs(Variable):
    value_type = float
    unit = "currency"
    cerfa_field = "AD"
    entity = FoyerFiscal
    label = "Revenus fonciers soumis à la CCS"
    definition_period = YEAR


class deficits_fonciers(Variable):
    value_type = float
    unit = "currency"
    cerfa_field = "AG"
    entity = FoyerFiscal
    label = "Déficits fonciers"
    definition_period = YEAR
