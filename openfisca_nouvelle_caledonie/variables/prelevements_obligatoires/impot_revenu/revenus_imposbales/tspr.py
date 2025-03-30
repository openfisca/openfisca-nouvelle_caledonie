from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu

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
    unit = 'currency'
    cerfa_field = {
        0: 'NA',
        1: 'NB',
        2: 'NC',
        }
    entity = Individu
    label = 'Salaires imposables'
    # set_input = set_input_divide_by_period
    definition_period = YEAR


class frais_reels(Variable):
    cerfa_field = {
        0: 'OA',
        1: 'OB',
        2: 'OC',
        }
    value_type = int
    unit = 'currency'
    entity = Individu
    label = 'Frais réels'
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
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'PA',
        1: 'PB',
        2: 'PC',
        }
    entity = Individu
    label = 'Pensions, retraites et rentes au sens strict imposables (rentes à titre onéreux exclues)'
    # set_input = set_input_divide_by_period
    definition_period = YEAR


class gerant_sarl_selarl_sci_cotisant_ruamm(Variable):
    unit = 'currency'
    value_type = bool
    cerfa_field = {
        0: 'NJ',
        1: 'NK',
        2: 'NL',
        }
    entity = Individu
    label = "Gérant de SARL, SELARL ou SCI soumise à l'IS cotisant au RUAMM"
    # set_input = set_input_divide_by_period
    definition_period = YEAR


class cotisations_retraite_gerant_cotisant_ruamm(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'OD',
        1: 'OE',
        2: 'OF',
        }
    entity = Individu
    label = "Cotisations retraite des gérant de SARL, SELARL ou SCI soumise à l'IS cotisant au RUAMM"
    # set_input = set_input_divide_by_period
    definition_period = YEAR


class autres_cotisations_gerant_cotisant_ruamm(Variable):
    unit = 'currency'
    value_type = float
    cerfa_field = {
        0: 'OG',
        1: 'OH',
        2: 'OI',
        }
    entity = Individu
    label = "Cotisations retraite des gérant de SARL, SELARL ou SCI soumise à l'IS cotisant au RUAMM"
    # set_input = set_input_divide_by_period
    definition_period = YEAR
