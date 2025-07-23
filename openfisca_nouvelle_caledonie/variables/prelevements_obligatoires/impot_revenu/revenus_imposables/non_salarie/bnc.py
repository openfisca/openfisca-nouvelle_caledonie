"""Bénéfices non commerciaux (BNC)."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie import (
    get_multiple_and_plafond_cafat_cotisation,
)


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


class bnc(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Bénéfices non commerciaux"
    definition_period = YEAR

    def formula(individu, period, parameters):
        diviseur = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie.bnc.diviseur_recettes
        multiple, plafond_cafat = get_multiple_and_plafond_cafat_cotisation(
            period, parameters
        )
        return max_(
            0,
            individu("bnc_recettes_ht", period) / diviseur  # Forfait
            - min_(
                individu("reste_cotisations_apres_bic_ba_avant_bnc", period),
                multiple * plafond_cafat,
            ),
        ) + max_(
            (
                individu("benefices_non_commerciaux_reel_simplifie", period)
                - individu("deficits_non_commerciaux_reel_simplifie", period)
            ),
            0,  # Réel
        )
