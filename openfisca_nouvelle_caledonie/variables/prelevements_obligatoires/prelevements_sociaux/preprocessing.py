"""Preprocessing of the legislation parameters for cotisations sociales in Nouvelle-Calédonie."""

import logging

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.salarie import (
    TypesCategorieSalarie,
)

log = logging.getLogger(__name__)


def build_cotisations_employeur(parameters):
    """Construit le dictionnaire de barèmes des cotisations employeur à partir des paramètres de parameters."""
    # TODO: contribution patronale de prévoyance complémentaire
    cotisations_employeur = ParameterNode(
        "cotisations_employeur", data={"description": "Cotisations sociales employeur"}
    )  # Génère cotisations_employeur

    # Raccourcis
    prelevements_sociaux = parameters.prelevements_obligatoires.prelevements_sociaux
    cafat = prelevements_sociaux.cafat
    chomage = cafat.autres_regimes.chomage
    prestations_familiales = cafat.autres_regimes.prestations_familiales
    fds = cafat.fds
    fiaf = cafat.fiaf
    fsh = prelevements_sociaux.fsh
    retraite = cafat.maladie_retraite.retraite
    ruamm = cafat.maladie_retraite.ruamm
    retraite_complementaire = (
        prelevements_sociaux.regimes_complementaires_retraite_secteur_prive
    )

    # TODO: Peut-être créer une base communn après avoir un type qui fonctionne (voir France pour exemple)

    # Initialisation Cadre
    prive_cadre = ParameterNode(
        "prive_cadre",
        data={
            "description": "Cotisations employeur pour salarié cadre",
            "metadata": {"order": []},
        },
    )
    cotisations_employeur.add_child("prive_cadre", prive_cadre)

    cotisations_employeur.children["prive_cadre"].add_child(
        "chomage", chomage.employeur
    )
    cotisations_employeur.children["prive_cadre"].add_child("fds", fds.employeur)
    cotisations_employeur.children["prive_cadre"].add_child("fiaf", fiaf.employeur)
    cotisations_employeur.children["prive_cadre"].add_child("fsh", fsh.employeur)
    cotisations_employeur.children["prive_cadre"].add_child(
        "prestations_familiales", prestations_familiales.employeur
    )
    cotisations_employeur.children["prive_cadre"].add_child(
        "retraite", retraite.employeur
    )
    cotisations_employeur.children["prive_cadre"].add_child("ruamm", ruamm.employeur)

    # cotisations_employeur.children['prive_cadre'].metadata['order'] += commun.metadata['order']

    keys_retraite_complementaire = [
        retraite_complementaire.agff.employeur.cadre,
        retraite_complementaire.arrco.taux_effectifs_salaries_employeurs.employeur.cadre,
        retraite_complementaire.agirc.taux_effectifs_salaries_employeurs.avant81.employeur,
        retraite_complementaire.ceg.employeur,
        retraite_complementaire.cet2019.employeur,
        retraite_complementaire.agirc_arrco.employeur,
        retraite_complementaire.cet.employeur,
    ]
    for key in keys_retraite_complementaire:
        cotisations_employeur.children["prive_cadre"].children.update(key.children)

    # Initialisation Non Cadre
    prive_non_cadre = ParameterNode(
        "prive_non_cadre",
        data={
            "description": "Cotisations employeur pour salarié non cadre",
            "metadata": {"order": []},
        },
    )

    cotisations_employeur.add_child("prive_non_cadre", prive_non_cadre)

    cotisations_employeur.children["prive_non_cadre"].add_child(
        "chomage", chomage.employeur
    )
    cotisations_employeur.children["prive_non_cadre"].add_child("fds", fds.employeur)
    cotisations_employeur.children["prive_non_cadre"].add_child("fiaf", fiaf.employeur)
    cotisations_employeur.children["prive_non_cadre"].add_child("fsh", fsh.employeur)
    cotisations_employeur.children["prive_non_cadre"].add_child(
        "prestations_familiales", prestations_familiales.employeur
    )
    cotisations_employeur.children["prive_non_cadre"].add_child(
        "retraite", retraite.employeur
    )
    cotisations_employeur.children["prive_non_cadre"].add_child(
        "ruamm", ruamm.employeur
    )

    keys_retraite_complementaire = [
        retraite_complementaire.agff.employeur.noncadre,
        retraite_complementaire.arrco.taux_effectifs_salaries_employeurs.employeur.noncadre,
        retraite_complementaire.ceg.employeur,
        retraite_complementaire.cet2019.employeur,
        retraite_complementaire.agirc_arrco.employeur,
    ]
    for key in keys_retraite_complementaire:
        cotisations_employeur.children["prive_non_cadre"].children.update(key.children)

    return cotisations_employeur


