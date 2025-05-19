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


# Régime réel simplifié (Cadre 10 de la déclaration complémentaire)


class benefices_non_commerciaux_reel_simplifie(Variable):
    unit = "currency"
    cerfa_field = {
        0: "KA",
        1: "KB",
    }
    value_type = float
    entity = Individu
    label = "Bénéfices non commerciaux au régime réel simplifié"
    definition_period = YEAR


class deficits_non_commerciaux_reel_simplifie(Variable):
    unit = "currency"
    cerfa_field = {
        0: "KJ",
        1: "KK",
    }
    value_type = float
    entity = Individu
    label = "Déficits non commerciaux au régime réel simplifié"
    definition_period = YEAR
