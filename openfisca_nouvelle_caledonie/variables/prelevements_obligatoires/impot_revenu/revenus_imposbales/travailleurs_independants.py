from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu


# BÉNÉFICES AGRICOLES (BA)

class chiffre_d_daffaires_agricole_ht_imposable(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'GA',
        1: 'GB',
        2: 'GC',
        }
    entity = Individu
    label = "Chiffre d’affaires hors taxes tiré des exploitations agricoles imposables"
    definition_period = YEAR
    # Le bénéfice, égal à 1/6 e de ce chiffre d’affaires sera déterminé automatiquement.


class chiffre_d_daffaires_agricole_ht_exonere(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'GD',
        1: 'GE',
        2: 'GF',
        }
    entity = Individu
    label = "Chiffre d’affaires hors taxes tiré des exploitations agricoles exonérées en vertu d’un bail rural"
    definition_period = YEAR


class ba(Variable):
    unit = 'currency'
    value_type = float
    entity = Individu
    label = "Bénéfices agricoles"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        # Le bénéfice, égal à 1/6 e de ce chiffre d’affaires sera déterminé automatiquement.
        return (
            foyer_fiscal("chiffre_d_daffaires_agricole_ht_imposable", period)
            + foyer_fiscal("chiffre_d_daffaires_agricole_ht_exonere", period)
            ) / 6


# BÉNÉFICES INDUSTRIELS ET COMMERCIAUX (BIC)



# BÉNÉFICES NON COMMERCIAUX (BNC)

class bnc_recettes_ht(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'HA',
        1: 'HB',
        2: 'HC',
        }
    entity = Individu
    label = "Recettes annuelles des bénéfices non-commerciaux"
    definition_period = YEAR


#  COTISATIONS SOCIALES COMMUNES AUX BIC - BA - BNC RÉGIME DU FORFAIT

# • Indiquez lignes QA, QB, QC vos cotisations de retraite (en tant que chef d’entre-
# prise) dans la limite du plafond, soit 3 776 500 F.
# • Indiquez lignes QD, QE, QF le montant total de vos cotisations sociales person-
# nelles (autres que de retraite) versées au RUAMM, aux mutuelles et CCS.
# • Indiquez ligne XY le montant total de vos autres cotisations sociales volontaires.
# Pour davantage de précisions, un dépliant d’information est à votre disposition dans
# nos locaux ou sur notre site dsf.gouv.nc.

class cotisations_retraite_exploitant(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'QA',
        1: 'QB',
        2: 'QC',
        }
    entity = Individu
    label = "Cotisations retraite personnelles de l'exploitant"
    definition_period = YEAR


class cotisations_ruamm_mutuelle_ccs_exploitant(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'QD',
        1: 'QE',
        2: 'QF',
        }
    entity = Individu
    label = "Cotisations RUAMM, mutuelle et CSS personnelles de l'exploitant"
    definition_period = YEAR
