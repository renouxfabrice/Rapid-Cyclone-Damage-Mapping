# -*- coding: utf-8 -*-
"""
# Building Quality Comparison Tool
Single-script QGIS dialog - native QGIS style
Auteur: Fabrice RENOUX, Eunice WOUODA DONGMO, Mohamed SECK
Version corrigée - Février 2026

Usage: Run from QGIS Script Editor or Python Console
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QLineEdit, QFileDialog, QCheckBox,
    QWidget, QScrollArea, QProgressBar, QTextEdit,
    QFrame, QMessageBox, QApplication, QStackedWidget,
    QRadioButton, QSizePolicy, QToolButton
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont

from qgis.core import (
    QgsVectorLayer, QgsProject, QgsSpatialIndex, QgsFeature, QgsGeometry,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    QgsApplication, QgsSymbol, QgsSingleSymbolRenderer, QgsUnitTypes,
    QgsMapLayerProxyModel, QgsLayerTree, QgsLayerTreeGroup, QgsLayerTreeLayer
)
from qgis.gui import QgsMapLayerComboBox, QgsProjectionSelectionDialog

from PyQt5.QtGui import QColor

import os
import statistics
from datetime import datetime


# ============================================================================
# LANGUAGE
# ============================================================================

_LANG = 'en'   # toggled by language button

T = {
    # Window / group titles
    'title':           {'fr': 'Comparaison Qualité Bâti',             'en': 'Building Quality Comparison'},
    'grp_ref':         {'fr': 'Couche de référence',                   'en': 'Reference Layer'},
    'grp_study':       {'fr': "Couches à évaluer",                     'en': 'Study Layers'},
    'grp_aoi':         {'fr': "Zone d'intérêt (AOI) — optionnel",      'en': 'Area of Interest (AOI) — Optional'},
    'grp_crs':         {'fr': 'Projection / CRS',                      'en': 'Projection / CRS'},
    'grp_params':      {'fr': "Paramètres d'appariement",              'en': 'Matching Parameters'},
    'grp_weights':     {'fr': 'Poids du score',                        'en': 'Score Weights'},
    'grp_output':      {'fr': 'Résultats et sorties',                  'en': 'Output'},
    # Radio / checkbox labels
    'from_project':    {'fr': 'Depuis le projet',                      'en': 'From project'},
    'from_file':       {'fr': 'Depuis un fichier',                     'en': 'From file'},
    'chk_aoi':         {'fr': "Limiter l'analyse à une zone spécifique", 'en': 'Restrict analysis to a specific area'},
    'chk_sensitivity': {'fr': 'Analyse de sensibilité automatique (F1-score, 16 combinaisons par couche)',
                        'en': 'Automatic sensitivity analysis (F1-score, 16 combinations per layer)'},
    'chk_save_layers': {'fr': 'Exporter les couches en GeoPackage dans le dossier de sortie',
                        'en': 'Export output layers to GeoPackage files in the report directory'},
    # CRS
    'lbl_crs_auto':    {'fr': 'CRS détecté (auto) :',                  'en': 'Auto-detected CRS:'},
    'lbl_crs_use':     {'fr': 'CRS à utiliser :',                      'en': 'CRS to use:'},
    'btn_crs_sel':     {'fr': 'Sélectionner...',                       'en': 'Select...'},
    'crs_placeholder': {'fr': "(sélectionner la couche référence d'abord)", 'en': '(select reference layer first)'},
    'crs_warning':     {'fr': ("Attention : le CRS sélectionné n'est pas métrique. "
                               "Les calculs de distance seront incorrects. "
                               "Choisir un CRS UTM ou toute autre projection en mètres."),
                        'en': ('Warning: the selected CRS is not metric (not projected in metres). '
                               'Distance calculations will be incorrect. '
                               'Please select a UTM or other metric CRS.')},
    # Params
    'grp_manual':      {'fr': 'Paramètres manuels (si analyse de sensibilité désactivée)',
                        'en': 'Manual parameters (used when sensitivity analysis is off)'},
    'lbl_max_dist':    {'fr': 'Distance centroïde max (m) :',          'en': 'Max centroid distance (m):'},
    'lbl_jaccard':     {'fr': 'Jaccard minimum :',                     'en': 'Min Jaccard index:'},
    'lbl_match_mode':  {'fr': "Mode d'appariement :",                 'en': 'Matching mode:'},
    'match_unique':    {'fr': '1:1 Unique (recommandé)',                'en': '1:1 Unique (recommended)'},
    'match_multi':     {'fr': '1:n Multiple',                          'en': '1:n Multiple'},
    # Weights
    'lbl_w_jac':       {'fr': 'Poids Jaccard (%) :',                   'en': 'Jaccard weight (%):'},
    'lbl_w_dist':      {'fr': 'Poids Distance (%) :',                  'en': 'Distance weight (%):'},
    'lbl_w_area':      {'fr': 'Poids Surface (%) :',                   'en': 'Area weight (%):'},
    'lbl_w_bonus':     {'fr': 'Poids Bonus (%) :',                     'en': 'Bonus weight (%):'},
    'weights_note':    {'fr': 'Note : les poids sont normalisés automatiquement.',
                        'en': 'Note: weights are normalised automatically.'},
    # Output
    'lbl_report_dir':  {'fr': 'Dossier des rapports :',                'en': 'Report directory:'},
    # Study row
    'layer_n':         {'fr': 'Couche',                                'en': 'Layer'},
    'btn_remove':      {'fr': 'Supprimer',                             'en': 'Remove'},
    'lbl_alias':       {'fr': "Nom d'affichage (alias) :",            'en': 'Display name (alias):'},
    'alias_ph':        {'fr': "Optionnel — laisser vide pour utiliser le nom de la couche",
                        'en': 'Optional — leave empty to use layer name'},
    'file_ph':         {'fr': 'Chemin vers le fichier (.shp / .gpkg)...',
                        'en': 'Path to vector file (.shp / .gpkg)...'},
    'btn_browse':      {'fr': 'Parcourir...',                          'en': 'Browse...'},
    # Buttons
    'btn_run':         {'fr': "Lancer l'analyse",                      'en': 'Run analysis'},
    'btn_running':     {'fr': 'Analyse en cours...',                   'en': 'Running...'},
    'btn_close':       {'fr': 'Fermer',                                'en': 'Close'},
    'btn_add_layer':   {'fr': 'Ajouter une couche',                    'en': 'Add layer'},
    'btn_clear':       {'fr': 'Effacer',                               'en': 'Clear'},
    'lbl_log':         {'fr': "Journal d'exécution",                   'en': 'Execution log'},
    # Validation
    'validation':      {'fr': 'Validation',                            'en': 'Validation'},
    'val_ref':         {'fr': 'Sélectionnez une couche de référence valide.',
                        'en': 'Please select a valid reference layer.'},
    'val_study':       {'fr': 'Ajoutez au moins une couche à évaluer valide.',
                        'en': 'Please add at least one valid study layer.'},
    'val_crs':         {'fr': "Aucun CRS disponible. Sélectionnez la couche référence d'abord.",
                        'en': 'No CRS available. Please select the reference layer first.'},
    'val_crs_metric':  {'fr': ("Le CRS sélectionné n'est pas en mètres.\n"
                               "Les calculs de distance seront incorrects.\n\n"
                               "Continuer quand même ?"),
                        'en': ("The selected CRS is not metric (not projected in metres).\n"
                               "Distance calculations will be incorrect.\n\n"
                               "Do you want to continue anyway?")},
    'non_metric_title':{'fr': 'CRS non métrique',                      'en': 'Non-metric CRS'},
    # Log / done messages
    'log_max_layers':  {'fr': "Maximum 5 couches d'étude autorisées.",'en': 'Maximum 5 study layers allowed.'},
    'log_min_layer':   {'fr': "Au moins une couche d'étude est requise.", 'en': 'At least one study layer is required.'},
    'log_started':     {'fr': 'Analyse démarrée',                      'en': 'Analysis started'},
    'log_reference':   {'fr': 'Référence',                             'en': 'Reference'},
    'log_crs':         {'fr': 'CRS',                                   'en': 'CRS'},
    'log_layers':      {'fr': "Couches à évaluer",                     'en': 'Study layers'},
    'log_sensitivity': {'fr': 'Analyse de sensibilité',                'en': 'Sensitivity analysis'},
    'log_yes':         {'fr': 'oui',                                   'en': 'yes'},
    'log_no':          {'fr': 'non',                                   'en': 'no'},
    'log_complete':    {'fr': 'ANALYSE TERMINÉE',                      'en': 'ANALYSIS COMPLETE'},
    'log_ranking':     {'fr': 'Classement (par score global) :',       'en': 'Ranking (by global score):'},
    'log_report':      {'fr': 'Rapport',                               'en': 'Report'},
    'log_error':       {'fr': 'ERREUR',                                'en': 'ERROR'},
    # Done popup
    'done_title':      {'fr': 'Analyse terminée',                      'en': 'Analysis complete'},
    'done_msg':        {'fr': (' couche(s) évaluée(s).\n\nLes couches de sortie ont été ajoutées '
                               'au projet QGIS, groupées par couche dans le panneau Couches.'),
                        'en': (' layer(s) evaluated.\n\nOutput layers have been added to the QGIS '
                               'project, grouped by study layer name in the Layers panel.')},
    'done_report':     {'fr': '\n\nRapport enregistré dans :\n',   'en': '\n\nReport saved to:\n'},
    'err_title':       {'fr': 'Erreur',                                'en': 'Error'},
    'err_msg':         {'fr': 'Une erreur est survenue :',             'en': 'An error occurred:'},
    # ref info
    'buildings':       {'fr': 'bâtiments',                             'en': 'buildings'},
    'ref_ph':          {'fr': 'Chemin vers la couche de référence (.shp / .gpkg)...',
                        'en': 'Path to reference file (.shp / .gpkg)...'},
    'aoi_ph':          {'fr': 'Chemin vers le masque AOI (.shp / .gpkg)...',
                        'en': 'Path to AOI mask (.shp / .gpkg)...'},
    'out_ph':          {'fr': 'Laisser vide pour ne pas générer de rapports texte',
                        'en': 'Leave empty to skip text reports'},
}

def tr(key):
    return T.get(key, {}).get(_LANG, T.get(key, {}).get('en', key))


# ============================================================================
# HELP TEXTS  (bilingual)
# ============================================================================

HELP = {
    'reference_layer': {
        'fr': ("Couche de référence\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Jeu de données bâti de référence (terrain vérité). Il doit être le plus précis "
               "disponible pour la zone (cadastre, relevé terrain, numérisation haute résolution).\n\n"
               "Toutes les couches à évaluer seront comparées à cette référence.\n\n"
               "Formats acceptés : Shapefile (.shp), GeoPackage (.gpkg)"),
        'en': ("Reference Layer\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "The ground-truth building dataset used as baseline for all comparisons. "
               "It should be the most accurate dataset available for your study area "
               "(e.g. cadastral data, field-surveyed footprints, high-resolution digitisation).\n\n"
               "All study layers will be evaluated against this reference.\n\n"
               "Supported formats: Shapefile (.shp), GeoPackage (.gpkg)")
    },
    'study_layers': {
        'fr': ("Couches à évaluer\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Couches bâti à évaluer par rapport à la référence (OSM, Microsoft, Google, etc.).\n\n"
               "Jusqu'à 5 couches. Chacune reçoit un score qualité individuel et un classement final.\n\n"
               "Alias : si le nom de la couche n'est pas parlant, renseigner un alias court "
               "qui sera utilisé dans les rapports et les noms de couches de sortie."),
        'en': ("Study Layers\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Building layers to evaluate against the reference. Typically datasets from "
               "different providers or methods (e.g. OpenStreetMap, Microsoft Building Footprints, "
               "Google Open Buildings, automated AI extraction).\n\n"
               "Up to 5 layers. Each receives an individual quality score and a final ranking "
               "is produced.\n\n"
               "Alias: if the layer name is not meaningful, enter a short alias that will be "
               "used in all reports and output layer names.")
    },
    'aoi': {
        'fr': ("Zone d'intérêt (AOI) — Optionnel\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Restreindre l'analyse à une zone spécifique en fournissant un masque polygone. "
               "Seuls les bâtiments dans cette zone seront pris en compte.\n\n"
               "Si vide, tous les entités des deux couches sont utilisées."),
        'en': ("Area of Interest (AOI) — Optional\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Restrict the analysis to a specific area by providing a polygon mask. "
               "Only buildings within this zone will be considered.\n\n"
               "If left empty, all features in both layers are used.")
    },
    'crs': {
        'fr': ("Projection / CRS\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Tous les calculs de distance et de surface nécessitent un CRS métrique (mètres). "
               "Le CRS UTM adapté est détecté automatiquement depuis l'emprise de la couche référence.\n\n"
               "ATTENTION : un CRS en degrés (ex. WGS84 / EPSG:4326) produira des distances "
               "sans signification. Toujours utiliser un CRS UTM.\n\n"
               "Cliquer sur Sélectionner... pour ouvrir le sélecteur QGIS."),
        'en': ("Coordinate Reference System (CRS)\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "All distance and area calculations require a metric projected CRS (metres). "
               "The tool auto-detects the most appropriate UTM zone from the reference layer extent.\n\n"
               "WARNING: Using a geographic CRS (degrees, e.g. WGS84 / EPSG:4326) will produce "
               "meaningless distance results. Always use UTM or another metric projected CRS.\n\n"
               "Click 'Select...' to open the full QGIS projection selector.")
    },
    'sensitivity': {
        'fr': ("Analyse de sensibilité automatique\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Teste 16 combinaisons de paramètres (4 distances × 4 seuils Jaccard) par couche "
               "et retient celle qui maximise le F1-score.\n\n"
               "F1-score = moyenne harmonique de l'exhaustivité et de la précision (ISO 19157).\n\n"
               "Durée : environ 2-3 min par couche. Désactiver pour utiliser des paramètres manuels."),
        'en': ("Automatic Sensitivity Analysis\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "When enabled, the tool tests 16 parameter combinations (4 distance x 4 Jaccard "
               "thresholds) per study layer and selects the combination maximising the F1-score.\n\n"
               "F1-score = harmonic mean of Completeness (recall) and Correctness (precision), "
               "following ISO 19157 data quality principles.\n\n"
               "Duration: approx. 2-3 min per layer. Disable to use fixed manual parameters instead.")
    },
    'max_distance': {
        'fr': ("Distance centroïde maximale (mètres)\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Deux bâtiments ne sont candidats à l'appariement que si la distance entre "
               "leurs centroïdes est inférieure à ce seuil.\n\n"
               "Valeurs recommandées :\n"
               "  Données bien alignées :        5 - 10 m\n"
               "  Erreur positionnelle modérée : 10 - 15 m\n"
               "  Précision faible :             15 - 20 m\n\n"
               "Actif uniquement si l'analyse de sensibilité est désactivée."),
        'en': ("Maximum Centroid Distance (metres)\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Two buildings are candidate matches only if the distance between their centroids "
               "is below this threshold.\n\n"
               "Recommended values:\n"
               "  Well-aligned datasets:      5 - 10 m\n"
               "  Moderate positional error: 10 - 15 m\n"
               "  Poor positional accuracy:  15 - 20 m\n\n"
               "Only active when sensitivity analysis is disabled.")
    },
    'jaccard_min': {
        'fr': ("Indice de Jaccard minimum\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Mesure le recouvrement géométrique entre deux polygones :\n"
               "  Jaccard = Aire intersection / Aire union\n\n"
               "1.0 = correspondance parfaite. 0.0 = aucun chevauchement.\n\n"
               "Valeurs recommandées :\n"
               "  Haute qualité de forme :         0.7 - 0.8\n"
               "  Formes approximatives (Caraïbe) : 0.5 - 0.6\n\n"
               "Actif uniquement si l'analyse de sensibilité est désactivée."),
        'en': ("Minimum Jaccard Index\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Measures geometric overlap between two polygons:\n"
               "  Jaccard = Intersection area / Union area\n\n"
               "Value of 1.0 = perfect match. Value of 0.0 = no overlap.\n\n"
               "Recommended values:\n"
               "  High shape quality:                0.7 - 0.8\n"
               "  Approximate shapes (Caribbean):    0.5 - 0.6\n\n"
               "Only active when sensitivity analysis is disabled.")
    },
    'match_mode': {
        'fr': ("Mode d'appariement\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "1:1 Unique (recommandé) :\n"
               "Chaque bâtiment référence est apparié à au plus un bâtiment d'étude. "
               "Permet une comparaison objective entre couches.\n\n"
               "1:n Multiple :\n"
               "Un bâtiment référence peut être apparié à plusieurs bâtiments d'étude. "
               "Utile pour les jeux de données avec subdivisions ou fusions."),
        'en': ("Matching Mode\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "1:1 Unique (recommended):\n"
               "Each reference building is matched to at most one study building. "
               "Enables objective comparison between layers on equal terms.\n\n"
               "1:n Multiple:\n"
               "A reference building can be matched by several study buildings. "
               "Useful for datasets representing building splits or merges differently.")
    },
    'weights': {
        'fr': ("Poids du score global\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Le score global est une somme pondérée de quatre métriques normalisées :\n\n"
               "  Jaccard :  qualité forme/surface (défaut 42%)\n"
               "  Distance : précision positionnelle (défaut 35%)\n"
               "  Surface :  qualité ratio de taille (défaut 18%)\n"
               "  Bonus :    stabilité / cohérence (défaut 5%)\n\n"
               "Les poids sont normalisés automatiquement (somme = 100%)."),
        'en': ("Global Score Weights\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "The global quality score is a weighted sum of four normalised metrics:\n\n"
               "  Jaccard weight:   shape/area overlap quality     (default 42%)\n"
               "  Distance weight:  positional accuracy            (default 35%)\n"
               "  Area weight:      building size ratio quality    (default 18%)\n"
               "  Bonus weight:     stability / consistency bonus  (default  5%)\n\n"
               "Weights are normalised automatically so their sum always equals 100%.")
    },
    'output_dir': {
        'fr': ("Dossier de sortie\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Si renseigné, les rapports texte seront enregistrés ici :\n"
               "  - Un rapport détaillé par couche\n"
               "  - Un fichier de synthèse avec classement\n\n"
               "Laisser vide pour ne pas générer de rapports (résultats visibles dans le journal)."),
        'en': ("Output Directory\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "If specified, text reports will be saved here:\n"
               "  - One detailed report per study layer\n"
               "  - One summary file ranking all layers\n\n"
               "Leave empty to skip file reports (results are still shown in the log panel).")
    },
    'save_layers': {
        'fr': ("Couches de sortie\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Trois couches sont produites par couche évaluée et ajoutées au projet QGIS :\n\n"
               "  Matched       bâtiments correctement détectés (contour vert)\n"
               "  Unmatched     bâtiments sans équivalent dans la référence (contour rouge)\n"
               "  Not detected  bâtiments référence non détectés (contour violet)\n\n"
               "Les couches sont groupées par couche dans le panneau Couches QGIS."),
        'en': ("Output Layers\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Three derived layers are produced per study layer and added to the QGIS project:\n\n"
               "  Matched       buildings correctly detected (green outline)\n"
               "  Unmatched     buildings with no reference match (red outline)\n"
               "  Not detected  reference buildings missed by study layer (purple outline)\n\n"
               "Layers are grouped by study layer name in the QGIS Layers panel.")
    },
}

def help_text(key):
    return HELP.get(key, {}).get(_LANG, HELP.get(key, {}).get('en', ''))


# ============================================================================
# CORE ANALYSIS FUNCTIONS
# ============================================================================

def calculate_mad(values):
    if not values:
        return 0
    median = statistics.median(values)
    return statistics.median([abs(x - median) for x in values])

def identify_significant_differences(area_differences, threshold=0.5):
    return [d for d in area_differences if abs(d) > threshold]

def find_best_utm_crs(layer):
    try:
        crs = layer.crs()
        if crs.authid().startswith('EPSG:326') or crs.authid().startswith('EPSG:327'):
            return crs

        centroid = layer.extent().center()
        lat, lon = centroid.y(), centroid.x()

        if abs(lat) > 90 or abs(lon) > 180:
            wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
            t = QgsCoordinateTransform(crs, wgs84, QgsProject.instance())
            c = t.transform(centroid)
            lat, lon = c.y(), c.x()

        zone = max(1, min(int((lon + 180) / 6) + 1, 60))
        code = f"326{zone:02d}" if lat >= 0 else f"327{zone:02d}"
        return QgsCoordinateReferenceSystem(f"EPSG:{code}")
    except Exception:
        return QgsCoordinateReferenceSystem("EPSG:32631")

def ensure_metric_crs(layer):
    crs = layer.crs()
    if crs.mapUnits() == QgsUnitTypes.DistanceMeters:
        return crs
    return find_best_utm_crs(layer)

def is_metric_crs(crs):
    return crs.mapUnits() == QgsUnitTypes.DistanceMeters

def apply_outline_style(layer, color_name, width=0.5):
    try:
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        sl = symbol.symbolLayer(0)
        sl.setFillColor(QColor(0, 0, 0, 0))
        sl.setStrokeColor(QColor(color_name))
        sl.setStrokeWidth(width)
        sl.setStrokeStyle(1)
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        layer.triggerRepaint()
    except Exception:
        pass

def initialize_ref_index(layer_ref, ref_crs):
    t = None
    if layer_ref.crs() != ref_crs:
        t = QgsCoordinateTransform(layer_ref.crs(), ref_crs, QgsProject.instance())

    index = QgsSpatialIndex()
    features = {}
    for f in layer_ref.getFeatures():
        g = QgsGeometry(f.geometry())
        if t:
            g.transform(t)
        g = g.makeValid()
        features[f.id()] = {
            'geom': g,
            'centroid': g.centroid(),
            'area': g.area()
        }
        tmp = QgsFeature()
        tmp.setGeometry(g)
        tmp.setId(f.id())
        index.insertFeature(tmp)

    return {'index': index, 'features': features}

def match_buildings(layer_study, ref_data, max_dist, jaccard_min, ref_crs, allow_multiple, log_fn=None):
    def log(m):
        if log_fn:
            log_fn(m)

    index = ref_data['index']
    ref_features = ref_data['features']

    t = None
    if layer_study.crs() != ref_crs:
        t = QgsCoordinateTransform(layer_study.crs(), ref_crs, QgsProject.instance())

    matches = {}
    ref_match_count = {}
    distances, area_diffs, jaccards = [], [], []

    log(f"  Matching: {layer_study.featureCount()} study buildings vs {len(ref_features)} reference")
    log(f"  Parameters: max_distance={max_dist} m, min_jaccard={jaccard_min}")

    for sf in layer_study.getFeatures():
        sg = QgsGeometry(sf.geometry())
        if t:
            sg.transform(t)
        sg = sg.makeValid()
        sc = sg.centroid()

        rect = sc.buffer(max_dist, 8).boundingBox()
        candidates = index.intersects(rect)

        best = None
        best_score = -1

        for rid in candidates:
            if rid not in ref_features:
                continue
            rf = ref_features[rid]
            rg = rf['geom']

            dist = sc.distance(rf['centroid'])
            if dist > max_dist:
                continue

            inter = sg.intersection(rg).area()
            union = sg.area() + rg.area() - inter
            jaccard = inter / union if union > 0 else 0
            if jaccard < jaccard_min:
                continue

            score = jaccard * 0.6 + (1 - min(dist / max_dist, 1)) * 0.4
            if score > best_score:
                best_score = score
                best = {'ref_id': rid, 'jaccard': jaccard, 'distance': dist,
                        'area_diff': abs(sg.area() - rg.area())}

        if best:
            rid = best['ref_id']
            if not allow_multiple and rid in ref_match_count:
                continue
            matches[sf.id()] = rid
            ref_match_count[rid] = ref_match_count.get(rid, 0) + 1
            distances.append(best['distance'])
            area_diffs.append(best['area_diff'])
            jaccards.append(best['jaccard'])

    log(f"  Matches found: {len(matches)}")
    return {
        'matches': matches,
        'ref_match_count': ref_match_count,
        'distances': distances,
        'area_diffs': area_diffs,
        'jaccards': jaccards
    }

def calculate_metrics(layer_study, layer_ref, match_result, allow_multiple):
    nb_ref = layer_ref.featureCount()
    nb_study = layer_study.featureCount()
    matches = match_result['matches']
    ref_match_count = match_result['ref_match_count']
    distances = match_result['distances']
    area_diffs = match_result['area_diffs']
    jaccards = match_result['jaccards']

    nb_matched_ref = len(ref_match_count)
    nb_matched_study = len(matches)

    completeness = (nb_matched_ref / nb_ref * 100) if nb_ref > 0 else 0
    commission = ((nb_study - nb_matched_study) / nb_study * 100) if nb_study > 0 else 0
    overlap = (sum(jaccards) / len(jaccards) * 100) if jaccards else 0

    mean_dist = sum(distances) / len(distances) if distances else 0
    median_dist = statistics.median(distances) if distances else 0
    mad_dist = calculate_mad(distances) if distances else 0
    median_area = statistics.median(area_diffs) if area_diffs else 0
    mad_area = calculate_mad(area_diffs) if area_diffs else 0
    pct_sig = (len(identify_significant_differences(area_diffs)) / len(area_diffs) * 100) if area_diffs else 0

    return {
        'completeness': completeness,
        'commission': commission,
        'overlap': overlap,
        'mean_dist': mean_dist,
        'median_dist': median_dist,
        'mad_dist': mad_dist,
        'median_area': median_area,
        'mad_area': mad_area,
        'pct_significant': pct_sig,
        'nb_matched_ref': nb_matched_ref,
        'nb_matched_study': nb_matched_study,
        'nb_ref': nb_ref,
        'nb_study': nb_study
    }

def calculate_f1(completeness, commission):
    precision = 1.0 - (commission / 100.0)
    recall = completeness / 100.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall) * 100

def calculate_global_score(metrics, weights):
    s_comp = max(0, min(metrics['completeness'] / 100.0, 1))
    s_comm = max(0, min(1.0 - metrics['commission'] / 100.0, 1))
    s_over = max(0, min(metrics['overlap'] / 100.0, 1))
    md = metrics['median_dist']
    s_dist = 1.0 if md <= 0 else (0.0 if md >= 20 else 1.0 - md / 20.0)
    s_dist = max(0, min(s_dist, 1))

    score = (
        s_comp * weights.get('jaccard', 0.42) +
        s_comm * weights.get('distance', 0.35) +
        s_over * weights.get('area', 0.18) +
        s_dist * weights.get('bonus', 0.05)
    )
    return {
        's_completeness': s_comp, 's_commission': s_comm,
        's_overlap': s_over, 's_distance': s_dist,
        'score_global': max(0, min(score, 1))
    }

def run_sensitivity(layer_study, layer_ref, ref_data, ref_crs, log_fn=None):
    distances_test = [5, 10, 15, 20]
    jaccard_test = [0.5, 0.6, 0.7, 0.8]
    best_score = -1
    best_params = {'distance': 10.0, 'jaccard': 0.7, 'f1': 0.0}

    for d in distances_test:
        for j in jaccard_test:
            try:
                mr = match_buildings(layer_study, ref_data, d, j, ref_crs, False)
                m = calculate_metrics(layer_study, layer_ref, mr, False)
                f1 = calculate_f1(m['completeness'], m['commission'])
                if log_fn:
                    log_fn(f"  dist={d:2d}m  jaccard={j:.1f}  F1={f1:.1f}%")
                if f1 > best_score:
                    best_score = f1
                    best_params = {'distance': d, 'jaccard': j, 'f1': f1}
            except Exception:
                continue
    return best_params

def create_output_layers(layer_study, layer_ref, match_result, ref_crs, alias):
    """Create the three output layers. alias is the display name for this study layer."""
    matches = match_result['matches']
    ref_matched_ids = set(match_result['ref_match_count'].keys())
    crs_id = layer_study.crs().authid()

    lyr_matched = QgsVectorLayer(f"Polygon?crs={crs_id}", f"{alias} - Matched", "memory")
    lyr_matched.dataProvider().addAttributes(layer_study.fields())
    lyr_matched.updateFields()

    lyr_unmatched = QgsVectorLayer(f"Polygon?crs={crs_id}", f"{alias} - Unmatched", "memory")
    lyr_unmatched.dataProvider().addAttributes(layer_study.fields())
    lyr_unmatched.updateFields()

    lyr_notdetected = QgsVectorLayer(f"Polygon?crs={crs_id}", f"{alias} - Not Detected (ref)", "memory")
    lyr_notdetected.dataProvider().addAttributes(layer_ref.fields())
    lyr_notdetected.updateFields()

    for feat in layer_study.getFeatures():
        nf = QgsFeature(feat)
        if feat.id() in matches:
            lyr_matched.dataProvider().addFeature(nf)
        else:
            lyr_unmatched.dataProvider().addFeature(nf)

    t = None
    if layer_ref.crs() != layer_study.crs():
        t = QgsCoordinateTransform(layer_ref.crs(), layer_study.crs(), QgsProject.instance())
    for feat in layer_ref.getFeatures():
        if feat.id() not in ref_matched_ids:
            nf = QgsFeature(feat)
            if t:
                g = QgsGeometry(nf.geometry())
                g.transform(t)
                nf.setGeometry(g)
            lyr_notdetected.dataProvider().addFeature(nf)

    apply_outline_style(lyr_matched, "green")
    apply_outline_style(lyr_unmatched, "red")
    apply_outline_style(lyr_notdetected, "darkMagenta")

    return {
        'matched': lyr_matched,
        'unmatched': lyr_unmatched,
        'not_detected': lyr_notdetected
    }

def add_layers_as_group(project, group_name, layers_dict):
    """
    Add layers into a named group in the QGIS layer tree.
    layers_dict = {'matched': lyr, 'unmatched': lyr, 'not_detected': lyr}
    Order in panel: Matched on top, then Unmatched, then Not Detected.
    """
    root = project.layerTreeRoot()

    # Create group at top of tree
    group = root.insertGroup(0, group_name)

    # Add layers in display order (top to bottom in panel)
    order = ['matched', 'unmatched', 'not_detected']
    for key in order:
        lyr = layers_dict.get(key)
        if lyr:
            lyr.updateExtents()
            project.addMapLayer(lyr, False)          # False = don't add to root
            group.addLayer(lyr)

    return group

def write_reports(out_dir, all_results, ref_name, nb_ref, crs_id, weights, timestamp, lang="en"):
    summary_path = os.path.join(out_dir, f"summary_{timestamp}.txt")

    fr = (lang == 'fr')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(("COMPARAISON QUALITÉ BÂTI - SYNTHÈSE\n") if fr else ("BUILDING QUALITY COMPARISON - SUMMARY\n"))
        f.write("=" * 100 + "\n\n")
        f.write(f"{'Référence' if fr else 'Reference'} : {ref_name} ({nb_ref} {'bâtiments' if fr else 'buildings'})\n")
        f.write(f"CRS  : {crs_id}\n")
        f.write(f"{'Date' if fr else 'Date'} : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(
            f"{'Poids' if fr else 'Weights'} : Jaccard {weights.get('jaccard',0.42)*100:.1f}%  |  "
            f"{'Distance' if fr else 'Distance'} {weights.get('distance',0.35)*100:.1f}%  |  "
            f"{'Surface' if fr else 'Area'} {weights.get('area',0.18)*100:.1f}%  |  "
            f"Bonus {weights.get('bonus',0.05)*100:.1f}%\n\n"
        )

        f.write(("PARAMÈTRES UTILISÉS PAR COUCHE\n") if fr else ("PARAMETERS USED PER LAYER\n"))
        f.write("-" * 100 + "\n")
        lbl_layer = 'Couche' if fr else 'Layer'
        lbl_src   = 'Source' if fr else 'Source'
        f.write(f"{lbl_layer:<35} {'Distance':>10} {'Jaccard':>10} {lbl_src:<25}\n")
        f.write("-" * 100 + "\n")
        for r in all_results:
            f.write(
                f"{r['alias']:<35} {r['distance_used']:>10.1f} "
                f"{r['jaccard_used']:>10.2f} {r['params_source']:<25}\n"
            )

        f.write(("\nCLASSEMENT\n") if fr else ("\nRANKING\n"))
        f.write("-" * 100 + "\n")
        for rank, r in enumerate(sorted(all_results, key=lambda x: x['score_global'], reverse=True), 1):
            f.write(f"\n{rank}. {r['alias']}\n")
            f.write(f"   {'Score global' if fr else 'Global score'}   : {r['score_global']*100:.1f}%\n")
            f.write(f"   F1-score       : {r['f1_score']:.1f}%\n")
            f.write(f"   {'Exhaustivité' if fr else 'Completeness'}   : {r['completeness']:.1f}%\n")
            f.write(f"   {'Sur-complétion' if fr else 'Commission err.'}: {r['commission']:.1f}%\n")
            f.write(f"   {'Recouvrement' if fr else 'Overlap (Jacc.)'}: {r['overlap']:.1f}%\n")
            f.write(f"   {'Dist. médiane' if fr else 'Median distance'}: {r['median_dist']:.2f} m\n")

    for r in all_results:
        safe = r['alias'].replace(' ', '_').replace('/', '_')
        rpath = os.path.join(out_dir, f"report_{safe}.txt")
        with open(rpath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write((f"RAPPORT : {r['alias']}\n") if fr else (f"REPORT: {r['alias']}\n"))
            f.write("=" * 60 + "\n\n")
            f.write(f"{'Couche étude' if fr else 'Study layer'}     : {r['layer_name']}\n")
            f.write(f"{'Bâtiments étude' if fr else 'Buildings study'} : {r['nb_study']}\n")
            f.write(f"{'Bâtiments réf.' if fr else 'Buildings ref.'}  : {r['nb_ref']}\n")
            f.write(f"{'Appariés (réf.)' if fr else 'Matched (ref)'}   : {r['nb_matched_ref']}\n")
            f.write(f"{'Appariés (étude)' if fr else 'Matched (study)'} : {r['nb_matched_study']}\n\n")
            f.write(f"{'Exhaustivité' if fr else 'Completeness'}    : {r['completeness']:.1f}%\n")
            f.write(f"{'Sur-complétion' if fr else 'Commission err.'} : {r['commission']:.1f}%\n")
            f.write(f"F1-score        : {r['f1_score']:.1f}%\n")
            f.write(f"{'Recouvrement' if fr else 'Overlap (Jacc.)'} : {r['overlap']:.1f}%\n")
            f.write(f"{'Dist. médiane' if fr else 'Median distance'} : {r['median_dist']:.2f} m\n")
            f.write(f"{'MAD distance' if fr else 'MAD distance'}    : {r['mad_dist']:.2f} m\n\n")
            f.write(f"{'Score global' if fr else 'Global score'}    : {r['score_global']*100:.1f}%\n\n")
            score = r['score_global']
            if fr:
                if score >= 0.85:
                    f.write("Recommandation : EXCELLENT — Utilisation directe possible\n")
                elif score >= 0.70:
                    f.write("Recommandation : BON — Utiliser avec validation ponctuelle\n")
                elif score >= 0.50:
                    f.write("Recommandation : ACCEPTABLE — Nettoyage requis\n")
                else:
                    f.write("Recommandation : INSUFFISANT — Ne pas utiliser sans révision majeure\n")
            else:
                if score >= 0.85:
                    f.write("Recommendation: EXCELLENT - Use directly\n")
                elif score >= 0.70:
                    f.write("Recommendation: GOOD - Use with spot-check validation\n")
                elif score >= 0.50:
                    f.write("Recommendation: ACCEPTABLE - Requires cleaning\n")
                else:
                    f.write("Recommendation: INSUFFICIENT - Do not use without major revision\n")

    return summary_path


# ============================================================================
# WORKER THREAD
# ============================================================================

class AnalysisWorker(QThread):
    log_signal      = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    error_signal    = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        try:
            p = self.params
            layer_ref     = p['layer_ref']
            study_items   = p['study_items']   # list of {'layer': ..., 'alias': ...}
            ref_crs       = p['ref_crs']
            weights       = p['weights']
            allow_multiple = p['allow_multiple']
            max_dist      = p['max_dist']
            jaccard_min   = p['jaccard_min']
            use_sensitivity = p['use_sensitivity']
            out_dir       = p['out_dir']
            timestamp     = p['timestamp']

            self.log('Initialisation de l\'index spatial...' if _LANG=='fr' else 'Initialising spatial index on reference layer...')
            ref_data = initialize_ref_index(layer_ref, ref_crs)
            self.log(f"  {len(ref_data['features'])} " + ('bâtiments référence indexés.\n' if _LANG=='fr' else 'reference buildings indexed.\n'))

            project = QgsProject.instance()
            all_results = []
            total = len(study_items)

            for idx, item in enumerate(study_items):
                layer_study = item['layer']
                alias = item['alias']

                self.log(f"{'─'*60}")
                self.log(f"{'Traitement couche' if _LANG=='fr' else 'Processing layer'} {idx+1}/{total}: {alias}")
                self.log(f"{'─'*60}")

                if use_sensitivity:
                    self.log('  Analyse de sensibilité (16 combinaisons)...' if _LANG=='fr' else '  Running sensitivity analysis (16 combinations)...')
                    best = run_sensitivity(layer_study, layer_ref, ref_data, ref_crs, self.log)
                    layer_dist    = best['distance']
                    layer_jaccard = best['jaccard']
                    params_source = f"Auto F1={best.get('f1',0):.1f}%"
                    self.log(f"  {'Paramètres optimaux' if _LANG=='fr' else 'Best params'}: distance={layer_dist} m  jaccard={layer_jaccard}")
                else:
                    layer_dist    = max_dist
                    layer_jaccard = jaccard_min
                    params_source = "Manual"
                    self.log(f"  {'Paramètres manuels' if _LANG=='fr' else 'Manual params'}: distance={layer_dist} m  jaccard={layer_jaccard}")

                self.log('  Appariement des bâtiments...' if _LANG=='fr' else '  Matching buildings...')
                mr = match_buildings(
                    layer_study, ref_data, layer_dist, layer_jaccard,
                    ref_crs, allow_multiple, self.log
                )

                self.log('  Calcul des métriques de qualité...' if _LANG=='fr' else '  Computing quality metrics...')
                metrics = calculate_metrics(layer_study, layer_ref, mr, allow_multiple)
                scores  = calculate_global_score(metrics, weights)
                f1      = calculate_f1(metrics['completeness'], metrics['commission'])

                self.log('  Création des couches de sortie...' if _LANG=='fr' else '  Creating output layers...')
                out_layers = create_output_layers(layer_study, layer_ref, mr, ref_crs, alias)

                # Add to project under a named group
                group_name = f"[{idx+1}] {alias}"
                add_layers_as_group(project, group_name, out_layers)

                self.log(f"  {'Couches ajoutées au groupe' if _LANG=='fr' else 'Layers added to group'}: '{group_name}'")
                self.log(f"  {'Score global' if _LANG=='fr' else 'Global score'} : {scores['score_global']*100:.1f}%")
                self.log(f"  F1-score : {f1:.1f}%")
                self.log(f"  {'Exhaustivité' if _LANG=='fr' else 'Completeness'} : {metrics['completeness']:.1f}%  |  Commission: {metrics['commission']:.1f}%\n")

                all_results.append({
                    'alias':          alias,
                    'layer_name':     layer_study.name(),
                    'completeness':   metrics['completeness'],
                    'commission':     metrics['commission'],
                    'overlap':        metrics['overlap'],
                    'mean_dist':      metrics['mean_dist'],
                    'median_dist':    metrics['median_dist'],
                    'mad_dist':       metrics['mad_dist'],
                    'median_area':    metrics['median_area'],
                    'pct_significant':metrics['pct_significant'],
                    'nb_matched_ref': metrics['nb_matched_ref'],
                    'nb_matched_study': metrics['nb_matched_study'],
                    'nb_ref':         metrics['nb_ref'],
                    'nb_study':       metrics['nb_study'],
                    'score_global':   scores['score_global'],
                    'f1_score':       f1,
                    'distance_used':  layer_dist,
                    'jaccard_used':   layer_jaccard,
                    'params_source':  params_source
                })

                self.progress_signal.emit(int((idx + 1) / total * 90))

            summary_path = None
            if out_dir and all_results:
                self.log('Rédaction des rapports...' if _LANG=='fr' else 'Writing reports...')
                summary_path = write_reports(
                    out_dir, all_results,
                    os.path.basename(layer_ref.source()),
                    layer_ref.featureCount(),
                    ref_crs.authid(),
                    weights, timestamp, _LANG
                )
                self.log(f"{'Rapports enregistrés dans' if _LANG=='fr' else 'Reports saved to'}: {out_dir}")

            self.progress_signal.emit(100)
            self.finished_signal.emit({'results': all_results, 'summary_path': summary_path})

        except Exception as e:
            import traceback
            self.error_signal.emit(f"{str(e)}\n\n{traceback.format_exc()}")


# ============================================================================
# INFO BUTTON  (small "?" button that shows a popup)
# ============================================================================

class InfoButton(QToolButton):
    def __init__(self, help_key, parent=None):
        super().__init__(parent)
        self.help_key = help_key
        self.setText("?")
        self.setFixedSize(18, 18)
        self.setToolTip("Click for help")
        self.setStyleSheet("""
            QToolButton {
                font-size: 10px;
                font-weight: bold;
                color: #555555;
                border: 1px solid #aaaaaa;
                border-radius: 9px;
                background: #f0f0f0;
                padding: 0;
            }
            QToolButton:hover {
                background: #e0e8f0;
                border-color: #5b7dba;
                color: #2a5aa0;
            }
        """)
        self.clicked.connect(self._show_help)

    def _show_help(self):
        text = HELP.get(self.help_key, "No help available.")
        msg = QMessageBox(self.window())
        msg.setWindowTitle("Aide" if _LANG == 'fr' else "Help")
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


def labeled_row(label_text, widget, help_key=None):
    """Returns a QHBoxLayout: label + widget + optional info button."""
    layout = QHBoxLayout()
    layout.setSpacing(6)
    lbl = QLabel(label_text)
    lbl.setMinimumWidth(170)
    layout.addWidget(lbl)
    layout.addWidget(widget, 1)
    if help_key:
        layout.addWidget(InfoButton(help_key))
    return layout


# ============================================================================
# STUDY LAYER ROW WIDGET
# ============================================================================

class StudyLayerRow(QWidget):
    remove_requested = pyqtSignal(object)

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.setSpacing(3)

        # ── Row 1: index + source selector + remove ──────────────────────────
        top = QHBoxLayout()
        top.setSpacing(6)

        self.num_label = QLabel(f"{tr('layer_n')} {self.index}")
        self.num_label.setFixedWidth(52)
        font = self.num_label.font()
        font.setBold(True)
        self.num_label.setFont(font)
        top.addWidget(self.num_label)

        # Toggle: Project layer vs File
        self.radio_project = QRadioButton(tr('from_project'))
        self.radio_file    = QRadioButton(tr('from_file'))
        self.radio_project.setChecked(True)
        self.radio_project.toggled.connect(self._toggle_source)
        top.addWidget(self.radio_project)
        top.addWidget(self.radio_file)
        top.addStretch()

        self.btn_remove = QPushButton(tr('btn_remove'))
        self.btn_remove.setFixedHeight(22)
        self.btn_remove.clicked.connect(lambda: self.remove_requested.emit(self))
        top.addWidget(self.btn_remove)

        outer.addLayout(top)

        # ── Row 2: source widget (combo or file path) ─────────────────────────
        self.stack = QStackedWidget()
        self.stack.setFixedHeight(26)

        self.combo_project = QgsMapLayerComboBox()
        self.combo_project.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.stack.addWidget(self.combo_project)

        file_w = QWidget()
        fl = QHBoxLayout(file_w)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(4)
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText(tr('file_ph'))
        btn_browse = QPushButton(tr('btn_browse'))
        btn_browse.setFixedWidth(70)
        btn_browse.clicked.connect(self._browse)
        fl.addWidget(self.file_edit)
        fl.addWidget(btn_browse)
        self.stack.addWidget(file_w)

        outer.addWidget(self.stack)

        # ── Row 3: alias field ────────────────────────────────────────────────
        alias_row = QHBoxLayout()
        alias_row.setSpacing(6)
        alias_lbl = QLabel(tr('lbl_alias'))
        alias_lbl.setFixedWidth(160)
        alias_lbl.setStyleSheet("color: #555555; font-size: 11px;")
        self.alias_edit = QLineEdit()
        self.alias_edit.setPlaceholderText(tr('alias_ph'))
        self.alias_edit.setFixedHeight(22)
        alias_row.addWidget(alias_lbl)
        alias_row.addWidget(self.alias_edit, 1)
        outer.addLayout(alias_row)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        outer.addWidget(line)

    def _toggle_source(self, checked):
        self.stack.setCurrentIndex(0 if checked else 1)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr('btn_browse'), "", "Vector files (*.shp *.gpkg)"
        )
        if path:
            self.file_edit.setText(path)

    def get_layer(self):
        if self.radio_project.isChecked():
            return self.combo_project.currentLayer()
        path = self.file_edit.text().strip()
        if path and os.path.exists(path):
            name = os.path.splitext(os.path.basename(path))[0]
            lyr = QgsVectorLayer(path, name, "ogr")
            return lyr if lyr.isValid() else None
        return None

    def get_alias(self):
        alias = self.alias_edit.text().strip()
        if alias:
            return alias
        lyr = self.get_layer()
        if lyr:
            return lyr.name()
        return f"Layer {self.index}"

    def set_index(self, idx):
        self.index = idx
        self.num_label.setText(f"{tr('layer_n')} {idx}")


# ============================================================================
# MAIN DIALOG
# ============================================================================

class BuildingQualityDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('title'))
        self.setMinimumSize(680, 820)
        self.resize(720, 880)
        self.worker = None
        self.study_rows = []
        self._detected_crs = None
        self._custom_crs = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Scroll area ───────────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Language toggle
        lang_row = QHBoxLayout()
        lang_row.addStretch()
        self.btn_lang = QPushButton('Fran\u00e7ais')
        self.btn_lang.setFixedSize(72, 22)
        self.btn_lang.clicked.connect(self._toggle_lang)
        lang_row.addWidget(self.btn_lang)
        layout.addLayout(lang_row)

        # ── 1. REFERENCE LAYER ────────────────────────────────────────────────
        grp_ref = self._group(tr('grp_ref'), 'reference_layer')
        self.grp_ref = grp_ref

        self.ref_radio_project = QRadioButton(tr('from_project'))
        self.ref_radio_file    = QRadioButton(tr('from_file'))
        self.ref_radio_project.setChecked(True)
        self.ref_radio_project.toggled.connect(self._toggle_ref_source)

        src_row = QHBoxLayout()
        src_row.addWidget(self.ref_radio_project)
        src_row.addWidget(self.ref_radio_file)
        src_row.addStretch()
        grp_ref.layout().addLayout(src_row)

        self.ref_stack = QStackedWidget()
        self.ref_stack.setFixedHeight(26)

        self.ref_combo = QgsMapLayerComboBox()
        self.ref_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.ref_combo.layerChanged.connect(self._on_ref_layer_changed)
        self.ref_stack.addWidget(self.ref_combo)

        ref_file_w = QWidget()
        rfl = QHBoxLayout(ref_file_w)
        rfl.setContentsMargins(0, 0, 0, 0)
        rfl.setSpacing(4)
        self.ref_file_edit = QLineEdit()
        self.ref_file_edit.setPlaceholderText(tr('ref_ph'))
        self.ref_file_edit.textChanged.connect(self._on_ref_path_changed)
        self.btn_ref_browse = QPushButton(tr('btn_browse'))
        btn_ref_browse = self.btn_ref_browse
        btn_ref_browse.setFixedWidth(70)
        btn_ref_browse.clicked.connect(self._browse_ref)
        rfl.addWidget(self.ref_file_edit)
        rfl.addWidget(btn_ref_browse)
        self.ref_stack.addWidget(ref_file_w)

        grp_ref.layout().addWidget(self.ref_stack)

        self.ref_info_label = QLabel("")
        self.ref_info_label.setStyleSheet("color: #555555; font-size: 11px; margin-top: 2px;")
        grp_ref.layout().addWidget(self.ref_info_label)

        layout.addWidget(grp_ref)

        # ── 2. STUDY LAYERS ───────────────────────────────────────────────────
        grp_study = self._group(tr('grp_study'), 'study_layers')
        self.grp_study = grp_study

        self.study_rows_layout = QVBoxLayout()
        self.study_rows_layout.setSpacing(0)
        grp_study.layout().addLayout(self.study_rows_layout)

        self.btn_add = QPushButton(tr('btn_add_layer'))
        self.btn_add.setFixedWidth(90)
        self.btn_add.clicked.connect(self._add_study_row)
        grp_study.layout().addWidget(self.btn_add, alignment=Qt.AlignLeft)

        self._add_study_row()
        layout.addWidget(grp_study)

        # ── 3. AREA OF INTEREST ───────────────────────────────────────────────
        grp_aoi = self._group(tr('grp_aoi'), 'aoi')
        self.grp_aoi = grp_aoi

        self.chk_aoi = QCheckBox(tr('chk_aoi'))
        self.chk_aoi.toggled.connect(self._toggle_aoi)
        grp_aoi.layout().addWidget(self.chk_aoi)

        self.aoi_widget = QWidget()
        self.aoi_widget.setVisible(False)
        aoi_inner = QVBoxLayout(self.aoi_widget)
        aoi_inner.setContentsMargins(0, 4, 0, 0)
        aoi_inner.setSpacing(4)

        aoi_src_row = QHBoxLayout()
        self.aoi_radio_project = QRadioButton(tr('from_project'))
        self.aoi_radio_file    = QRadioButton(tr('from_file'))
        self.aoi_radio_project.setChecked(True)
        self.aoi_radio_project.toggled.connect(self._toggle_aoi_source)
        aoi_src_row.addWidget(self.aoi_radio_project)
        aoi_src_row.addWidget(self.aoi_radio_file)
        aoi_src_row.addStretch()
        aoi_inner.addLayout(aoi_src_row)

        self.aoi_stack = QStackedWidget()
        self.aoi_stack.setFixedHeight(26)
        self.aoi_combo = QgsMapLayerComboBox()
        self.aoi_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.aoi_stack.addWidget(self.aoi_combo)

        aoi_file_w = QWidget()
        afl = QHBoxLayout(aoi_file_w)
        afl.setContentsMargins(0, 0, 0, 0)
        afl.setSpacing(4)
        self.aoi_file_edit = QLineEdit()
        self.aoi_file_edit.setPlaceholderText(tr('aoi_ph'))
        self.btn_aoi = QPushButton(tr('btn_browse'))
        btn_aoi = self.btn_aoi
        btn_aoi.setFixedWidth(70)
        btn_aoi.clicked.connect(self._browse_aoi)
        afl.addWidget(self.aoi_file_edit)
        afl.addWidget(btn_aoi)
        self.aoi_stack.addWidget(aoi_file_w)

        aoi_inner.addWidget(self.aoi_stack)
        grp_aoi.layout().addWidget(self.aoi_widget)
        layout.addWidget(grp_aoi)

        # ── 4. PROJECTION ─────────────────────────────────────────────────────
        grp_crs = self._group(tr('grp_crs'), 'crs')
        self.grp_crs = grp_crs
        crs_grid = QGridLayout()
        crs_grid.setSpacing(6)
        crs_grid.setColumnStretch(1, 1)

        self.lbl_crs_auto = QLabel(tr('lbl_crs_auto'))
        crs_grid.addWidget(self.lbl_crs_auto, 0, 0)
        self.crs_detected_edit = QLineEdit(tr('crs_placeholder'))
        self.crs_detected_edit.setReadOnly(True)
        crs_grid.addWidget(self.crs_detected_edit, 0, 1)
        crs_grid.addWidget(InfoButton('crs'), 0, 2)

        self.lbl_crs_use = QLabel(tr('lbl_crs_use'))
        crs_grid.addWidget(self.lbl_crs_use, 1, 0)
        crs_pick_row = QHBoxLayout()
        self.crs_combo = QComboBox()
        self.crs_combo.setMinimumWidth(200)
        self.crs_combo.currentIndexChanged.connect(self._on_crs_combo_changed)
        crs_pick_row.addWidget(self.crs_combo, 1)
        self.btn_crs_sel = QPushButton(tr('btn_crs_sel'))
        btn_crs_sel = self.btn_crs_sel
        btn_crs_sel.setFixedWidth(70)
        btn_crs_sel.clicked.connect(self._pick_crs)
        crs_pick_row.addWidget(btn_crs_sel)
        crs_grid.addLayout(crs_pick_row, 1, 1)

        # Warning label (hidden by default)
        self.crs_warning = QLabel(tr('crs_warning'))
        self.crs_warning.setWordWrap(True)
        self.crs_warning.setStyleSheet(
            "color: #cc0000; font-size: 11px; "
            "background: #fff0f0; border: 1px solid #cc0000; "
            "padding: 4px; border-radius: 3px; margin-top: 4px;"
        )
        self.crs_warning.setVisible(False)

        grp_crs.layout().addLayout(crs_grid)
        grp_crs.layout().addWidget(self.crs_warning)
        layout.addWidget(grp_crs)

        # ── 5. MATCHING PARAMETERS ────────────────────────────────────────────
        grp_params = self._group(tr('grp_params'), 'sensitivity')
        self.grp_params = grp_params
        p_layout = QVBoxLayout()
        p_layout.setSpacing(6)

        # Sensitivity analysis toggle
        sens_row = QHBoxLayout()
        self.chk_sensitivity = QCheckBox(tr('chk_sensitivity'))
        self.chk_sensitivity.setChecked(True)
        self.chk_sensitivity.toggled.connect(self._toggle_sensitivity)
        sens_row.addWidget(self.chk_sensitivity)
        sens_row.addWidget(InfoButton('sensitivity'))
        p_layout.addLayout(sens_row)

        # Manual parameters (disabled when sensitivity is on)
        self.manual_widget = QGroupBox(tr('grp_manual'))
        manual_layout = QGridLayout(self.manual_widget)
        manual_layout.setSpacing(6)
        manual_layout.setColumnStretch(1, 1)
        manual_layout.setColumnStretch(3, 1)

        self.lbl_max_dist = QLabel(tr('lbl_max_dist'))
        manual_layout.addWidget(self.lbl_max_dist, 0, 0)
        self.spin_dist = QDoubleSpinBox()
        self.spin_dist.setRange(1, 100)
        self.spin_dist.setValue(10.0)
        self.spin_dist.setSuffix(" m")
        self.spin_dist.setDecimals(1)
        manual_layout.addWidget(self.spin_dist, 0, 1)
        manual_layout.addWidget(InfoButton('max_distance'), 0, 2)

        self.lbl_jaccard = QLabel(tr('lbl_jaccard'))
        manual_layout.addWidget(self.lbl_jaccard, 1, 0)
        self.spin_jaccard = QDoubleSpinBox()
        self.spin_jaccard.setRange(0.1, 1.0)
        self.spin_jaccard.setValue(0.70)
        self.spin_jaccard.setSingleStep(0.05)
        self.spin_jaccard.setDecimals(2)
        manual_layout.addWidget(self.spin_jaccard, 1, 1)
        manual_layout.addWidget(InfoButton('jaccard_min'), 1, 2)

        self.manual_widget.setEnabled(False)
        p_layout.addWidget(self.manual_widget)

        # Match mode
        mode_row = QHBoxLayout()
        self.lbl_match_mode = QLabel(tr('lbl_match_mode'))
        mode_row.addWidget(self.lbl_match_mode)
        self.combo_match_mode = QComboBox()
        self.combo_match_mode.addItems([tr('match_unique'), tr('match_multi')])
        mode_row.addWidget(self.combo_match_mode, 1)
        mode_row.addWidget(InfoButton('match_mode'))
        p_layout.addLayout(mode_row)

        grp_params.layout().addLayout(p_layout)
        layout.addWidget(grp_params)

        # ── 6. SCORE WEIGHTS ─────────────────────────────────────────────────
        grp_weights = self._group(tr('grp_weights'), 'weights')
        self.grp_weights = grp_weights
        w_grid = QGridLayout()
        w_grid.setSpacing(6)
        w_grid.setColumnStretch(1, 1)
        w_grid.setColumnStretch(3, 1)

        self.lbl_w_jac = QLabel(tr('lbl_w_jac'))
        w_grid.addWidget(self.lbl_w_jac, 0, 0)
        self.spin_w_jac = QSpinBox()
        self.spin_w_jac.setRange(0, 100)
        self.spin_w_jac.setValue(42)
        w_grid.addWidget(self.spin_w_jac, 0, 1)

        self.lbl_w_dist = QLabel(tr('lbl_w_dist'))
        w_grid.addWidget(self.lbl_w_dist, 0, 2)
        self.spin_w_dist = QSpinBox()
        self.spin_w_dist.setRange(0, 100)
        self.spin_w_dist.setValue(35)
        w_grid.addWidget(self.spin_w_dist, 0, 3)

        self.lbl_w_area = QLabel(tr('lbl_w_area'))
        w_grid.addWidget(self.lbl_w_area, 1, 0)
        self.spin_w_area = QSpinBox()
        self.spin_w_area.setRange(0, 100)
        self.spin_w_area.setValue(18)
        w_grid.addWidget(self.spin_w_area, 1, 1)

        self.lbl_w_bonus = QLabel(tr('lbl_w_bonus'))
        w_grid.addWidget(self.lbl_w_bonus, 1, 2)
        self.spin_w_bonus = QSpinBox()
        self.spin_w_bonus.setRange(0, 100)
        self.spin_w_bonus.setValue(5)
        w_grid.addWidget(self.spin_w_bonus, 1, 3)

        w_grid.addWidget(InfoButton('weights'), 0, 4, 2, 1, Qt.AlignTop)

        self.weights_note = QLabel(tr('weights_note'))
        self.weights_note.setStyleSheet("color: #555555; font-size: 11px;")
        grp_weights.layout().addLayout(w_grid)
        grp_weights.layout().addWidget(self.weights_note)
        layout.addWidget(grp_weights)

        # ── 7. OUTPUT ─────────────────────────────────────────────────────────
        grp_out = self._group(tr('grp_output'), 'output_dir')
        self.grp_out = grp_out
        out_grid = QGridLayout()
        out_grid.setSpacing(6)
        out_grid.setColumnStretch(1, 1)

        self.lbl_report_dir = QLabel(tr('lbl_report_dir'))
        out_grid.addWidget(self.lbl_report_dir, 0, 0)
        out_row = QHBoxLayout()
        self.out_dir_edit = QLineEdit()
        self.out_dir_edit.setPlaceholderText(tr('out_ph'))
        out_row.addWidget(self.out_dir_edit)
        self.btn_out = QPushButton(tr('btn_browse'))
        btn_out = self.btn_out
        btn_out.setFixedWidth(70)
        btn_out.clicked.connect(self._browse_out)
        out_row.addWidget(btn_out)
        out_grid.addLayout(out_row, 0, 1)
        out_grid.addWidget(InfoButton('output_dir'), 0, 2)

        self.chk_save_layers = QCheckBox(tr('chk_save_layers'))
        self.chk_save_layers.setChecked(False)
        out_grid.addWidget(self.chk_save_layers, 1, 0, 1, 3)
        out_grid.addWidget(InfoButton('save_layers'), 1, 2)

        grp_out.layout().addLayout(out_grid)
        layout.addWidget(grp_out)

        layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── Log panel ─────────────────────────────────────────────────────────
        log_frame = QFrame()
        log_frame.setFixedHeight(150)
        log_frame.setFrameShape(QFrame.StyledPanel)
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(6, 4, 6, 4)
        log_layout.setSpacing(2)

        log_header = QHBoxLayout()
        self.lbl_log = QLabel(tr('lbl_log'))
        log_lbl = self.lbl_log
        log_lbl.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.btn_clear = QPushButton(tr('btn_clear'))
        btn_clear = self.btn_clear
        btn_clear.setFixedSize(50, 18)
        btn_clear.clicked.connect(lambda: self.log_edit.clear())
        log_header.addWidget(log_lbl)
        log_header.addStretch()
        log_header.addWidget(btn_clear)
        log_layout.addLayout(log_header)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Courier New", 9))
        log_layout.addWidget(self.log_edit)

        root.addWidget(log_frame)

        # ── Bottom bar ────────────────────────────────────────────────────────
        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(10, 6, 10, 6)
        bottom_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(14)
        bottom_layout.addWidget(self.progress_bar, 1)

        self.btn_run = QPushButton(tr('btn_run'))
        self.btn_run.setDefault(True)
        self.btn_run.setFixedHeight(30)
        self.btn_run.clicked.connect(self._run)

        self.btn_close = QPushButton(tr('btn_close'))
        btn_close = self.btn_close
        btn_close.setFixedHeight(30)
        btn_close.clicked.connect(self.close)

        bottom_layout.addWidget(self.btn_run)
        bottom_layout.addWidget(btn_close)
        root.addWidget(bottom)

    # ── Helpers ───────────────────────────────────────────────────────────────

    # ── Language toggle ───────────────────────────────────────────────────────

    def _toggle_lang(self):
        global _LANG
        _LANG = 'fr' if _LANG == 'en' else 'en'
        self.btn_lang.setText('English' if _LANG == 'fr' else 'Français')
        self._retranslate()

    def _retranslate(self):
        """Update all translatable labels without rebuilding the UI."""
        self.setWindowTitle(tr('title'))
        self.grp_ref.setTitle(tr('grp_ref'))
        self.grp_study.setTitle(tr('grp_study'))
        self.grp_aoi.setTitle(tr('grp_aoi'))
        self.grp_crs.setTitle(tr('grp_crs'))
        self.grp_params.setTitle(tr('grp_params'))
        self.grp_weights.setTitle(tr('grp_weights'))
        self.grp_out.setTitle(tr('grp_output'))
        # Ref section
        self.ref_radio_project.setText(tr('from_project'))
        self.ref_radio_file.setText(tr('from_file'))
        self.ref_file_edit.setPlaceholderText(tr('ref_ph'))
        self.btn_ref_browse.setText(tr('btn_browse'))
        # Study
        self.btn_add.setText(tr('btn_add_layer'))
        for row in self.study_rows:
            row.radio_project.setText(tr('from_project'))
            row.radio_file.setText(tr('from_file'))
            row.num_label.setText(f"{tr('layer_n')} {row.index}")
            row.btn_remove.setText(tr('btn_remove'))
            row.file_edit.setPlaceholderText(tr('file_ph'))
            row.alias_edit.setPlaceholderText(tr('alias_ph'))
            # alias label is the first QLabel child in the alias row
            for child in row.findChildren(QLabel):
                if child.styleSheet() and '555555' in child.styleSheet():
                    child.setText(tr('lbl_alias'))
                    break
        # AOI
        self.chk_aoi.setText(tr('chk_aoi'))
        self.aoi_radio_project.setText(tr('from_project'))
        self.aoi_radio_file.setText(tr('from_file'))
        self.aoi_file_edit.setPlaceholderText(tr('aoi_ph'))
        self.btn_aoi.setText(tr('btn_browse'))
        # CRS
        self.lbl_crs_auto.setText(tr('lbl_crs_auto'))
        self.lbl_crs_use.setText(tr('lbl_crs_use'))
        self.btn_crs_sel.setText(tr('btn_crs_sel'))
        self.crs_warning.setText(tr('crs_warning'))
        ph_fr = 'sélectionner la couche référence'
        ph_en = 'select reference layer'
        cur = self.crs_detected_edit.text()
        if ph_fr in cur or ph_en in cur:
            self.crs_detected_edit.setText(tr('crs_placeholder'))
        # Params
        self.chk_sensitivity.setText(tr('chk_sensitivity'))
        self.manual_widget.setTitle(tr('grp_manual'))
        self.lbl_max_dist.setText(tr('lbl_max_dist'))
        self.lbl_jaccard.setText(tr('lbl_jaccard'))
        self.lbl_match_mode.setText(tr('lbl_match_mode'))
        cur_idx = self.combo_match_mode.currentIndex()
        self.combo_match_mode.blockSignals(True)
        self.combo_match_mode.clear()
        self.combo_match_mode.addItems([tr('match_unique'), tr('match_multi')])
        self.combo_match_mode.setCurrentIndex(cur_idx)
        self.combo_match_mode.blockSignals(False)
        # Weights
        self.lbl_w_jac.setText(tr('lbl_w_jac'))
        self.lbl_w_dist.setText(tr('lbl_w_dist'))
        self.lbl_w_area.setText(tr('lbl_w_area'))
        self.lbl_w_bonus.setText(tr('lbl_w_bonus'))
        self.weights_note.setText(tr('weights_note'))
        # Output
        self.lbl_report_dir.setText(tr('lbl_report_dir'))
        self.out_dir_edit.setPlaceholderText(tr('out_ph'))
        self.btn_out.setText(tr('btn_browse'))
        self.chk_save_layers.setText(tr('chk_save_layers'))
        # Log / bottom
        self.lbl_log.setText(tr('lbl_log'))
        self.btn_clear.setText(tr('btn_clear'))
        self.btn_run.setText(tr('btn_run'))
        self.btn_close.setText(tr('btn_close'))


    def _group(self, title, help_key=None):
        """Create a QGroupBox with a vertical layout and an optional help button in the title area."""
        grp = QGroupBox(title)
        vbox = QVBoxLayout(grp)
        vbox.setContentsMargins(10, 8, 10, 8)
        vbox.setSpacing(5)
        if help_key:
            # Place an info button at the right of the group box title via a proxy widget
            btn = InfoButton(help_key, grp)
            btn.move(grp.sizeHint().width() - 28, 2)    # approximate; repositioned on resize
            btn.setParent(grp)
            # We keep a reference so the button stays visible
            if not hasattr(self, '_help_buttons'):
                self._help_buttons = []
            self._help_buttons.append((grp, btn, help_key))
        return grp

    def resizeEvent(self, event):
        """Reposition help buttons on group box titles when dialog resizes."""
        super().resizeEvent(event)
        if hasattr(self, '_help_buttons'):
            for grp, btn, _ in self._help_buttons:
                btn.move(grp.width() - 24, 3)

    def _log(self, msg):
        self.log_edit.append(msg)
        self.log_edit.verticalScrollBar().setValue(
            self.log_edit.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

    # ── Study rows ────────────────────────────────────────────────────────────

    def _add_study_row(self):
        if len(self.study_rows) >= 5:
            self._log(tr('log_max_layers'))
            return
        row = StudyLayerRow(len(self.study_rows) + 1, self)
        row.remove_requested.connect(self._remove_study_row)
        self.study_rows.append(row)
        self.study_rows_layout.addWidget(row)

    def _remove_study_row(self, row_widget):
        if len(self.study_rows) <= 1:
            self._log(tr('log_min_layer'))
            return
        self.study_rows.remove(row_widget)
        self.study_rows_layout.removeWidget(row_widget)
        row_widget.deleteLater()
        for i, r in enumerate(self.study_rows):
            r.set_index(i + 1)

    # ── Source toggles ────────────────────────────────────────────────────────

    def _toggle_ref_source(self, project_checked):
        self.ref_stack.setCurrentIndex(0 if project_checked else 1)

    def _toggle_aoi(self, checked):
        self.aoi_widget.setVisible(checked)

    def _toggle_aoi_source(self, project_checked):
        self.aoi_stack.setCurrentIndex(0 if project_checked else 1)

    def _toggle_sensitivity(self, checked):
        self.manual_widget.setEnabled(not checked)

    # ── Browse ────────────────────────────────────────────────────────────────

    def _browse_ref(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr('grp_ref'), "", "Vector files (*.shp *.gpkg)"
        )
        if path:
            self.ref_file_edit.setText(path)

    def _browse_aoi(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr('grp_aoi'), "", "Vector files (*.shp *.gpkg)"
        )
        if path:
            self.aoi_file_edit.setText(path)

    def _browse_out(self):
        d = QFileDialog.getExistingDirectory(self, tr('grp_output'))
        if d:
            self.out_dir_edit.setText(d)

    # ── CRS ───────────────────────────────────────────────────────────────────

    def _on_ref_layer_changed(self, layer):
        if layer:
            self._update_crs(layer)
            n = layer.featureCount()
            self.ref_info_label.setText(
                f"{n} {tr('buildings')}   |   CRS: {layer.crs().authid()}"
            )

    def _on_ref_path_changed(self, path):
        if path and os.path.exists(path):
            lyr = QgsVectorLayer(path, "tmp", "ogr")
            if lyr.isValid():
                self._update_crs(lyr)
                self.ref_info_label.setText(
                    f"{lyr.featureCount()} {tr('buildings')}   |   CRS: {lyr.crs().authid()}"
                )

    def _update_crs(self, layer):
        utm = ensure_metric_crs(layer)
        self._detected_crs = utm
        self.crs_detected_edit.setText(utm.authid())
        self._populate_crs_combo(utm)

    def _populate_crs_combo(self, detected_crs):
        self.crs_combo.blockSignals(True)
        self.crs_combo.clear()
        self.crs_combo.addItem(
            f"{detected_crs.authid()}  ({'auto' if _LANG == 'en' else 'auto-détecté'})",
            detected_crs.authid()
        )
        common = [
            ("EPSG:32618", "UTM 18N  —  Caribbean centre"),
            ("EPSG:32619", "UTM 19N  —  Caribbean east"),
            ("EPSG:32620", "UTM 20N  —  Lesser Antilles"),
            ("EPSG:32621", "UTM 21N  —  Trinidad / Tobago"),
            ("EPSG:32622", "UTM 22N  —  Guyana / Suriname"),
            ("EPSG:32631", "UTM 31N  —  Western Europe"),
            ("EPSG:32632", "UTM 32N  —  Central Europe"),
            ("EPSG:4326",  "WGS84 geographic  (NOT recommended)"),
        ]
        added = {detected_crs.authid()}
        for epsg, label in common:
            if epsg not in added:
                self.crs_combo.addItem(f"{epsg}  —  {label}", epsg)
                added.add(epsg)
        self.crs_combo.blockSignals(False)
        self._on_crs_combo_changed(0)

    def _on_crs_combo_changed(self, idx):
        epsg = self.crs_combo.currentData()
        if epsg:
            crs = QgsCoordinateReferenceSystem(epsg)
            is_metric = is_metric_crs(crs)
            self.crs_warning.setVisible(not is_metric)

    def _pick_crs(self):
        dlg = QgsProjectionSelectionDialog(self)
        if self._detected_crs:
            dlg.setCrs(self._detected_crs)
        if dlg.exec_():
            crs = dlg.crs()
            epsg = crs.authid()
            # Check if already in combo
            for i in range(self.crs_combo.count()):
                if self.crs_combo.itemData(i) == epsg:
                    self.crs_combo.setCurrentIndex(i)
                    return
            self.crs_combo.insertItem(0, f"{epsg}  (custom)", epsg)
            self.crs_combo.setCurrentIndex(0)

    def _get_chosen_crs(self):
        epsg = self.crs_combo.currentData()
        if epsg:
            return QgsCoordinateReferenceSystem(epsg)
        return self._detected_crs

    # ── Getters ───────────────────────────────────────────────────────────────

    def _get_ref_layer(self):
        if self.ref_radio_project.isChecked():
            return self.ref_combo.currentLayer()
        path = self.ref_file_edit.text().strip()
        if path and os.path.exists(path):
            lyr = QgsVectorLayer(path, "Reference", "ogr")
            return lyr if lyr.isValid() else None
        return None

    def _get_weights(self):
        total = (self.spin_w_jac.value() + self.spin_w_dist.value() +
                 self.spin_w_area.value() + self.spin_w_bonus.value()) or 1
        return {
            'jaccard':  self.spin_w_jac.value()   / total,
            'distance': self.spin_w_dist.value()  / total,
            'area':     self.spin_w_area.value()  / total,
            'bonus':    self.spin_w_bonus.value() / total,
        }

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate(self):
        if not self._get_ref_layer():
            QMessageBox.warning(self, tr('validation'), tr('val_ref'))
            return False
        items = [r for r in self.study_rows if r.get_layer() is not None]
        if not items:
            QMessageBox.warning(self, tr('validation'), tr('val_study'))
            return False
        if not self.crs_combo.count():
            QMessageBox.warning(self, tr('validation'), tr('val_crs'))
            return False
        crs = self._get_chosen_crs()
        if crs and not is_metric_crs(crs):
            ans = QMessageBox.warning(
                self, tr('non_metric_title'), tr('val_crs_metric'),
                QMessageBox.Yes | QMessageBox.No
            )
            if ans == QMessageBox.No:
                return False
        return True

    # ── Run ───────────────────────────────────────────────────────────────────

    def _run(self):
        if not self._validate():
            return

        layer_ref = self._get_ref_layer()
        study_items = [
            {'layer': r.get_layer(), 'alias': r.get_alias()}
            for r in self.study_rows
            if r.get_layer() is not None
        ]
        ref_crs   = self._get_chosen_crs()
        weights   = self._get_weights()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        # Add reference to project if loaded from file
        if not QgsProject.instance().mapLayer(layer_ref.id()):
            QgsProject.instance().addMapLayer(layer_ref)
        apply_outline_style(layer_ref, "orange")

        params = {
            'layer_ref':      layer_ref,
            'study_items':    study_items,
            'ref_crs':        ref_crs,
            'weights':        weights,
            'allow_multiple': self.combo_match_mode.currentIndex() == 1,
            'max_dist':       self.spin_dist.value(),
            'jaccard_min':    self.spin_jaccard.value(),
            'use_sensitivity':self.chk_sensitivity.isChecked(),
            'out_dir':        self.out_dir_edit.text().strip() or None,
            'save_layers':    self.chk_save_layers.isChecked(),
            'timestamp':      timestamp,
        }

        self.btn_run.setEnabled(False)
        self.btn_run.setText(tr('btn_running'))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._log(f"{tr('log_started')}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"{tr('log_reference')}: {layer_ref.name()}  ({layer_ref.featureCount()} {tr('buildings')})")
        self._log(f"{tr('log_crs')}: {ref_crs.authid()}")
        self._log(f"{tr('log_layers')}: {len(study_items)}")
        self._log(f"{tr('log_sensitivity')}: {tr('log_yes') if params['use_sensitivity'] else tr('log_no')}")
        self._log(f"{'─'*60}")

        self.worker = AnalysisWorker(params)
        self.worker.log_signal.connect(self._log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_done(self, result):
        self.btn_run.setEnabled(True)
        self.btn_run.setText(tr('btn_run'))
        self.progress_bar.setVisible(False)

        results = result.get('results', [])
        summary_path = result.get('summary_path')

        self._log(f"\n{'─'*60}")
        self._log(tr('log_complete'))
        self._log(f"{'─'*60}")

        if results:
            self._log(f"\n{tr('log_ranking')}")
            for rank, r in enumerate(
                sorted(results, key=lambda x: x['score_global'], reverse=True), 1
            ):
                self._log(
                    f"  {rank}. {r['alias']:<35}  "
                    f"Score: {r['score_global']*100:.1f}%  |  "
                    f"F1: {r['f1_score']:.1f}%  |  "
                    f"Completeness: {r['completeness']:.1f}%  |  "
                    f"Commission: {r['commission']:.1f}%"
                )

        if summary_path:
            self._log(f"\n{tr('log_report')}: {summary_path}")

        QMessageBox.information(
            self, tr('done_title'),
            f"{len(results)}{tr('done_msg')}"
            + (f"{tr('done_report')}{summary_path}" if summary_path else "")
        )

    def _on_error(self, err):
        self.btn_run.setEnabled(True)
        self.btn_run.setText(tr('btn_run'))
        self.progress_bar.setVisible(False)
        self._log(f"\n{tr('log_error')}:\n{err}")
        QMessageBox.critical(self, tr('err_title'), f"{tr('err_msg')}\n\n{err[:600]}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def show_dialog():
    dlg = BuildingQualityDialog()
    dlg.show()
    return dlg

_dlg = show_dialog()
