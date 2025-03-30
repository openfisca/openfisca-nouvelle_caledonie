from openfisca_core.model_api import Enum


class TypesStatutMarital(Enum):
    __order__ = "non_renseigne marie pacse celibataire divorce separe veuf"  # Needed to preserve the enum order in Python 2
    non_renseigne = "Non renseigné"
    marie = "Marié"
    pacse = "Pacsé"
    celibataire = "Célibataire"
    divorce = "Divorcé"
    separe = "Séparé"
    veuf = "Veuf"
