"""Bénéfices non commerciaux (BNC)."""


from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu


class bnc_recettes_ht(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "HA",
        1: "HB",
        2: "HC",
    }
    entity = Individu
    label = "Recettes annuelles des bénéfices non-commerciaux"
    definition_period = YEAR
