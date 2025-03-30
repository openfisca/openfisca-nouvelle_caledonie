class TypesStatutMarital(Enum):
    __order__ = 'non_renseigne marie pacse celibataire divorce veuf'  # Needed to preserve the enum order in Python 2
    non_renseigne = 'Non renseigné'
    marie = 'Marié'
    pacse = 'Pacsé'
    celibataire = 'Célibataire'
    divorce = 'Divorcé'
    separe = 'Séparé'
    veuf = 'Veuf'
