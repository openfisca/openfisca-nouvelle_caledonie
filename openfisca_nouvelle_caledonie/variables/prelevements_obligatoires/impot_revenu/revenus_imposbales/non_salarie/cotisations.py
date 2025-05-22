"""Cotisations sociales communes aux BIC - BA - BNC régime du forfait."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu

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
    label = "Cotisations RUAMM, mutuelle et CSS personnelles de l'exploitant"
    definition_period = YEAR


class cotisations_non_salarie(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Cotisations non salarié"
    definition_period = YEAR

    def formula(individu, period, parameters):
        multiple, plafond_cafat = get_multiple_and_plafond_cafat_cotisation(period, parameters)
        return (
            min_(individu("cotisations_retraite_exploitant", period), multiple * plafond_cafat)
            + individu("cotisations_ruamm_mutuelle_ccs_exploitant", period)
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
                - individu("bic_forfait", period),  # Ne concerne pas les BIC réels
                0,
                )
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
                - individu("bic_forfait", period),
                0,
                )
            )

# Helpers

def get_multiple_and_plafond_cafat_cotisation(period, parameters):
    """Renvoie le plafond de la cotisation CAFAT pour l'année revenus donnée."""

    period_plafond = period.start.offset("first-of", "month").offset(11, "month")
    cafat = parameters(period_plafond).prelevements_obligatoires.prelevements_sociaux.cafat
    cotisations = parameters(period).prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie.cotisations
    if period_plafond.year >= 2023:
        plafond_cafat = cafat.maladie_retraite.plafond # Donc année revenus 2023
        multiple = cotisations.plafond_depuis_ir_2024
    else:
        plafond_cafat = cafat.autres_regimes.plafond
        multiple = cotisations.plafond_avant_ir_2024

    return multiple, plafond_cafat
