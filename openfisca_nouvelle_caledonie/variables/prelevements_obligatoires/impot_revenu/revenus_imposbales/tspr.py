"""Traitements, alaires, pensions et rentes."""

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


# PENSIONS, RETRAITES ET RENTES À TITRE GRATUIT

# Déclarez lignes PA à PC les sommes perçues en 2024 par chaque membre du
# foyer, notamment :
# - le total net annuel des pensions perçues au titre des retraites publiques ou privées
# territoriales ou étrangères ;
# - les rentes et pensions d’invalidité imposables, servies par les organismes de sé-
# curité sociale ;
# - les rentes viagères à titre gratuit ;
# - les pensions alimentaires ;
# - les rentes versées à titre de prestation compensatoire en cas de divorce (voir
# dépliant d’information pour modalités) ;
# - la contribution aux charges du mariage lorsque son versement résulte d’une dé-
# cision de justice.
# Elles bénéficient d’un abattement de 10 %, plafonné à 550 000 F, qui sera calculé
# automatiquement. Les pensions de source métropolitaine sont exclusivement impo-
# sables en Nouvelle-Calédonie pour les résidents du territoire.
# Sommes à ne pas déclarer :
# - les prestations familiales légales (allocations familiales et complément familial,
# allocations prénatales et de maternité, indemnités en faveur des femmes en
# couches…) ;
# - les salaires perçus dans le cadre d’un contrat d’apprentissage ou d’un contrat
# unique d’alternance ;
# - les salaires perçus dans le cadre du volontariat civil à l’aide technique (VCAT) ;
# - les allocations de chômage en cas de perte d’emploi ;
# - les indemni


class pension_retraite_rente_imposables(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "PA",
        1: "PB",
        2: "PC",
    }
    entity = Individu
    label = "Pensions, retraites et rentes au sens strict imposables (rentes à titre onéreux exclues)"
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


class cotisations_retraite_gerant_cotisant_ruamm(Variable):  # TODO remove me cotisation1
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


class autres_cotisations_gerant_cotisant_ruamm(Variable):  # TODO remove me cotisation2
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


class revenus_categoriels_tspr(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenus catégoriels des traitements, salaires, pensions et rentes"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        # TODO: les abbatement se fontt-ils salaire par salaire ou sur l'enemble du foyer fiscal ?
        salaire_imposable = foyer_fiscal.sum(
            foyer_fiscal.members("salaire_imposable", period)
        )
        frais_professionnels_forfaitaire = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.tspr.deduction_frais_professionnels_forfaitaire
        deduction_forfaitaire = min_(
            max_(
                salaire_imposable * frais_professionnels_forfaitaire.taux,
                frais_professionnels_forfaitaire.minimum,
            ),
            frais_professionnels_forfaitaire.plafond,
        )
        salaire_apres_deduction = max_(salaire_imposable - deduction_forfaitaire, 0)

        pension_imposable = foyer_fiscal.sum(
            foyer_fiscal.members("pension_retraite_rente_imposables", period)
        )
        abattement_pension = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.tspr.abattement_pension
        montant_abattement_pension = min_(
            max_(
                pension_imposable * abattement_pension.taux, abattement_pension.minimum
            ),
            abattement_pension.plafond,
        )
        pension_apres_abattement = max_(
            pension_imposable - montant_abattement_pension, 0
        )

        # TODO: revenus gérant et cotisations

        return salaire_apres_deduction + pension_apres_abattement
