"""Traitements et salaires."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Person as Individu

# TRAITEMENT, SALAIRES

# Déclarez les sommes perçues en 2024, par chaque membre du foyer, au titre des
# traitements, salaires, vacations, indemnités, congés payés, soldes… lignes NA, NB
# ou NC, selon le cas. II s’agit du salaire net annuel.
# Pour davantage de précisions, un dépliant d’information est à votre disposition dans
# nos locaux ou sur notre site Internet dsf.gouv.nc.
# Vous devez ajouter :
# - les primes d’éloignement ou d’installation (qui peuvent être étalées sur votre de-
# mande sur la période qu’elles couvrent dans la limite de la prescription)
# - les revenus exceptionnels ou différés (sauf si système du quotient) ;
# - certaines indemnités perçues en cas de rupture du contrat de travail (certaines
# d’entre elles sont exonérées) ;
# - les indemnités journalières versées par les organismes de sécurité sociale, à l’ex-
# clusion des indemnités journalières d’accident du travail ou de longue maladie ;
# - les avantages en argent constitués par la prise en charge par l’employeur de
# dépenses personnelles (téléphone…) ;
# - les avantages en nature (uniquement ceux concernant la fourniture d’un logement
# ou d’un véhicule loué ou appartenant à l’employeur).

# Sommes à ne pas déclarer :
# - les prestations familiales légales (allocations familiales et complément familial,
# allocations prénatales et de maternité, indemnités en faveur des femmes en
# couches…) ;
# - les salaires perçus dans le cadre d’un contrat d’apprentissage ou d’un contrat
# unique d’alternance ;
# - les salaires perçus dans le cadre du volontariat civil à l’aide technique (VCAT) ;
# - les allocations de chômage en cas de perte d’emploi ;
# - les indemnités servies aux familles d’accueil dans le cadre de l’aide sociale à
# l’enfance.


class salaire_imposable(Variable):
    value_type = float
    unit = "currency"
    cerfa_field = {
        0: "NA",
        1: "NB",
        2: "NC",
    }
    entity = Individu
    label = "Salaires imposables"
    definition_period = YEAR


class salaire_percu(Variable):
    value_type = float
    unit = "currency"
    entity = Individu
    label = "Salaire perçu"
    definition_period = YEAR

    def formula(individu, period):
        return max_(individu("salaire_imposable", period), 0)  # TODO: add NM, NN, NO


class frais_reels(Variable):
    cerfa_field = {
        0: "OA",
        1: "OB",
        2: "OC",
    }
    value_type = int
    unit = "currency"
    entity = Individu
    label = "Frais réels"
    definition_period = YEAR


class gerant_sarl_selarl_sci_cotisant_ruamm(Variable):
    unit = "currency"
    value_type = bool
    cerfa_field = {
        0: "NJ",
        1: "NK",
        2: "NL",
    }
    entity = Individu
    label = "Gérant de SARL, SELARL ou SCI soumise à l'IS cotisant au RUAMM"
    definition_period = YEAR


class cotisations_retraite_gerant_cotisant_ruamm(
    Variable
):  # TODO: remove me cotisation1
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "OD",
        1: "OE",
        2: "OF",
    }
    entity = Individu
    label = "Cotisations retraite des gérant de SARL, SELARL ou SCI soumise à l'IS cotisant au RUAMM"
    definition_period = YEAR


class autres_cotisations_gerant_cotisant_ruamm(Variable):  # TODO: remove me cotisation2
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "OG",
        1: "OH",
        2: "OI",
    }
    entity = Individu
    label = "Cotisations retraite des gérant de SARL, SELARL ou SCI soumise à l'IS cotisant au RUAMM"
    definition_period = YEAR


class cotisations(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    definition_period = YEAR
    label = "Cotisations"

    def formula_2022(individu, period, parameters):
        # TODO: voir https://github.com/openfisca/openfisca-nouvelle_caledonie/issues/7
        # Lp.123 du code des impôts de la NC :

        # II - Le total des versements aux organismes de retraites au titre des cotisations d’assurance vieillesse
        # souscrites à titre obligatoire ou volontaire, sont déductibles dans la limite de sept fois le montant du salaire
        # plafond de la caisse de compensation des prestations familiales, des accidents du travail et de prévoyance des
        # travailleurs (C.A.F.A.T.), relatif à la retraitel du mois de novembre de l'année de réalisation des revenus ,
        # l’excédent est réintégré au bénéfice imposable. Cette limite s'apprécie par personne, quel que soit le nombre
        # de revenus catégoriels dont elle est titulaire.
        cotisations_retraite_gerant_cotisant_ruamm = individu(
            "cotisations_retraite_gerant_cotisant_ruamm", period
        )
        autres_cotisations_gerant_cotisant_ruamm = individu(
            "autres_cotisations_gerant_cotisant_ruamm", period
        )
        period_plafond = period.start.offset("first-of", "month").offset(11, "month")
        plafond_cafat_retraite = parameters(
            period_plafond
        ).prelevements_obligatoires.prelevements_sociaux.cafat.maladie_retraite.plafond
        return (
            min_(cotisations_retraite_gerant_cotisant_ruamm, 7 * plafond_cafat_retraite)
            + autres_cotisations_gerant_cotisant_ruamm
        )


class salaire_imposable_apres_deduction_et_abattement(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Salaire imposable après déduction et abattement"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        # salaires_percus - retenue_cotisations - deduction_salaires - abattement_salaires

        tspr = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.tspr

        salaire_percu_net_de_cotisation = max_(
            foyer_fiscal.members("salaire_percu", period)
            - foyer_fiscal.members("cotisations", period),
            0,
        )

        frais_professionnels_forfaitaire = (
            tspr.deduction_frais_professionnels_forfaitaire
        )  # 10%
        deduction_forfaitaire = min_(
            max_(
                salaire_percu_net_de_cotisation * frais_professionnels_forfaitaire.taux,
                frais_professionnels_forfaitaire.minimum,
            ),
            frais_professionnels_forfaitaire.plafond,
        )
        salaire_apres_deduction = max_(
            salaire_percu_net_de_cotisation - deduction_forfaitaire, 0
        )

        return foyer_fiscal.sum(
            max_(
                (
                    salaire_apres_deduction
                    - min_(
                        salaire_apres_deduction * tspr.abattement.taux,
                        tspr.abattement.plafond,
                    )
                ),
                0,
            )
        )


# Revenus de la déclaration complémentaire

# Revenus différés salaires et pensions (Cadre 9)


class salaires_imposes_selon_le_quotient(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "ND",
        1: "NE",
    }
    entity = Individu
    label = "Salaires imposés selon le quotient"
    definition_period = YEAR


class annees_de_rappel_salaires(Variable):
    value_type = int
    cerfa_field = {
        0: "NG",
        1: "NH",
    }
    entity = Individu
    label = "Années de rappel pour les salaires imposés selon le quotient"
    definition_period = YEAR


class indemnites_elus_municipaux(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "NP",
        1: "NQ",
        2: "NR",
    }
    entity = Individu
    label = "Indemnités des élus municipaux"
    definition_period = YEAR


class indemnites(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Indemnités"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        # TODO: Calculer l'abattement sur les indemnités des élus municipaux
        # 20 % de l'indemnité brute dans la limote du reste de l'abattement sur salaire
        return foyer_fiscal.sum(
            foyer_fiscal.members("indemnites_elus_municipaux", period)
        )
