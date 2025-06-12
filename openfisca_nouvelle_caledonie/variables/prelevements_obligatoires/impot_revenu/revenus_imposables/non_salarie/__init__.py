# Helpers


def get_multiple_and_plafond_cafat_cotisation(period, parameters):
    """Renvoie le plafond de la cotisation CAFAT pour l'année revenus donnée."""
    period_plafond = period.start.offset("first-of", "month").offset(11, "month")
    cafat = parameters(
        period_plafond
    ).prelevements_obligatoires.prelevements_sociaux.cafat
    cotisations = parameters(
        period
    ).prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie.cotisations
    if period_plafond.year >= 2023:
        plafond_cafat = (
            cafat.maladie_retraite.plafond_retraite_mensuel
        )  # Donc année revenus 2023
        multiple = cotisations.plafond_depuis_ir_2024
    else:
        plafond_cafat = cafat.autres_regimes.plafond
        multiple = cotisations.plafond_avant_ir_2024

    return multiple, plafond_cafat
