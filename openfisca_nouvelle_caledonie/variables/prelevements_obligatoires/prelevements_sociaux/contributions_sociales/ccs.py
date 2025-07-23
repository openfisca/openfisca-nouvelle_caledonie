"""Contribution calédonienne de solidarité (CCS)."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Individu


class ccs(Variable):
    value_type = float
    entity = Individu
    label = "Contribution calédonienne de soliarité"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2015(individu, period, parameters):
        ccs = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.contribution_caledonienne_solidarite
        revenus_d_activite = individu("salaire_de_base", period)
        revenus_de_remplacement = (
            individu.empty_array()
        )  # TODO: Implement this variable
        revenus_epargne_patrimoine = individu.empty_array()  # TODO: A implémenter si besoin mais cela semble prélevé en même temps que l'IR
        return (
            ccs.activite.calc(revenus_d_activite)
            + ccs.remplacement.calc(revenus_de_remplacement)
            + ccs.epargne_patrimoine.calc(revenus_epargne_patrimoine)
        )


class ccs_revenu_du_capital_base(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Base de la contribution calédonienne de solidarité sur les revenus capital issus de la déclaration de l'impôt sur le revenu"
    definition_period = YEAR

    def formula_2015(foyer_fiscal, period):
        revenus_fonciers_soumis_ccs = foyer_fiscal(
            "revenus_fonciers_soumis_ccs", period
        )
        rentes_viageres_a_titre_onereux = foyer_fiscal(
            "rentes_viageres_a_titre_onereux", period
        )
        plus_values = foyer_fiscal.sum(
            foyer_fiscal.members("plus_values_professionnelles_a_taux_reduit", period)
            + foyer_fiscal.members("plus_values_professionnelles_a_taux_normal", period)
        )
        return (
            revenus_fonciers_soumis_ccs + rentes_viageres_a_titre_onereux + plus_values
        )


class ccs_revenu_du_capital(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Contribution calédonienne de solidarité sur les revenus capital"
    definition_period = YEAR

    def formula_2015(foyer_fiscal, period, parameters):
        ccs = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.contribution_caledonienne_solidarite.epargne_patrimoine
        ccs_revenu_du_capital_base = foyer_fiscal("ccs_revenu_du_capital_base", period)
        return ccs.calc(ccs_revenu_du_capital_base)
