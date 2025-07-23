"""Entités du système socio-fiscal de Nouvelle Calédonie."""

from openfisca_core.entities import build_entity

Menage = build_entity(
    key="menage",
    plural="menages",
    label="All the people in a family or group who live together in the same place.",
    doc="""
    Menage is an example of a group entity.
    A group entity contains one or more individual·s.
    Each individual in a group entity has a role (e.g. parent or children).
    Some roles can only be held by a limited number of individuals (e.g. a
    'first_parent' can only be held by one individual), while others can
    have an unlimited number of individuals (e.g. 'children').

    Example:
        Housing variables (e.g. housing_tax') are usually defined for a group
        entity such as 'Menage'.

    Usage:
        Check the number of individuals of a specific role (e.g. check if there
        is a 'second_parent' with menage.nb_persons(Menage.SECOND_PARENT)).
        Calculate a variable applied to each individual of the group entity
        (e.g. calculate the 'salary' of each member of the 'Menage' with:
            salaries = menage.members("salary", period = MONTH)
            sum_salaries = menage.sum(salaries)).

    For more information, see: https://openfisca.org/doc/coding-the-legislation/50_entities.html
    """,
    roles=[
        {
            "key": "parent",
            "plural": "parents",
            "label": "Parents",
            "max": 2,
            "subroles": ["first_parent", "second_parent"],
            "doc": "The one or two adults in charge of the menage.",
        },
        {
            "key": "child",
            "plural": "children",
            "label": "Child",
            "doc": "Other individuals living in the menage.",
        },
    ],
)

Individu = build_entity(
    key="individu",
    plural="individus",
    label="An individual. The minimal entity on which legislation can be applied.",
    doc="""
    Variables like 'salary' and 'income_tax' are usually defined for the entity
    'Individu'.

    Usage:
        Calculate a variable applied to a 'Individu' (e.g. access the 'salary' of
        a specific month with individu("salary", "2017-05")).
        Check the role of a 'Individu' in a group entity (e.g. check if a the
        'Individu' is a 'first_parent' in a 'Menage' entity with
        person.has_role(Menage.FIRST_PARENT)).

    For more information, see: https://openfisca.org/doc/coding-the-legislation/50_entities.html
    """,
    is_person=True,
)


FoyerFiscal = build_entity(
    key="foyer_fiscal",
    plural="foyers_fiscaux",
    label="Déclaration d’impôts",
    doc="""
    Le foyer fiscal désigne l'ensemble des personnes inscrites sur une même déclaration de revenus.
    Il peut y avoir plusieurs foyers fiscaux dans un seul ménage : par exemple, un couple non marié où chacun remplit
    sa propre déclaration de revenus compte pour deux foyers fiscaux.
    """,
    roles=[
        {
            "key": "declarant",
            "plural": "declarants",
            "label": "Déclarants",
            "subroles": ["declarant_principal", "conjoint"],
        },
        {
            "key": "enfant_a_charge",
            "plural": "enfants_a_charge",
            "label": "Enfants à charge",
        },
        {
            "key": "ascendant_a_charge",
            "plural": "ascendants_a_charge",
            "label": "Ascendants à charge",
        },
        {
            "key": "enfant_accueilli",
            "plural": "enfants_accueillis",
            "label": "Enfants accueillis",
        },
    ],
)


entities = [FoyerFiscal, Menage, Individu]
