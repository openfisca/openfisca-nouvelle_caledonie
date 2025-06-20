"""Rentes viagères à titre onéreux."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Individu


class rentes_viageres_a_titre_onereux_moins_de_50_ans(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "RA",
        1: "RB",
    }
    entity = Individu
    label = (
        "Rentes viagères à titre onéreux ; âge d'entrée en jouissance : moins de 50 ans"
    )
    definition_period = YEAR


class rentes_viageres_a_titre_onereux_50_59_ans(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "SA",
        1: "SB",
    }
    entity = Individu
    label = "Rentes viagères à titre onéreux ; âge d'entrée en jouissance : 50 à 59 ans"
    definition_period = YEAR


class rentes_viageres_a_titre_onereux_60_69_ans(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "TA",
        1: "TB",
    }
    entity = Individu
    label = "Rentes viagères à titre onéreux ; âge d'entrée en jouissance : 60 à 69 ans"
    definition_period = YEAR


class rentes_viageres_a_titre_onereux_plus_de_69_ans(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "UA",
        1: "UB",
    }
    entity = Individu
    label = (
        "Rentes viagères à titre onéreux ; âge d'entrée en jouissance : plus de 69 ans"
    )
    definition_period = YEAR


class rentes_viageres_a_titre_onereux(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Rentes viagères à titre onéreux"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        rentes_viageres_a_titre_onereux_moins_de_50_ans = foyer_fiscal.members(
            "rentes_viageres_a_titre_onereux_moins_de_50_ans", period
        )
        rentes_viageres_a_titre_onereux_50_59_ans = foyer_fiscal.members(
            "rentes_viageres_a_titre_onereux_50_59_ans", period
        )
        rentes_viageres_a_titre_onereux_60_69_ans = foyer_fiscal.members(
            "rentes_viageres_a_titre_onereux_60_69_ans", period
        )
        rentes_viageres_a_titre_onereux_plus_de_69_ans = foyer_fiscal.members(
            "rentes_viageres_a_titre_onereux_plus_de_69_ans", period
        )

        rto = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.tspr.rto

        return foyer_fiscal.sum(
            rentes_viageres_a_titre_onereux_moins_de_50_ans * rto.taux_moins_de_50
            + rentes_viageres_a_titre_onereux_50_59_ans * rto.taux_50_59
            + rentes_viageres_a_titre_onereux_60_69_ans * rto.taux_60_69
            + rentes_viageres_a_titre_onereux_plus_de_69_ans * rto.taux_plus_de_69
        )
