"""Revenus des capitaux mobiliers."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal

# Contribuables fiscalement domiciliés en Nouvelle-Calédonie :
# • Vous devez inscrire ligne BA le montant brut des produits ou intérêts :
# - de prêts, titres de créances négociables, cautionnements, comptes courants (uni-
# quement pour la partie supérieure au taux de l’intérêt légal) ;
# - de contrats de capitalisation (principalement assurance-vie) lorsque la durée de
# détention est inférieure à 8 ans.


class produits_pret_contrat_de_capitalisation(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "BA"
    entity = FoyerFiscal
    label = "Produits de prêts, titres de créances négociables, cautionnements et contrats de capitalisation"
    definition_period = YEAR


# Lorsque l’impôt sur le revenu des créances, dépôts et cautionnements (IRCDC), a
# été prélevé sur des revenus déclarés, reportez son montant ligne YA.


class ircdc(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "YA"
    entity = FoyerFiscal
    label = "Impôt sur le revenu des créances, dépôts et cautionnements (IRCDC) prélevé sur les revenus déclarés"
    definition_period = YEAR


# • Vous devez inscrire ligne CA le montant brut :
# - des jetons de présence (à l’exception de ceux versés par une société métropo-
# litaine) ;
# - des produits des bons de caisse, des obligations et des emprunts de toute
# nature ;
# - des revenus d’actions étrangères ;
# - des revenus de sociétés civiles de portefeuille ou de parts de sociétés dont le
# prélèvement d’IRVM n’est pas libératoire.

# Doit être inférieur à .08 * produits_pret_contrat_de_capitalisation


class ircdc_impute(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Impôt sur le revenu des créances, dépôts et cautionnements (IRCDC) prélevé sur les revenus déclarés imputé"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return min_(
            foyer_fiscal("ircdc", period),
            0.08 * foyer_fiscal("produits_pret_contrat_de_capitalisation", period),
        )


class revenus_obligations_actions_jetons_de_presence(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "CA"
    entity = FoyerFiscal
    label = "Jetons de présence"
    definition_period = YEAR


# Lorsque l’impôt sur le revenu des valeurs mobilières (IRVM) a été prélevé sur les
# revenus déclarés, reportez son montant ligne YB.


class irvm(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "YB"
    entity = FoyerFiscal
    label = "Impôt sur le revenu des valeurs mobilières (IRVM) prélevé sur les revenus déclarés"
    definition_period = YEAR


class irvm_impute(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Impôt sur le revenu des valeurs mobilières (IRVM) prélevé sur les revenus déclarés"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return min_(
            foyer_fiscal("irvm", period),
            0.16
            * foyer_fiscal("revenus_obligations_actions_jetons_de_presence", period),
        )


# • Vous devez inscrire ligne DA le montant brut des revenus d’actions et de parts de
# sociétés métropolitaines.
# TODO: ajouter les paramètres
# Doit être inférieur à .16 * revenus_obligations_actions_jetons_de_presence à partir des revenus 2014 / IR 2015
# Mais inférieur à .125 * produits_pret_contrat_de_capitalisation à partir des revenus 2007 / IR 2008


class revenus_actions_metropolitaines(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "DA"
    entity = FoyerFiscal
    label = "Revenus d'actions et de parts de sociétés métropolitaines"
    definition_period = YEAR


class retenue_a_la_source_metropole(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "YC"
    entity = FoyerFiscal
    label = "Retenue à la source pratiquée en métropole sur les revenus d'actions et de parts de sociétés métropolitaines"
    definition_period = YEAR


#  La retenue à la source pratiquée en métropole doit être inscrite ligne YC, celle-ci sera automatiquement plafonnée à 15 % de la somme ligne DA.
class retenue_a_la_source_metropole_imputee(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Retenue à la source pratiquée en métropole sur les revenus d'actions et de parts de sociétés métropolitaines imputée"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return min_(
            foyer_fiscal("retenue_a_la_source_metropole", period),
            0.15 * foyer_fiscal("revenus_actions_metropolitaines", period),
        )


# • Droits de garde ligne DD : Il s’agit des frais prélevés par l’intermédiaire financier
# pour la tenue des comptes titres. Ils sont déductibles de vos revenus d’actions.
# Contribuables fiscalement domiciliés hors de la Nouvelle-Calédonie :


class droits_de_garde(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "DD"
    entity = FoyerFiscal
    label = "Droits de garde prélevés par l'intermédiaire financier pour la tenue des comptes titres"
    definition_period = YEAR


# • Indiquez ligne BB, le montant des intérêts de dépôts de sommes d’argent servis
# par les établissements bancaires ou financiers exerçant en Nouvelle-Calédonie
# et de comptes courants d’associés dans les sociétés passibles de l’IS (le taux
# d’imposition est fixé à 8 % au lieu de 25 %).


class interets_de_depots(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "BB"
    entity = FoyerFiscal
    label = "Intérêts de dépôts de sommes d'argent servis par les établissements bancaires ou financiers exerçant en Nouvelle-Calédonie et de comptes courants d'associés dans les sociétés passibles de l'IS"
    definition_period = YEAR


# • Indiquez ligne BA, le montant des autres revenus de créances, dépôts et cau-
# tionnements et comptes courants de source calédonienne (le taux d’imposition
# est fixé à 25 %).
# • Indiquez ligne CA, le montant brut des jetons de présence de source calédo-
# nienne. L’impôt sur le revenu des valeurs mobilières (IRVM) qui a été prélevé est à
# reporter ligne YB, hors Contribution Calédonienne de Solidarité (CCS).
# Sommes à ne pas déclarer :
# - les intérêts de dépôts de sommes d’argent servis par les établissements ban-
# caires et financiers de Nouvelle-Calédonie aux contribuables fiscalement domi-
# ciliés en Nouvelle-Calédonie et soumis à l’IRCDC ;
# - les intérêts rémunérant des comptes courants d’associés dans les sociétés rele-
# vant de l’impôt sur les sociétés et ayant leur siège en Nouvelle-Calédonie dans
# la limite du taux légal et soumis à l’IRCDC (uniquement pour les résidents) ;
# - les dividendes issus de distributions régulières faites par des sociétés ayant leur
# siège en Nouvelle-Calédonie et soumis à l’IRVM ;
# - les produits ou contrats de capitalisation au moment de leur dénouement
# lorsque la durée de détention du produit excède 8 ans.


class revenu_categoriel_capital(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Revenus catégoriels de capitaux mobiliers"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        resident = foyer_fiscal("resident", period)
        rcm_resident = max_(
            (
                +foyer_fiscal("revenus_obligations_actions_jetons_de_presence", period)
                + foyer_fiscal("revenus_actions_metropolitaines", period)
                - foyer_fiscal("droits_de_garde", period)
            ),
            0,
        ) + foyer_fiscal("produits_pret_contrat_de_capitalisation", period)

        rcm_non_resident = max_(
            (
                +foyer_fiscal("revenus_obligations_actions_jetons_de_presence", period)
                - foyer_fiscal("droits_de_garde", period)
            ),
            0,
        ) + (
            foyer_fiscal("produits_pret_contrat_de_capitalisation", period)
            + foyer_fiscal("interets_de_depots", period)
        )

        return where(resident, rcm_resident, rcm_non_resident)
