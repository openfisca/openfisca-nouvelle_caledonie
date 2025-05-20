"""Bénéfices agricoles (BA)."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu


class chiffre_d_daffaires_agricole_ht_imposable(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "GA",
        1: "GB",
        2: "GC",
    }
    entity = Individu
    label = "Chiffre d’affaires hors taxes tiré des exploitations agricoles imposables"
    definition_period = YEAR
    # Le bénéfice, égal à 1/6 e de ce chiffre d’affaires sera déterminé automatiquement.


class chiffre_d_daffaires_agricole_ht_exonere(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "GD",
        1: "GE",
        2: "GF",
    }
    entity = Individu
    label = "Chiffre d’affaires hors taxes tiré des exploitations agricoles exonérées en vertu d’un bail rural"
    definition_period = YEAR


class ba(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Bénéfices agricoles"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        # Au forfait
        # Le bénéfice, égal à 1/6 e de ce chiffre d’affaires sera déterminé automatiquement.
        diviseur = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.travailleurs_independants.ba.diviseur_ca
        return (
            max_(
                0,
                foyer_fiscal("chiffre_d_daffaires_agricole_ht_imposable", period),
                # TODO: déduire mes cotisations dans la limite d'un plafond
                # min_(
                # foyer_fiscal("cotisations_retraite_exploitant", period),
                #  plafonf
                # )
                # - foyer_fiscal("cotisations_ruamm_mutuelle_ccs_exploitant", period)
                # )
            )
            / diviseur
        )


# Régime réel simplifié (Cadre 10 de la déclaration complémentaire)


class benefices_agricoles_regime_reel(Variable):
    unit = "currency"
    cerfa_field = {
        0: "JA",
        1: "JB",
    }
    value_type = float
    entity = Individu
    label = "Bénéfices agricoles du régime réel simplifié"
    definition_period = YEAR


class deficits_agricoles_regime_reel(Variable):
    unit = "currency"
    cerfa_field = {
        0: "JD",
        1: "JE",
    }
    value_type = float
    entity = Individu
    label = "Déficits agricoles du régime réel simplifié"
    definition_period = YEAR


# TODO: à compléter
# class reliquat_cotisation_apres_ba(Variable):
#     unit = "currency"
#     value_type = float
#     entity = Individu
#     label = "Bénéfices agricoles"
#     definition_period = YEAR
