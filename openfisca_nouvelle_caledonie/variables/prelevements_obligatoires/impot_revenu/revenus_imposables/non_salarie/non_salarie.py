"""Revenus des non-salariés."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class revenu_categoriel_non_salarie(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenus catégoriels non salariés"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            foyer_fiscal.members("bic", period)
            + foyer_fiscal.members("ba", period)
            + foyer_fiscal.members("bnc", period)
        )  # Ajouter régime réel à BA
