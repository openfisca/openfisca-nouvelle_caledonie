"""Traitements, alaires, pensions et rentes."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class revenus_categoriels_tspr(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenus catégoriels des traitements, salaires, pensions et rentes"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        salaire_imposable_apres_deduction_et_abattement = foyer_fiscal.sum(
            foyer_fiscal.members(
                "salaire_imposable_apres_deduction_et_abattement", period
            )
        )
        indemnites = foyer_fiscal("indemnites", period)
        pension_imposable_apres_deduction_et_abattement = foyer_fiscal(
            "pension_imposable_apres_deduction_et_abattement", period
        )
        rentes_viageres_a_titre_onereux = foyer_fiscal(
            "rentes_viageres_a_titre_onereux", period
        )
        return (
            salaire_imposable_apres_deduction_et_abattement
            + indemnites
            + pension_imposable_apres_deduction_et_abattement
            + rentes_viageres_a_titre_onereux
        )


class revenus_bruts_salaires_pensions(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenus bruts salaires et pensions"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            foyer_fiscal.members("salaire_percu", period)
            + foyer_fiscal.members("pension_retraite_rente_imposables", period)
            + foyer_fiscal.members(
                "rentes_viageres_a_titre_onereux_moins_de_50_ans", period
            )
            + foyer_fiscal.members("rentes_viageres_a_titre_onereux_50_59_ans", period)
            + foyer_fiscal.members("rentes_viageres_a_titre_onereux_60_69_ans", period)
            + foyer_fiscal.members(
                "rentes_viageres_a_titre_onereux_plus_de_69_ans", period
            )
            + foyer_fiscal.members("indemnites_elus_municipaux", period)
        )
