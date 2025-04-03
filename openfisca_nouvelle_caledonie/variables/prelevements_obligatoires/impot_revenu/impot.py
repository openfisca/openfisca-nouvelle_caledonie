"""Calcul de l'impôt sur le revenu."""


from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class revenus_categoriels(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenus catégoriels"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        rev_cat_tspr = foyer_fiscal("revenu_categoriel_tspr", period)
        rev_cat_rvcm = foyer_fiscal("revenu_categoriel_capital", period)
        rev_cat_rfon = foyer_fiscal("revenu_categoriel_foncier", period)
        rev_cat_rpns = foyer_fiscal("revenu_categoriel_non_salarial", period)
        rev_cat_pv = foyer_fiscal("revenu_categoriel_plus_values", period)

        return rev_cat_tspr + rev_cat_rvcm + rev_cat_rfon + rev_cat_rpns + rev_cat_pv
