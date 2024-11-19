from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable
from openfisca_nouvelle_caledonie.entities import Household

from openfisca_core.model_api import select


class TypologieLogement(Enum):
    __order__ = "chambre f1 f2 f3 f4 f5p maisonderetraite"
    chambre = "Chambre"
    f1 = "F1"
    f2 = "F2"
    f3 = "F3"
    f4 = "F4"
    f5p = "F5 et suivants"
    maisonderetraite = "Maison de retraite"


class typologie_logement(Variable):
    value_type = Enum
    possible_values = TypologieLogement
    default_value = TypologieLogement.chambre
    entity = Household
    definition_period = MONTH
    label = "Legal housing situation of the household concerning their main residence"


class loyer(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Loyer de base hors charges"


class charges_locatives(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Charges locatives"


class loyer_mensuel_de_base(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Loyer mensuel de base"

    def formula(household, period, parameters):
        loyer_mensuel_reference = household('loyer_mensuel_reference', period)
        loyer = household('loyer', period)

        # Clarification nécessaire
        # Prise en compte ou non de l'excédent de loyer pour charges importantes ?
        return min(loyer, loyer_mensuel_reference)


class loyer_mensuel_reference(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Loyer mensuel de référence"

    def formula(household, period, parameters):
        typologie_logement = household('typologie_logement', period)
        return  parameters(period).benefits.aide_logement.loyer_mensuel_reference[typologie_logement]


class loyer_mensuel_plafond(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Loyer mensuel de référence"

    def formula(household, period, parameters):
        loyer_mensuel_reference = household('loyer_mensuel_reference', period)
        params = parameters(period).benefits.aide_logement.loyer_mensuel_plafond
        pourcentage_plafond = params.pourcentage

        excedent_pour_charges = params.excedent_pour_charges

        charges = household('charges_locatives', period)
        excedent_pour_charges_montant = max(0, charges - loyer_mensuel_reference * excedent_pour_charges)

        # Clarification nécessaire
        # return loyer_mensuel_reference * (1 + pourcentage_plafond) + excedent_pour_charges_montant
        # OU
        # return (loyer_mensuel_reference + excedent_pour_charges_montant) * (1 + pourcentage_plafond)
        return (loyer_mensuel_reference + excedent_pour_charges_montant) * (1 + pourcentage_plafond)


class aide_logement(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Aide au logement"

    def formula(household, period, parameters):
        loyer = household('loyer', period)
        loyer_mensuel_plafond = household('loyer_mensuel_plafond', period)
        return select([loyer > loyer_mensuel_plafond], [0], default = 1)

