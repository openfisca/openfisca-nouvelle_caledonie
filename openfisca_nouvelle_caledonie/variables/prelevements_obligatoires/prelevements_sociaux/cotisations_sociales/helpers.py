from openfisca_core.model_api import *


DEFAULT_ROUND_BASE_DECIMALS = 2

cotisations_employeur_by_categorie_salarie = {
    "prive_cadre": [
        "agffc",
        "agirc_arrco",
        "agirc",
        "arrco",
        "ceg",
        "cet",
        "cet2019",
        "chomage",
        "fds",
        "fiaf",
        "fsh",
        "prestations_familiales",
        "retraite",
        "ruamm",
    ],
    "prive_non_cadre": [
        "agffnc",
        "agirc_arrco",
        "arrco",
        "asf",
        "ceg",
        "cet2019",
        "chomage",
        "fds",
        "fiaf",
        "fsh",
        "prestations_familiales",
        "retraite",
        "ruamm",
    ],
    "public_non_titulaire": [],
    "public_titulaire_etat": [],
    "public_titulaire_hospitaliere": [],
    "public_titulaire_militaire": [],
    "public_titulaire_territoriale": [],
}


cotisations_salarie_by_categorie_salarie = {
    "prive_cadre": [
        "agff",
        "agirc_arrco",
        "agirc",
        "apec",
        "arrco",
        "asf",
        "ceg",
        "cet",
        "cet2019",
        "chomage",
        "retraite",
        "ruamm",
    ],
    "prive_non_cadre": [
        "agff",
        "agirc_arrco",
        "asf",
        "arrco",
        "ceg",
        "cet2019",
        "chomage",
        "retraite",
        "ruamm",
    ],
    "public_non_titulaire": [],
    "public_titulaire_etat": [],
    "public_titulaire_hospitaliere": [],
    "public_titulaire_territoriale": [],
}


def apply_bareme_for_relevant_type_sal(
    bareme_by_categorie_salarie,
    bareme_name,
    categorie_salarie,
    base,
    plafond,
    round_base_decimals=DEFAULT_ROUND_BASE_DECIMALS,
):
    """Apply bareme corresponding to bareme_name to the relevant categorie_salarie."""
    assert bareme_by_categorie_salarie is not None
    assert bareme_name is not None
    assert categorie_salarie is not None
    assert base is not None
    assert plafond is not None
    TypesCategorieSalarie = categorie_salarie.possible_values

    def iter_cotisations():
        for categorie_salarie_type in TypesCategorieSalarie:
            if categorie_salarie_type == TypesCategorieSalarie.non_pertinent:
                continue

            if bareme_by_categorie_salarie._name == "cotisations_employeur":
                cotisations_by_categorie_salarie = (
                    cotisations_employeur_by_categorie_salarie
                )
            elif bareme_by_categorie_salarie._name == "cotisations_salarie":
                cotisations_by_categorie_salarie = (
                    cotisations_salarie_by_categorie_salarie
                )
            else:
                raise NameError(
                    "cotisations_employeur nor cotisations_salarie not found"
                )

            try:
                categorie_salarie_baremes = bareme_by_categorie_salarie[
                    categorie_salarie_type.name
                ]
            except KeyError as e:
                print(
                    f"KeyError: {e} in {bareme_by_categorie_salarie._name} for {categorie_salarie_type.name}"
                )
                continue

            if (
                bareme_name
                in cotisations_by_categorie_salarie[categorie_salarie_type.name]
            ):
                bareme = categorie_salarie_baremes[bareme_name]
            else:
                KeyError(
                    f"{bareme_name} not in {bareme_by_categorie_salarie._name} for {categorie_salarie_type.name}"
                )
                continue

            print(f"computing {bareme_name} for {categorie_salarie_type.name}")

            yield bareme.calc(
                base * (categorie_salarie == categorie_salarie_type),
                factor=plafond,
                round_base_decimals=round_base_decimals,
            )

    return sum(iter_cotisations())


