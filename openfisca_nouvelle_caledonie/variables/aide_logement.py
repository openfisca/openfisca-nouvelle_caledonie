from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable
from openfisca_nouvelle_caledonie.entities import Household


class TypologieLogement(Enum):
    __order__ = "chambre f1 f2 f3 f4 f5p maisonderetraite"
    chambre = "Chambre"
    f1 = "F1"
    f2 = "F2"
    f3 = "F3"
    f4 = "F4"
    f5p = "F5 et plus"
    maisonderetraite = "Maison de retraite"


class typologie_logement(Variable):
    value_type = Enum
    possible_values = TypologieLogement
    default_value = TypologieLogement.chambre
    entity = Household
    definition_period = MONTH
    label = "Legal housing situation of the household concerning their main residence"


class aide_logement(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Aide au logement"


class loyer(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Aide au sogement"
