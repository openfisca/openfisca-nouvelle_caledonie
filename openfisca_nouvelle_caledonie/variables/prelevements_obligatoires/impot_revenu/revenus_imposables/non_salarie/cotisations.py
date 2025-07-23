"""Cotisations sociales communes aux BIC - BA - BNC régime du forfait."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie import (
    get_multiple_and_plafond_cafat_cotisation,
)

# • Indiquez lignes QA, QB, QC vos cotisations de retraite (en tant que chef d’entre-
# prise) dans la limite du plafond, soit 3 776 500 F.
# • Indiquez lignes QD, QE, QF le montant total de vos cotisations sociales person-
# nelles (autres que de retraite) versées au RUAMM, aux mutuelles et CCS.
# • Indiquez ligne XY le montant total de vos autres cotisations sociales volontaires.
# Pour davantage de précisions, un dépliant d’information est à votre disposition dans
# nos locaux ou sur notre site dsf.gouv.nc.


class cotisations_retraite_exploitant(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "QA",
        1: "QB",
        2: "QC",
    }
    entity = Individu
    label = "Cotisations retraite personnelles de l'exploitant"
    definition_period = YEAR


class cotisations_ruamm_mutuelle_ccs_exploitant(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "QD",
        1: "QE",
        2: "QF",
    }
    entity = Individu
    label = "Cotisations RUAMM, mutuelle et CCS personnelles de l'exploitant"
    definition_period = YEAR


class cotisations_non_salarie(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Cotisations non salarié"
    definition_period = YEAR

    def formula(individu, period, parameters):
        multiple, plafond_cafat = get_multiple_and_plafond_cafat_cotisation(
            period, parameters
        )
        return max_(
            (
                min_(
                    individu("cotisations_retraite_exploitant", period),
                    multiple * plafond_cafat,
                )
                + individu("cotisations_ruamm_mutuelle_ccs_exploitant", period)
            ),
            0,
        )


class reste_cotisations_apres_bic_avant_ba(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Reste des cotisations après BIC avant BA et BNC"
    definition_period = YEAR

    def formula(individu, period):
        return max_(
            (
                individu("cotisations_non_salarie", period)
                - individu("bic_forfait", period)  # Ne concerne pas les BIC réels
            ),
            0,
        )


class reste_cotisations_apres_bic_ba_avant_bnc(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Reste des cotisations après BIC et BA et avant BNC"
    definition_period = YEAR

    def formula(individu, period):
        return max_(
            (
                individu("reste_cotisations_apres_bic_avant_ba", period)
                - individu("bic_forfait", period)  # Ne concerne pas les BIC forfait
            ),
            0,
        )


class reste_cotisations_apres_bic_ba_bnc(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Reste des cotisations après BIC et BA et avant BNC"
    definition_period = YEAR

    def formula(individu, period):
        return max_(
            (
                individu("reste_cotisations_apres_bic_avant_ba", period)
                - individu("bnc", period)  # Concerne tous les BNC
            ),
            0,
        )