def build_cotisations_salarie(parameters):
    """Construit le dictionnaire de barèmes des cotisations salariales."""
    cotisations_salarie = ParameterNode(
        "cotisations_salarie", data={"description": "Cotisations sociales salariales"}
    )  # Génère cotisations_salarie

    prelevements_sociaux = parameters.prelevements_obligatoires.prelevements_sociaux
    cafat = prelevements_sociaux.cafat
    chomage = cafat.autres_regimes.chomage
    retraite = cafat.maladie_retraite.retraite
    ruamm = cafat.maladie_retraite.ruamm
    retraite_complementaire = (
        prelevements_sociaux.regimes_complementaires_retraite_secteur_prive
    )

    # TODO: Peut-être créer une base communn après avoir un type qui fonctionne (voir France pour exemple)

    # Cadre
    prive_cadre = ParameterNode(
        "prive_cadre",
        data={
            "description": "Cotisations salariales pour salarié cadre",
            "metadata": {"order": []},
        },
    )
    cotisations_salarie.add_child("prive_cadre", prive_cadre)

    cotisations_salarie.children["prive_cadre"].add_child("chomage", chomage.salarie)
    cotisations_salarie.children["prive_cadre"].add_child("retraite", retraite.salarie)
    cotisations_salarie.children["prive_cadre"].add_child("ruamm", ruamm.salarie)

    keys_retraite_complementaire = [
        retraite_complementaire.agff.salarie.cadre,
        retraite_complementaire.arrco.taux_effectifs_salaries_employeurs.salarie.cadre,
        retraite_complementaire.agirc.taux_effectifs_salaries_employeurs.avant81.salarie,
        retraite_complementaire.ceg.salarie,
        retraite_complementaire.cet2019.salarie,
        retraite_complementaire.cet.salarie,
        retraite_complementaire.agirc_arrco.salarie,
    ]
    for key in keys_retraite_complementaire:
        cotisations_salarie.children["prive_cadre"].children.update(key.children)

    # Non Cadre
    # Initialisation
    prive_non_cadre = ParameterNode(
        "prive_non_cadre",
        data={
            "description": "Cotisations salariales pour salarié non cadre",
            "metadata": {"order": []},
        },
    )

    cotisations_salarie.add_child("prive_non_cadre", prive_non_cadre)

    cotisations_salarie.children["prive_non_cadre"].add_child(
        "chomage", chomage.salarie
    )
    cotisations_salarie.children["prive_non_cadre"].add_child(
        "retraite", retraite.salarie
    )
    cotisations_salarie.children["prive_non_cadre"].add_child("ruamm", ruamm.salarie)

    keys_retraite_complementaire = [
        retraite_complementaire.agff.salarie.cadre,
        retraite_complementaire.arrco.taux_effectifs_salaries_employeurs.salarie.noncadre,
        retraite_complementaire.ceg.salarie,
        retraite_complementaire.cet2019.salarie,
        retraite_complementaire.agirc_arrco.salarie,
    ]
    for key in keys_retraite_complementaire:
        cotisations_salarie.children["prive_non_cadre"].children.update(key.children)

    return cotisations_salarie


def preprocess_parameters(parameters):
    """Preprocess the legislation parameters to build the cotisations sociales taxscales (barèmes)."""
    cotisations_employeur = build_cotisations_employeur(parameters)
    cotisations_salarie = build_cotisations_salarie(parameters)

    cotsoc = ParameterNode("cotsoc", data={"description": "Cotisations sociales"})
    parameters.add_child("cotsoc", cotsoc)
    cotsoc.add_child("cotisations_employeur", cotisations_employeur)
    cotsoc.add_child("cotisations_salarie", cotisations_salarie)

    # Modifs
    # cotsoc.add_child('cotisations_employeur', ParameterNode('cotisations_employeur_after_preprocessing', data=dict(description='Cotisations sociales employeur')))
    # cotsoc.add_child('cotisations_salarie', ParameterNode('cotisations_salarie_after_preprocessing', data=dict(description='Cotisations sociales salariales')))

    for cotisation_name, baremes in (
        ("cotisations_employeur", cotisations_employeur.children),
        ("cotisations_salarie", cotisations_salarie.children),
    ):
        for category, bareme in baremes.items():
            if category in [member.name for member in TypesCategorieSalarie]:
                cotsoc.children[cotisation_name].children[category] = bareme

    return parameters