def apply_bareme(
    individu,
    period,
    parameters,
    cotisation_type=None,
    bareme_name=None,
    variable_name=None,
):
    cotisation_mode_recouvrement = individu(
        "cotisation_sociale_mode_recouvrement", period
    )
    TypesCotisationSocialeModeRecouvrement = (
        cotisation_mode_recouvrement.possible_values
    )
    cotisation = (
        (
            # anticipé (mensuel avec recouvrement en fin d'année)
            cotisation_mode_recouvrement
            == TypesCotisationSocialeModeRecouvrement.mensuel
        )
        * (
            compute_cotisation_anticipee(
                individu,
                period,
                parameters,
                cotisation_type=cotisation_type,
                bareme_name=bareme_name,
                variable_name=variable_name,
            )
        )
        + (
            # en fin d'année
            cotisation_mode_recouvrement
            == TypesCotisationSocialeModeRecouvrement.annuel
        )
        * (
            compute_cotisation_annuelle(
                individu,
                period,
                parameters,
                cotisation_type=cotisation_type,
                bareme_name=bareme_name,
            )
        )
        + (
            # mensuel strict
            cotisation_mode_recouvrement
            == TypesCotisationSocialeModeRecouvrement.mensuel_strict
        )
        * (
            compute_cotisation(
                individu,
                period,
                parameters,
                cotisation_type=cotisation_type,
                bareme_name=bareme_name,
            )
        )
    )
    return cotisation


def compute_cotisation(
    individu, period, parameters, cotisation_type=None, bareme_name=None
):
    assert cotisation_type is not None
    if cotisation_type == "employeur":
        bareme_by_type_sal_name = parameters(period).cotsoc.cotisations_employeur
    elif cotisation_type == "salarie":
        bareme_by_type_sal_name = parameters(period).cotsoc.cotisations_salarie
    assert bareme_name is not None

    assiette_cotisations_sociales = individu(
        "assiette_cotisations_sociales", period, options=[ADD]
    )
    plafond = individu("plafond_securite_sociale", period, options=[ADD])

    if bareme_name in ["retraite", "fiaf"]:
        plafond = individu("plafond_retraite", period, options=[ADD])

    if bareme_name in ["chomage", "fds", "prestations_familiales"]:
        plafond = individu("plafond_cafat_autres_regimes", period, options=[ADD])

    if bareme_name == "fsh":
        plafond = individu("plafond_fsh", period, options=[ADD])

    if bareme_name == "ruamm":
        plafond = plafond / plafond

    categorie_salarie = individu("categorie_salarie", period.first_month)

    cotisation = apply_bareme_for_relevant_type_sal(
        bareme_by_categorie_salarie=bareme_by_type_sal_name,
        bareme_name=bareme_name,
        base=assiette_cotisations_sociales,
        plafond=plafond,
        categorie_salarie=categorie_salarie,
    )
    return cotisation


def compute_cotisation_annuelle(
    individu, period, parameters, cotisation_type=None, bareme_name=None
):
    if period.start.month < 12:
        return 0
    if period.start.month == 12:
        return compute_cotisation(
            individu,
            period.this_year,
            parameters,
            cotisation_type=cotisation_type,
            bareme_name=bareme_name,
        )


def compute_cotisation_anticipee(
    individu,
    period,
    parameters,
    cotisation_type=None,
    bareme_name=None,
    variable_name=None,
):
    if period.start.month < 12:
        return compute_cotisation(
            individu,
            period.first_month,
            parameters,
            cotisation_type=cotisation_type,
            bareme_name=bareme_name,
        )
    if period.start.month == 12:
        cumul = individu(
            variable_name,
            Period(
                (
                    "month",
                    period.start.offset("first-of", "month").offset(-11, "month"),
                    11,
                )
            ),
            options=[ADD],
        )
        # December variable_name depends on variable_name in the past 11 months.
        # We need to explicitely allow this recursion.

        return (
            compute_cotisation(
                individu,
                period.this_year,
                parameters,
                cotisation_type=cotisation_type,
                bareme_name=bareme_name,
            )
            - cumul
        )
