# -*- coding: utf-8 -*-
"""
Population per Building — QGIS Dialog Script
Dasymetric disaggregation of WorldPop population to building level
using WSF3D building height raster and household settings.
Auteur: Fabrice RENOUX, Eunice WOUODA DONGMO, Mohamed SECK
Version corrigée - Février 2026

Usage: Run from QGIS Script Editor or Python Console
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QLineEdit, QFileDialog,
    QWidget, QScrollArea, QProgressBar, QTextEdit,
    QFrame, QMessageBox, QApplication, QStackedWidget,
    QRadioButton, QToolButton
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QUrl
from qgis.PyQt.QtGui import QColor, QFont, QDesktopServices

from qgis.core import (
    QgsVectorLayer, QgsRasterLayer, QgsProject,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsUnitTypes, QgsMapLayerProxyModel,
    QgsVectorFileWriter,
    QgsGraduatedSymbolRenderer, QgsRendererRange,
    QgsFillSymbol
)
from qgis.gui import QgsMapLayerComboBox, QgsProjectionSelectionDialog

import processing
import os
from datetime import datetime


# ============================================================================
# LANGUAGE
# ============================================================================

_LANG = 'fr'

T = {
    'title':           {'fr': 'Population par bâtiment',          'en': 'Population per Building'},
    'grp_input':       {'fr': "Données d'entrée",                  'en': 'Input Data'},
    'grp_crs':         {'fr': 'Projection / CRS',                  'en': 'Projection / CRS'},
    'grp_settings':    {'fr': 'Paramètres ménages (obligatoire)',  'en': 'Household Settings (required)'},
    'grp_output':      {'fr': 'Couche de sortie',                  'en': 'Output Layer'},
    'lbl_aoi':         {'fr': "Zone d'étude (AOI) :",              'en': 'Study area (AOI):'},
    'lbl_building':    {'fr': 'Couche bâti (polygones) :',         'en': 'Building layer (polygons):'},
    'lbl_wsf3d':       {'fr': 'Raster WSF3D (hauteur) :',          'en': 'WSF3D Raster (height):'},
    'lbl_worldpop':    {'fr': 'Raster WorldPop (population) :',    'en': 'WorldPop Raster (population):'},
    'lbl_dl_wsf':      {'fr': 'Télécharger WSF3D (site DLR)...',   'en': 'Download WSF3D (DLR site)...'},
    'lbl_dl_wp':       {'fr': 'Télécharger WorldPop...',           'en': 'Download WorldPop...'},
    'lbl_crs_auto':    {'fr': 'CRS détecté (auto) :',              'en': 'Auto-detected CRS:'},
    'lbl_crs_use':     {'fr': 'CRS à utiliser :',                  'en': 'CRS to use:'},
    'btn_crs_sel':     {'fr': 'Sélectionner...',                   'en': 'Select...'},
    'crs_placeholder': {'fr': "(sélectionner la couche AOI d'abord)", 'en': '(select AOI layer first)'},
    'crs_warning':     {'fr': ("Attention : CRS non métrique. Les calculs de surface "
                               "seront incorrects. Choisir un CRS UTM."),
                        'en': ("Warning: non-metric CRS. Area calculations will be "
                               "incorrect. Please choose a UTM CRS.")},
    'lbl_hh_size':     {'fr': 'Personnes / ménage (moy.) :',       'en': 'Persons / household (avg.):'},
    'lbl_floor_h':     {'fr': 'Hauteur par étage (m) :',           'en': 'Floor height (m):'},
    'lbl_min_m2':      {'fr': 'Surface min. / ménage (m²) :',      'en': 'Min area / household (m²):'},
    'lbl_max_m2':      {'fr': 'Surface max. / ménage (m²) :',      'en': 'Max area / household (m²):'},
    'settings_note':   {'fr': ("Ces paramètres sont obligatoires. Ils permettent d'estimer "
                               "le nombre d'étages et la capacité d'accueil de chaque bâtiment."),
                        'en': ("These settings are required. They are used to estimate "
                               "the number of floors and the realistic capacity of each building.")},
    'radio_temp':      {'fr': 'Couche temporaire dans le projet',   'en': 'Temporary layer in project'},
    'radio_file':      {'fr': 'Enregistrer sur disque',             'en': 'Save to disk'},
    'lbl_out_file':    {'fr': 'Fichier de sortie :',                'en': 'Output file:'},
    'btn_browse':      {'fr': 'Parcourir...',                       'en': 'Browse...'},
    'btn_run':         {'fr': "Lancer l'analyse",                   'en': 'Run analysis'},
    'btn_running':     {'fr': 'Analyse en cours...',                'en': 'Running...'},
    'btn_close':       {'fr': 'Fermer',                             'en': 'Close'},
    'btn_clear':       {'fr': 'Effacer',                            'en': 'Clear'},
    'lbl_log':         {'fr': "Journal d'exécution",                'en': 'Execution log'},
    'from_project':    {'fr': 'Depuis le projet',                   'en': 'From project'},
    'from_file':       {'fr': 'Depuis un fichier',                  'en': 'From file'},
    'validation':      {'fr': 'Validation',                         'en': 'Validation'},
    'val_aoi':         {'fr': 'Sélectionnez une couche AOI valide.',  'en': 'Select a valid AOI layer.'},
    'val_building':    {'fr': 'Sélectionnez une couche bâti valide.', 'en': 'Select a valid building layer.'},
    'val_wsf3d':       {'fr': 'Sélectionnez le raster WSF3D valide.', 'en': 'Select a valid WSF3D raster.'},
    'val_worldpop':    {'fr': 'Sélectionnez le raster WorldPop valide.', 'en': 'Select a valid WorldPop raster.'},
    'val_crs':         {'fr': "Aucun CRS. Sélectionnez la couche AOI d'abord.",
                        'en': 'No CRS. Select the AOI layer first.'},
    'val_crs_metric':  {'fr': "CRS non métrique. Continuer quand même ?",
                        'en': 'Non-metric CRS. Continue anyway?'},
    'val_out_path':    {'fr': 'Spécifiez un chemin de fichier de sortie.',
                        'en': 'Specify an output file path.'},
    'val_min_max':     {'fr': 'La surface min. ne peut pas être > à la surface max.',
                        'en': 'Min area cannot be greater than max area.'},
    'val_hh':          {'fr': 'Le nombre de personnes par ménage doit être > 0.',
                        'en': 'Persons per household must be > 0.'},
    'val_floor_h':     {'fr': 'La hauteur par étage doit être > 0.',
                        'en': 'Floor height must be > 0.'},
    'non_metric_title':{'fr': 'CRS non métrique',                   'en': 'Non-metric CRS'},
    'done_title':      {'fr': 'Analyse terminée',                   'en': 'Analysis complete'},
    'err_title':       {'fr': 'Erreur',                             'en': 'Error'},
    'err_invalid_out': {'fr': "La couche de sortie n'a pas pu être créée.",
                        'en': 'The output layer could not be created.'},
    'done_msg':        {'fr': ("Couches ajoutées au projet QGIS.\n\n"
                               "Colonnes produites :\n"
                               "  area_m2       surface au sol (m²)\n"
                               "  h_mean        hauteur WSF3D moyenne (m)\n"
                               "  nb_floors     nombre d'étages estimé\n"
                               "  volume        volume total (m³)\n"
                               "  pop_cell      population cellule WorldPop\n"
                               "  Pop_raw       population par volume (méthode classique)\n"
                               "  Pop_settings  population par capacité ménages\n\n"
                               "Symbologie gradée jaune → rouge appliquée sur Pop_settings."),
                        'en': ("Layer added to the QGIS project.\n\n"
                               "Produced columns:\n"
                               "  area_m2       footprint area (m²)\n"
                               "  h_mean        mean WSF3D height (m)\n"
                               "  nb_floors     estimated number of floors\n"
                               "  volume        total volume (m³)\n"
                               "  pop_cell      WorldPop cell population\n"
                               "  Pop_raw       population by volume (classic method)\n"
                               "  Pop_settings  population by household capacity\n\n"
                               "Graduated yellow → red symbology applied to Pop_settings.")},
}

def tr(key):
    return T.get(key, {}).get(_LANG, T.get(key, {}).get('fr', key))


# ============================================================================
# HELP TEXTS
# ============================================================================

HELP = {
    'aoi': {
        'fr': ("Zone d'étude (AOI)\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Polygone délimitant la zone d'analyse. Tous les rasters et la couche bâti "
               "sont découpés sur cette emprise avant traitement.\n\nFormat : .shp ou .gpkg"),
        'en': ("Area of Interest (AOI)\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Polygon delimiting the analysis area. All rasters and the building layer "
               "are clipped to this extent before processing.\n\nFormat: .shp or .gpkg")
    },
    'building': {
        'fr': ("Couche bâti\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Polygones des empreintes au sol des bâtiments (OSM, Microsoft, Google, cadastre…).\n\n"
               "Chaque bâtiment reçoit deux estimations de population en sortie."),
        'en': ("Building layer\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Building footprint polygons (OSM, Microsoft, Google, cadastral data…).\n\n"
               "Each building receives two population estimates in the output.")
    },
    'wsf3d': {
        'fr': ("Raster WSF3D — Hauteur bâtiments\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Raster de hauteur de bâti (DLR). Résolution 90 m, valeurs en mètres.\n"
               "Fichier : WSF3D_V02_BuildingHeight\n\n"
               "Si la hauteur est NoData, 1 × hauteur_étage est utilisé par défaut."),
        'en': ("WSF3D Raster — Building Height\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Building height raster (DLR). 90 m resolution, values in metres.\n"
               "File: WSF3D_V02_BuildingHeight\n\n"
               "If height is NoData, 1 × floor_height is used as fallback.")
    },
    'worldpop': {
        'fr': ("Raster WorldPop — Population\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Raster de population WorldPop (100 m). Chaque pixel = estimation du nombre "
               "d'habitants dans cette cellule.\n\n"
               "Téléchargement : https://hub.worldpop.org/geodata/listing?id=135"),
        'en': ("WorldPop Raster — Population\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "WorldPop population raster (100 m resolution). Each pixel = estimated "
               "population count for that cell.\n\n"
               "Download: https://hub.worldpop.org/geodata/listing?id=135")
    },
    'crs': {
        'fr': ("Projection / CRS\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Un CRS métrique (en mètres) est obligatoire pour les calculs de surface.\n\n"
               "Le CRS UTM adapté est détecté automatiquement depuis l'AOI.\n\n"
               "ATTENTION : WGS84 (EPSG:4326) donne des surfaces en degrés carrés, "
               "rendant les estimations de population totalement incorrectes."),
        'en': ("Projection / CRS\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "A metric CRS (in metres) is required for area calculations.\n\n"
               "The appropriate UTM CRS is auto-detected from the AOI extent.\n\n"
               "WARNING: WGS84 (EPSG:4326) produces areas in square degrees, "
               "making population estimates completely wrong.")
    },
    'settings': {
        'fr': ("Paramètres ménages\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Personnes / ménage : taille moyenne d'un ménage (défaut 5).\n\n"
               "Hauteur par étage : utilisée pour calculer\n"
               "  nb_floors = max(1, round(h_mean / floor_h))\n\n"
               "Surface min. / ménage : surface minimale occupée par un ménage.\n"
               "Surface max. / ménage : surface maximale (limite les grands bâtiments).\n\n"
               "Méthode Pop_settings :\n"
               "  surface_utile = area_m2 × nb_floors\n"
               "  capacité = (surface_utile / avg_m2) × hh_size\n"
               "  Pop_settings = (capacité_bâtiment / Σ capacités cellule) × pop_cellule\n\n"
               "Pop_raw utilise la méthode classique par volume (m³)."),
        'en': ("Household Settings\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Persons / household: average household size (default 5).\n\n"
               "Floor height: used to compute\n"
               "  nb_floors = max(1, round(h_mean / floor_h))\n\n"
               "Min area / household: minimum area occupied by one household.\n"
               "Max area / household: maximum area (limits large buildings).\n\n"
               "Pop_settings method:\n"
               "  usable_area = area_m2 × nb_floors\n"
               "  capacity = (usable_area / avg_m2) × hh_size\n"
               "  Pop_settings = (building_capacity / Σ cell capacities) × cell_pop\n\n"
               "Pop_raw uses the classic volume-based method (m³).")
    },
    'output': {
        'fr': ("Couche de sortie\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Pop_raw       : désagrégation par volume WSF3D (méthode classique)\n"
               "Pop_settings  : désagrégation par capacité ménages\n\n"
               "La symbologie gradée jaune → rouge est appliquée sur Pop_settings.\n"
               "Format recommandé : GeoPackage (.gpkg)."),
        'en': ("Output Layer\n"
               "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
               "Pop_raw       : disaggregation by WSF3D volume (classic method)\n"
               "Pop_settings  : disaggregation by household capacity\n\n"
               "Graduated yellow → red symbology applied to Pop_settings.\n"
               "Recommended format: GeoPackage (.gpkg).")
    },
}

def help_text(key):
    return HELP.get(key, {}).get(_LANG, HELP.get(key, {}).get('fr', ''))


# ============================================================================
# INFO BUTTON
# ============================================================================

class InfoButton(QToolButton):
    def __init__(self, help_key, parent=None):
        super().__init__(parent)
        self.help_key = help_key
        self.setText("?")
        self.setFixedSize(18, 18)
        self.setStyleSheet("""
            QToolButton {
                font-size: 10px; font-weight: bold; color: #555;
                border: 1px solid #aaa; border-radius: 9px;
                background: #f0f0f0; padding: 0;
            }
            QToolButton:hover { background: #e0e8f0; border-color: #5b7dba; color: #2a5aa0; }
        """)
        self.clicked.connect(self._show)

    def _show(self):
        msg = QMessageBox(self.window())
        msg.setWindowTitle("Aide" if _LANG == 'fr' else "Help")
        msg.setText(help_text(self.help_key))
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


# ============================================================================
# LAYER SOURCE WIDGET
# ============================================================================

class LayerSourceWidget(QWidget):
    def __init__(self, layer_type='vector', parent=None):
        super().__init__(parent)
        self.layer_type = layer_type
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        radio_row = QHBoxLayout()
        radio_row.setSpacing(12)
        self.radio_project = QRadioButton(tr('from_project'))
        self.radio_file    = QRadioButton(tr('from_file'))
        self.radio_project.setChecked(True)
        self.radio_project.toggled.connect(self._toggle)
        radio_row.addWidget(self.radio_project)
        radio_row.addWidget(self.radio_file)
        radio_row.addStretch()
        layout.addLayout(radio_row)

        self.stack = QStackedWidget()
        self.stack.setFixedHeight(26)

        self.combo = QgsMapLayerComboBox()
        if self.layer_type == 'vector':
            self.combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        else:
            self.combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.stack.addWidget(self.combo)

        file_w = QWidget()
        fl = QHBoxLayout(file_w)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(4)
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("...")
        ext = ("Fichiers vecteur (*.shp *.gpkg)" if self.layer_type == 'vector'
               else "Fichiers raster (*.tif *.tiff *.img *.vrt)")
        self.btn_browse = QPushButton(tr('btn_browse'))
        self.btn_browse.setFixedWidth(80)
        self.btn_browse.clicked.connect(lambda: self._browse(ext))
        fl.addWidget(self.file_edit)
        fl.addWidget(self.btn_browse)
        self.stack.addWidget(file_w)
        layout.addWidget(self.stack)

    def _toggle(self, checked):
        self.stack.setCurrentIndex(0 if checked else 1)

    def _browse(self, ext):
        path, _ = QFileDialog.getOpenFileName(self, "", "", ext)
        if path:
            self.file_edit.setText(path)

    def get_layer(self, name="layer"):
        """Returns a QgsVectorLayer or QgsRasterLayer, or None."""
        if self.radio_project.isChecked():
            lyr = self.combo.currentLayer()
            return lyr  # may be None — caller checks
        path = self.file_edit.text().strip()
        if not path or not os.path.exists(path):
            return None
        if self.layer_type == 'vector':
            lyr = QgsVectorLayer(path, name, "ogr")
        else:
            lyr = QgsRasterLayer(path, name)
        return lyr if lyr.isValid() else None


# ============================================================================
# CRS UTILITIES
# ============================================================================

def find_utm_crs(layer):
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
        epsg = f"326{zone:02d}" if lat >= 0 else f"327{zone:02d}"
        return QgsCoordinateReferenceSystem(f"EPSG:{epsg}")
    except Exception:
        return QgsCoordinateReferenceSystem("EPSG:32631")

def is_metric(crs):
    return crs.mapUnits() == QgsUnitTypes.DistanceMeters


# ============================================================================
# GRADUATED SYMBOLOGY  (Jenks natural breaks)
# ============================================================================

def apply_graduated_style(layer, field='Pop_settings', n_classes=5):
    """
    Apply a yellow-to-red graduated renderer using Jenks natural breaks.
    Falls back to quantile classification if QgsClassificationJenks is
    not available (QGIS < 3.10).
    Buildings with 0 population get a separate grey class.
    """
    try:
        pop_idx = layer.fields().indexOf(field)
        if pop_idx < 0:
            return

        # Collect non-zero values for Jenks (zero gets its own class)
        all_vals, nonzero_vals = [], []
        for f in layer.getFeatures():
            v = f.attributes()[pop_idx]
            if v is not None:
                try:
                    fv = float(v)
                    all_vals.append(fv)
                    if fv > 0:
                        nonzero_vals.append(fv)
                except (TypeError, ValueError):
                    pass

        if not all_vals:
            return

        has_zeros = any(v == 0 for v in all_vals)
        vals_for_breaks = nonzero_vals if (has_zeros and nonzero_vals) else all_vals

        # ── Compute Jenks breaks ──────────────────────────────────────────────
        breaks = _jenks_breaks(vals_for_breaks, n_classes)
        if len(breaks) < 2:
            return

        # ── Colour ramp: yellow → orange → red ───────────────────────────────
        ramp = [QColor('#FFFF00'), QColor('#FFB300'),
                QColor('#FF6600'), QColor('#FF2200'), QColor('#CC0000')]

        def lerp(t):
            if t <= 0: return ramp[0]
            if t >= 1: return ramp[-1]
            seg = t * (len(ramp) - 1)
            i0 = int(seg); i1 = min(i0 + 1, len(ramp) - 1)
            f = seg - i0
            c0, c1 = ramp[i0], ramp[i1]
            return QColor(int(c0.red()+f*(c1.red()-c0.red())),
                          int(c0.green()+f*(c1.green()-c0.green())),
                          int(c0.blue()+f*(c1.blue()-c0.blue())))

        ranges = []

        # Class 0: buildings with zero population (grey)
        if has_zeros:
            sym0 = QgsFillSymbol.createSimple({
                'color': '#88cccccc', 'outline_color': '#66888888',
                'outline_width': '0.15', 'style': 'solid'})
            ranges.append(QgsRendererRange(0, 0, sym0, "0"))

        # Jenks classes
        n_ranges = len(breaks) - 1
        for i in range(n_ranges):
            lo, hi = breaks[i], breaks[i + 1]
            if lo == 0 and hi == 0:
                continue
            col = lerp(i / max(n_ranges - 1, 1))
            col.setAlpha(210)
            sym = QgsFillSymbol.createSimple({
                'color': col.name(QColor.HexArgb),
                'outline_color': '#80505050',
                'outline_width': '0.2', 'style': 'solid'})
            ranges.append(QgsRendererRange(lo, hi, sym,
                                           f"{int(lo)} – {int(hi)}"))

        renderer = QgsGraduatedSymbolRenderer(field, ranges)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        layer.emitStyleChanged()

    except Exception as e:
        print(f"[graduated_style] {e}")


def _jenks_breaks(values, n_classes):
    """
    Compute Jenks natural breaks using QgsClassificationJenks when available
    (QGIS >= 3.10).  Falls back to a pure-Python implementation otherwise.
    Returns a sorted list of break points (n_classes + 1 values).
    """
    if not values:
        return []

    n_classes = min(n_classes, len(set(values)))

    # ── Try native QGIS Jenks ─────────────────────────────────────────────────
    try:
        from qgis.core import QgsClassificationJenks
        clf = QgsClassificationJenks()
        # classify() returns a list of QgsClassificationRange
        ranges = clf.classes(values, n_classes)
        if ranges:
            breaks = [ranges[0].lowerBound()]
            for r in ranges:
                breaks.append(r.upperBound())
            return sorted(set(breaks))
    except (ImportError, AttributeError, Exception):
        pass  # fall through to Python implementation

    # ── Pure-Python Jenks (Fisher-Jenks / Jenks-Caspall) ────────────────────
    # Uses the O(kn^2) dynamic programming approach — fast enough for
    # typical building datasets (< 100 000 features).
    data = sorted(values)
    n = len(data)
    k = n_classes

    if n <= k:
        return sorted(set([data[0]] + data + [data[-1]]))

    # lower_class_limits[i][j] = optimal lower class limit for class j ending at i
    # variance_combinations[i][j] = within-class variance for class j ending at i
    inf = float('inf')
    llc  = [[0] * (k + 1) for _ in range(n + 1)]
    vrc  = [[inf] * (k + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        llc[i][1] = 1
        vrc[i][1] = 0.0
        s1 = s2 = 0.0
        for m in range(1, i + 1):
            v = data[m - 1]
            s2 += v * v
            s1 += v
            cnt = i - m + 1
            variance = s2 - (s1 * s1) / cnt
            if m > 1:
                for j in range(2, k + 1):
                    if vrc[i][j] >= variance + vrc[m - 1][j - 1]:
                        llc[i][j] = m
                        vrc[i][j] = variance + vrc[m - 1][j - 1]

    # Trace back class limits
    kclass = [0] * (k + 1)
    kclass[k] = n
    for j in range(k, 1, -1):
        kclass[j - 1] = llc[kclass[j]][j] - 1

    breaks = [data[0]]
    for j in range(1, k + 1):
        idx = kclass[j]
        if idx < n:
            breaks.append(data[idx])
        else:
            breaks.append(data[-1])

    return sorted(set(breaks))


# ============================================================================
# WORKER THREAD
# ============================================================================

class PopWorker(QThread):
    log_signal      = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(object)
    error_signal    = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        try:
            p = self.params
            layer_aoi       = p['layer_aoi']
            layer_building  = p['layer_building']
            raster_wsf3d    = p['raster_wsf3d']
            raster_worldpop = p['raster_worldpop']
            crs_id          = p['crs_id']
            out_path        = p['out_path']
            hh_size         = float(p['hh_size'])
            min_m2          = float(p['min_m2'])
            max_m2          = float(p['max_m2'])
            floor_h         = float(p['floor_h'])
            avg_m2          = (min_m2 + max_m2) / 2.0

            total_steps = 15
            step = [0]

            def alg(name, alg_params, label):
                step[0] += 1
                self.log(f"  [{step[0]}/{total_steps}] {label}")
                r = processing.run(name, alg_params)
                self.progress_signal.emit(int(step[0] / total_steps * 88))
                return r

            # 1. Clip building
            r = alg('native:clip', {
                'INPUT': layer_building, 'OVERLAY': layer_aoi,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Clip buildings to AOI")
            bld = r['OUTPUT']

            # 2. Clip WSF3D
            r = alg('gdal:cliprasterbymasklayer', {
                'INPUT': raster_wsf3d, 'MASK': layer_aoi,
                'CROP_TO_CUTLINE': True, 'ALPHA_BAND': False,
                'DATA_TYPE': 0, 'KEEP_RESOLUTION': False, 'MULTITHREADING': False,
                'NODATA': None, 'OPTIONS': None, 'EXTRA': None,
                'SOURCE_CRS': 'ProjectCrs', 'TARGET_CRS': None,
                'TARGET_EXTENT': None, 'X_RESOLUTION': None, 'Y_RESOLUTION': None,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Clip WSF3D to AOI")
            wsf_clip = r['OUTPUT']

            # 3. Clip WorldPop
            r = alg('gdal:cliprasterbymasklayer', {
                'INPUT': raster_worldpop, 'MASK': layer_aoi,
                'CROP_TO_CUTLINE': True, 'ALPHA_BAND': False,
                'DATA_TYPE': 0, 'KEEP_RESOLUTION': False, 'MULTITHREADING': False,
                'NODATA': None, 'OPTIONS': None, 'EXTRA': None,
                'SOURCE_CRS': 'ProjectCrs', 'TARGET_CRS': None,
                'TARGET_EXTENT': None, 'X_RESOLUTION': None, 'Y_RESOLUTION': None,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Clip WorldPop to AOI")
            wp_clip = r['OUTPUT']

            # 4. Zonal stats — mean height
            r = alg('native:zonalstatisticsfb', {
                'INPUT': bld, 'INPUT_RASTER': wsf_clip,
                'RASTER_BAND': 1, 'COLUMN_PREFIX': 'h_',
                'STATISTICS': [2], 'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Extract mean height (WSF3D zonal stats)")
            bld = r['OUTPUT']

            # 5. Reproject to metric CRS
            r = alg('native:reprojectlayer', {
                'INPUT': bld,
                'TARGET_CRS': QgsCoordinateReferenceSystem(crs_id),
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, f"Reproject to {crs_id}")
            bld = r['OUTPUT']

            # 6. area_m2
            r = alg('native:fieldcalculator', {
                'INPUT': bld, 'FIELD_NAME': 'area_m2',
                'FIELD_TYPE': 0, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 2,
                'FORMULA': '$area', 'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Compute footprint area (m²)")
            bld = r['OUTPUT']

            # 7. nb_floors
            r = alg('native:fieldcalculator', {
                'INPUT': bld, 'FIELD_NAME': 'nb_floors',
                'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                'FORMULA': f'max(1, round(coalesce("h_mean", {floor_h}) / {floor_h}))',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Compute number of floors")
            bld = r['OUTPUT']

            # 8. volume (for Pop_raw)
            r = alg('native:fieldcalculator', {
                'INPUT': bld, 'FIELD_NAME': 'volume',
                'FIELD_TYPE': 0, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 2,
                'FORMULA': f'"area_m2" * coalesce("h_mean", {floor_h})',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Compute building volume (m³)")
            bld = r['OUTPUT']

            # 9. capacity (for Pop_settings)
            # usable_area = area_m2 * nb_floors
            # capacity = (usable_area / avg_m2) * hh_size
            r = alg('native:fieldcalculator', {
                'INPUT': bld, 'FIELD_NAME': 'capacity',
                'FIELD_TYPE': 0, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 3,
                'FORMULA': f'("area_m2" * "nb_floors" / {avg_m2}) * {hh_size}',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Compute household capacity per building")
            bld = r['OUTPUT']

            # 10. Polygonize WorldPop
            r = alg('gdal:polygonize', {
                'INPUT': wp_clip, 'BAND': 1, 'FIELD': 'pop_cell',
                'EIGHT_CONNECTEDNESS': False, 'EXTRA': None,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Vectorise WorldPop cells")
            wp_cells = r['OUTPUT']

            # 11. cell_id
            r = alg('native:fieldcalculator', {
                'INPUT': wp_cells, 'FIELD_NAME': 'cell_id',
                'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                'FORMULA': '@id', 'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Add cell identifier")
            wp_cells = r['OUTPUT']

            # 12. Centroids + spatial join
            r = alg('native:centroids', {
                'INPUT': bld, 'ALL_PARTS': True,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Compute building centroids")
            centroids = r['OUTPUT']

            r = alg('native:joinattributesbylocation', {
                'INPUT': centroids, 'JOIN': wp_cells,
                'JOIN_FIELDS': ['cell_id', 'pop_cell'],
                'METHOD': 0, 'PREDICATE': [0],
                'DISCARD_NONMATCHING': False, 'PREFIX': None,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Join centroids to WorldPop cells")
            centroids_wp = r['OUTPUT']

            # 13. Join cell info to building polygon layer
            r = alg('native:joinattributestable', {
                'INPUT': bld, 'FIELD': 'fid',
                'INPUT_2': centroids_wp, 'FIELD_2': 'fid',
                'FIELDS_TO_COPY': ['cell_id', 'pop_cell'],
                'METHOD': 1, 'DISCARD_NONMATCHING': False,
                'PREFIX': None, 'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Join cell attributes to buildings")
            bld = r['OUTPUT']

            # 14. Sum volume per cell → Pop_raw
            r = alg('qgis:statisticsbycategories', {
                'INPUT': bld, 'VALUES_FIELD_NAME': 'volume',
                'CATEGORIES_FIELD_NAME': ['cell_id'],
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }, "Sum volume per WorldPop cell")
            vol_stats = r['OUTPUT']

            r = processing.run('native:joinattributestable', {
                'INPUT': bld, 'FIELD': 'cell_id',
                'INPUT_2': vol_stats, 'FIELD_2': 'cell_id',
                'FIELDS_TO_COPY': ['sum'], 'METHOD': 1,
                'DISCARD_NONMATCHING': False, 'PREFIX': 'v_',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            bld = r['OUTPUT']

            # 15. Sum capacity per cell → Pop_settings + compute both columns
            r = processing.run('qgis:statisticsbycategories', {
                'INPUT': bld, 'VALUES_FIELD_NAME': 'capacity',
                'CATEGORIES_FIELD_NAME': ['cell_id'],
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            cap_stats = r['OUTPUT']

            r = processing.run('native:joinattributestable', {
                'INPUT': bld, 'FIELD': 'cell_id',
                'INPUT_2': cap_stats, 'FIELD_2': 'cell_id',
                'FIELDS_TO_COPY': ['sum'], 'METHOD': 1,
                'DISCARD_NONMATCHING': False, 'PREFIX': 'c_',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            bld = r['OUTPUT']

            step[0] += 1
            self.log(f"  [{step[0]}/{total_steps}] Compute Pop_raw and Pop_settings")
            self.progress_signal.emit(91)

            # Pop_raw
            r = processing.run('native:fieldcalculator', {
                'INPUT': bld, 'FIELD_NAME': 'Pop_raw',
                'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                'FORMULA': 'round(if("v_sum" > 0, ("volume" / "v_sum") * "pop_cell", 0))',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            bld = r['OUTPUT']

            # Pop_settings
            r = processing.run('native:fieldcalculator', {
                'INPUT': bld, 'FIELD_NAME': 'Pop_settings',
                'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                'FORMULA': 'round(if("c_sum" > 0, ("capacity" / "c_sum") * "pop_cell", 0))',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            bld = r['OUTPUT']

            # Remove temporary helper columns
            r = processing.run('native:deletecolumn', {
                'INPUT': bld,
                'COLUMN': ['v_sum', 'c_sum', 'capacity'],
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            bld_clean = r['OUTPUT']

            self.progress_signal.emit(95)

            # Save or keep temporary
            # bld_clean may be a QgsVectorLayer object or a string path — handle both
            if isinstance(bld_clean, str):
                src_lyr = QgsVectorLayer(bld_clean, "tmp", "ogr")
            else:
                src_lyr = bld_clean   # already a QgsVectorLayer

            if out_path:
                self.log(f"  Saving to: {out_path}")
                drv = "GPKG" if out_path.lower().endswith('.gpkg') else "ESRI Shapefile"
                QgsVectorFileWriter.writeAsVectorFormat(
                    src_lyr, out_path, "UTF-8", src_lyr.crs(), drv)
                final_layer = QgsVectorLayer(out_path, "Population per Building", "ogr")
            else:
                src_lyr.setName("Population per Building")
                final_layer = src_lyr

            self.progress_signal.emit(100)
            self.finished_signal.emit(final_layer)

        except Exception as e:
            import traceback
            self.error_signal.emit(f"{str(e)}\n\n{traceback.format_exc()}")


# ============================================================================
# MAIN DIALOG
# ============================================================================

class PopBuildingDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('title'))
        self.setMinimumSize(660, 790)
        self.resize(700, 840)
        self.worker = None
        self._detected_crs = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

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
        self.btn_lang = QPushButton("English")
        self.btn_lang.setFixedSize(68, 22)
        self.btn_lang.clicked.connect(self._toggle_lang)
        lang_row.addWidget(self.btn_lang)
        layout.addLayout(lang_row)

        # ── 1. INPUT ──────────────────────────────────────────────────────────
        self.grp_in = self._grp(tr('grp_input'))

        def inp_row(label_key, help_key, ltype):
            row = QHBoxLayout()
            lbl = QLabel(tr(label_key))
            lbl.setFixedWidth(210)
            src = LayerSourceWidget(ltype)
            row.addWidget(lbl)
            row.addWidget(src, 1)
            row.addWidget(InfoButton(help_key))
            return row, lbl, src

        self.row_aoi,  self.lbl_aoi,  self.src_aoi      = inp_row('lbl_aoi',      'aoi',      'vector')
        self.row_bld,  self.lbl_bld,  self.src_building  = inp_row('lbl_building', 'building', 'vector')
        self.row_wsf,  self.lbl_wsf,  self.src_wsf3d     = inp_row('lbl_wsf3d',   'wsf3d',    'raster')
        self.row_wp,   self.lbl_wp,   self.src_worldpop  = inp_row('lbl_worldpop','worldpop', 'raster')

        self.src_aoi.combo.layerChanged.connect(self._on_aoi_changed)

        # Add rows in order, with download links placed just below their layer
        link_style = "color:#2255aa;text-decoration:underline;text-align:left;border:none;font-size:11px;"

        self.grp_in.layout().addLayout(self.row_aoi)
        self.grp_in.layout().addLayout(self.row_bld)

        # WSF3D row + download link
        self.grp_in.layout().addLayout(self.row_wsf)
        self.btn_dl_wsf = QPushButton(tr('lbl_dl_wsf'))
        self.btn_dl_wsf.setFlat(True)
        self.btn_dl_wsf.setStyleSheet(link_style)
        self.btn_dl_wsf.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://download.geoservice.dlr.de/WSF3D/files/global/")))
        self.grp_in.layout().addWidget(self.btn_dl_wsf)

        # WorldPop row + download link
        self.grp_in.layout().addLayout(self.row_wp)
        self.btn_dl_wp = QPushButton(tr('lbl_dl_wp'))
        self.btn_dl_wp.setFlat(True)
        self.btn_dl_wp.setStyleSheet(link_style)
        self.btn_dl_wp.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://hub.worldpop.org/geodata/listing?id=135")))
        self.grp_in.layout().addWidget(self.btn_dl_wp)

        layout.addWidget(self.grp_in)

        # ── 2. CRS ────────────────────────────────────────────────────────────
        self.grp_crs = self._grp(tr('grp_crs'))
        g = QGridLayout()
        g.setSpacing(6)
        g.setColumnStretch(1, 1)

        self.lbl_crs_auto = QLabel(tr('lbl_crs_auto'))
        g.addWidget(self.lbl_crs_auto, 0, 0)
        self.crs_detected_edit = QLineEdit(tr('crs_placeholder'))
        self.crs_detected_edit.setReadOnly(True)
        g.addWidget(self.crs_detected_edit, 0, 1)
        g.addWidget(InfoButton('crs'), 0, 2)

        self.lbl_crs_use = QLabel(tr('lbl_crs_use'))
        g.addWidget(self.lbl_crs_use, 1, 0)
        crs_pick = QHBoxLayout()
        self.crs_combo = QComboBox()
        self.crs_combo.setMinimumWidth(220)
        self.crs_combo.currentIndexChanged.connect(self._on_crs_changed)
        crs_pick.addWidget(self.crs_combo, 1)
        self.btn_crs_sel = QPushButton(tr('btn_crs_sel'))
        self.btn_crs_sel.setFixedWidth(100)
        self.btn_crs_sel.clicked.connect(self._pick_crs)
        crs_pick.addWidget(self.btn_crs_sel)
        g.addLayout(crs_pick, 1, 1)

        self.crs_warning = QLabel(tr('crs_warning'))
        self.crs_warning.setWordWrap(True)
        self.crs_warning.setStyleSheet(
            "color:#cc0000;font-size:11px;background:#fff0f0;"
            "border:1px solid #cc0000;padding:4px;border-radius:3px;margin-top:4px;")
        self.crs_warning.setVisible(False)

        self.grp_crs.layout().addLayout(g)
        self.grp_crs.layout().addWidget(self.crs_warning)
        layout.addWidget(self.grp_crs)

        # ── 3. HOUSEHOLD SETTINGS ─────────────────────────────────────────────
        self.grp_hh = self._grp(tr('grp_settings'))
        self.hh_note = QLabel(tr('settings_note'))
        self.hh_note.setWordWrap(True)
        self.hh_note.setStyleSheet("color:#555;font-size:11px;")
        self.grp_hh.layout().addWidget(self.hh_note)

        hg = QGridLayout()
        hg.setSpacing(8)
        hg.setColumnStretch(1, 1)
        hg.setColumnStretch(3, 1)

        self.lbl_hh_size = QLabel(tr('lbl_hh_size'))
        hg.addWidget(self.lbl_hh_size, 0, 0)
        self.spin_hh = QDoubleSpinBox()
        self.spin_hh.setRange(0.1, 50); self.spin_hh.setValue(5.0)
        self.spin_hh.setDecimals(1); self.spin_hh.setSuffix(" pers.")
        hg.addWidget(self.spin_hh, 0, 1)

        self.lbl_floor_h = QLabel(tr('lbl_floor_h'))
        hg.addWidget(self.lbl_floor_h, 0, 2)
        self.spin_floor = QDoubleSpinBox()
        self.spin_floor.setRange(1.0, 20.0); self.spin_floor.setValue(3.0)
        self.spin_floor.setDecimals(1); self.spin_floor.setSuffix(" m")
        hg.addWidget(self.spin_floor, 0, 3)
        hg.addWidget(InfoButton('settings'), 0, 4)

        self.lbl_min_m2 = QLabel(tr('lbl_min_m2'))
        hg.addWidget(self.lbl_min_m2, 1, 0)
        self.spin_min = QDoubleSpinBox()
        self.spin_min.setRange(1, 500); self.spin_min.setValue(10.0)
        self.spin_min.setDecimals(0); self.spin_min.setSuffix(" m²")
        hg.addWidget(self.spin_min, 1, 1)

        self.lbl_max_m2 = QLabel(tr('lbl_max_m2'))
        hg.addWidget(self.lbl_max_m2, 1, 2)
        self.spin_max = QDoubleSpinBox()
        self.spin_max.setRange(1, 5000); self.spin_max.setValue(100.0)
        self.spin_max.setDecimals(0); self.spin_max.setSuffix(" m²")
        hg.addWidget(self.spin_max, 1, 3)

        self.grp_hh.layout().addLayout(hg)
        layout.addWidget(self.grp_hh)

        # ── 4. OUTPUT ─────────────────────────────────────────────────────────
        self.grp_out = self._grp(tr('grp_output'))
        out_top = QHBoxLayout()
        self.radio_temp = QRadioButton(tr('radio_temp'))
        self.radio_file = QRadioButton(tr('radio_file'))
        self.radio_temp.setChecked(True)
        self.radio_temp.toggled.connect(lambda c: self.out_file_w.setVisible(not c))
        out_top.addWidget(self.radio_temp)
        out_top.addWidget(self.radio_file)
        out_top.addStretch()
        out_top.addWidget(InfoButton('output'))
        self.grp_out.layout().addLayout(out_top)

        self.out_file_w = QWidget()
        self.out_file_w.setVisible(False)
        ofl = QHBoxLayout(self.out_file_w)
        ofl.setContentsMargins(0, 0, 0, 0); ofl.setSpacing(4)
        self.lbl_out = QLabel(tr('lbl_out_file'))
        self.lbl_out.setFixedWidth(100)
        ofl.addWidget(self.lbl_out)
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("output.gpkg / output.shp")
        ofl.addWidget(self.out_edit, 1)
        self.btn_out = QPushButton(tr('btn_browse'))
        self.btn_out.setFixedWidth(80)
        self.btn_out.clicked.connect(self._browse_out)
        ofl.addWidget(self.btn_out)
        self.grp_out.layout().addWidget(self.out_file_w)

        layout.addWidget(self.grp_out)
        layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── Log ───────────────────────────────────────────────────────────────
        log_frame = QFrame()
        log_frame.setFixedHeight(140)
        log_frame.setFrameShape(QFrame.StyledPanel)
        ll = QVBoxLayout(log_frame)
        ll.setContentsMargins(6, 4, 6, 4); ll.setSpacing(2)
        lh = QHBoxLayout()
        self.lbl_log = QLabel(tr('lbl_log'))
        self.lbl_log.setStyleSheet("font-weight:bold;font-size:11px;")
        self.btn_clear = QPushButton(tr('btn_clear'))
        self.btn_clear.setFixedSize(60, 18)
        self.btn_clear.clicked.connect(lambda: self.log_edit.clear())
        lh.addWidget(self.lbl_log); lh.addStretch(); lh.addWidget(self.btn_clear)
        ll.addLayout(lh)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Courier New", 9))
        ll.addWidget(self.log_edit)
        root.addWidget(log_frame)

        # ── Bottom bar ────────────────────────────────────────────────────────
        bot_frame = QFrame()
        bot_frame.setFrameShape(QFrame.StyledPanel)
        bl = QHBoxLayout(bot_frame)
        bl.setContentsMargins(10, 6, 10, 6); bl.setSpacing(8)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(14)
        bl.addWidget(self.progress_bar, 1)
        self.btn_run = QPushButton(tr('btn_run'))
        self.btn_run.setDefault(True); self.btn_run.setFixedHeight(30)
        self.btn_run.clicked.connect(self._run)
        self.btn_close = QPushButton(tr('btn_close'))
        self.btn_close.setFixedHeight(30)
        self.btn_close.clicked.connect(self.close)
        bl.addWidget(self.btn_run); bl.addWidget(self.btn_close)
        root.addWidget(bot_frame)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _grp(self, title):
        grp = QGroupBox(title)
        vb = QVBoxLayout(grp)
        vb.setContentsMargins(10, 8, 10, 8); vb.setSpacing(5)
        return grp

    def _log(self, msg):
        self.log_edit.append(msg)
        self.log_edit.verticalScrollBar().setValue(
            self.log_edit.verticalScrollBar().maximum())
        QApplication.processEvents()

    def _browse_out(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "", "", "GeoPackage (*.gpkg);;Shapefile (*.shp)")
        if path:
            self.out_edit.setText(path)

    # ── Language ──────────────────────────────────────────────────────────────

    def _toggle_lang(self):
        global _LANG
        _LANG = 'en' if _LANG == 'fr' else 'fr'
        self.btn_lang.setText("Français" if _LANG == 'en' else "English")
        self._retranslate()

    def _retranslate(self):
        self.setWindowTitle(tr('title'))
        self.grp_in.setTitle(tr('grp_input'))
        self.grp_crs.setTitle(tr('grp_crs'))
        self.grp_hh.setTitle(tr('grp_settings'))
        self.grp_out.setTitle(tr('grp_output'))
        self.lbl_aoi.setText(tr('lbl_aoi'))
        self.lbl_bld.setText(tr('lbl_building'))
        self.lbl_wsf.setText(tr('lbl_wsf3d'))
        self.lbl_wp.setText(tr('lbl_worldpop'))
        self.btn_dl_wsf.setText(tr('lbl_dl_wsf'))
        self.btn_dl_wp.setText(tr('lbl_dl_wp'))
        self.lbl_crs_auto.setText(tr('lbl_crs_auto'))
        self.lbl_crs_use.setText(tr('lbl_crs_use'))
        self.btn_crs_sel.setText(tr('btn_crs_sel'))
        self.crs_warning.setText(tr('crs_warning'))
        self.hh_note.setText(tr('settings_note'))
        self.lbl_hh_size.setText(tr('lbl_hh_size'))
        self.lbl_floor_h.setText(tr('lbl_floor_h'))
        self.lbl_min_m2.setText(tr('lbl_min_m2'))
        self.lbl_max_m2.setText(tr('lbl_max_m2'))
        self.radio_temp.setText(tr('radio_temp'))
        self.radio_file.setText(tr('radio_file'))
        self.lbl_out.setText(tr('lbl_out_file'))
        self.btn_out.setText(tr('btn_browse'))
        self.btn_run.setText(tr('btn_run'))
        self.btn_close.setText(tr('btn_close'))
        self.lbl_log.setText(tr('lbl_log'))
        self.btn_clear.setText(tr('btn_clear'))
        ph_key_fr = T['crs_placeholder']['fr']
        ph_key_en = T['crs_placeholder']['en']
        if self.crs_detected_edit.text() in (ph_key_fr, ph_key_en):
            self.crs_detected_edit.setText(tr('crs_placeholder'))
        for src in [self.src_aoi, self.src_building, self.src_wsf3d, self.src_worldpop]:
            src.radio_project.setText(tr('from_project'))
            src.radio_file.setText(tr('from_file'))
            src.btn_browse.setText(tr('btn_browse'))

    # ── CRS ───────────────────────────────────────────────────────────────────

    def _on_aoi_changed(self, layer):
        if layer:
            utm = find_utm_crs(layer)
            self._detected_crs = utm
            self.crs_detected_edit.setText(utm.authid())
            self._populate_crs_combo(utm)

    def _populate_crs_combo(self, detected):
        self.crs_combo.blockSignals(True)
        self.crs_combo.clear()
        self.crs_combo.addItem(f"{detected.authid()}  (auto)", detected.authid())
        common = [
            ("EPSG:32618", "UTM 18N — Caribbean centre"),
            ("EPSG:32619", "UTM 19N — Caribbean east"),
            ("EPSG:32620", "UTM 20N — Lesser Antilles"),
            ("EPSG:32621", "UTM 21N — Trinidad"),
            ("EPSG:32622", "UTM 22N — Guyana"),
            ("EPSG:32628", "UTM 28N — West Africa"),
            ("EPSG:32631", "UTM 31N — W. Europe"),
            ("EPSG:32632", "UTM 32N — C. Europe"),
            ("EPSG:32637", "UTM 37N — E. Africa"),
            ("EPSG:4326",  "WGS84 geographic (NOT recommended)"),
        ]
        added = {detected.authid()}
        for epsg, label in common:
            if epsg not in added:
                self.crs_combo.addItem(f"{epsg}  —  {label}", epsg)
                added.add(epsg)
        self.crs_combo.blockSignals(False)
        self._on_crs_changed(0)

    def _on_crs_changed(self, _):
        epsg = self.crs_combo.currentData()
        if epsg:
            self.crs_warning.setVisible(
                not is_metric(QgsCoordinateReferenceSystem(epsg)))

    def _pick_crs(self):
        dlg = QgsProjectionSelectionDialog(self)
        if self._detected_crs:
            dlg.setCrs(self._detected_crs)
        if dlg.exec_():
            crs = dlg.crs(); epsg = crs.authid()
            for i in range(self.crs_combo.count()):
                if self.crs_combo.itemData(i) == epsg:
                    self.crs_combo.setCurrentIndex(i); return
            self.crs_combo.insertItem(0, f"{epsg}  (custom)", epsg)
            self.crs_combo.setCurrentIndex(0)

    def _get_crs(self):
        epsg = self.crs_combo.currentData()
        return epsg or (self._detected_crs.authid() if self._detected_crs else "EPSG:32631")

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate(self):
        for lyr, key in [(self.src_aoi.get_layer("AOI"),          'val_aoi'),
                         (self.src_building.get_layer("Building"), 'val_building'),
                         (self.src_wsf3d.get_layer("WSF3D"),       'val_wsf3d'),
                         (self.src_worldpop.get_layer("WorldPop"), 'val_worldpop')]:
            if not lyr:
                QMessageBox.warning(self, tr('validation'), tr(key)); return False

        if not self.crs_combo.count():
            QMessageBox.warning(self, tr('validation'), tr('val_crs')); return False

        epsg = self._get_crs()
        if not is_metric(QgsCoordinateReferenceSystem(epsg)):
            if QMessageBox.warning(self, tr('non_metric_title'), tr('val_crs_metric'),
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return False

        if self.spin_hh.value() <= 0:
            QMessageBox.warning(self, tr('validation'), tr('val_hh')); return False
        if self.spin_floor.value() <= 0:
            QMessageBox.warning(self, tr('validation'), tr('val_floor_h')); return False
        if self.spin_min.value() > self.spin_max.value():
            QMessageBox.warning(self, tr('validation'), tr('val_min_max')); return False
        if self.radio_file.isChecked() and not self.out_edit.text().strip():
            QMessageBox.warning(self, tr('validation'), tr('val_out_path')); return False
        return True

    # ── Run ───────────────────────────────────────────────────────────────────

    def _run(self):
        if not self._validate():
            return

        layer_aoi       = self.src_aoi.get_layer("AOI")
        layer_building  = self.src_building.get_layer("Building")
        raster_wsf3d    = self.src_wsf3d.get_layer("WSF3D")
        raster_worldpop = self.src_worldpop.get_layer("WorldPop")

        proj = QgsProject.instance()
        for lyr in [layer_aoi, layer_building, raster_wsf3d, raster_worldpop]:
            if lyr and not proj.mapLayer(lyr.id()):
                proj.addMapLayer(lyr, False)

        out_path = self.out_edit.text().strip() if self.radio_file.isChecked() else None

        params = {
            'layer_aoi':       layer_aoi,
            'layer_building':  layer_building,
            'raster_wsf3d':    raster_wsf3d,
            'raster_worldpop': raster_worldpop,
            'crs_id':          self._get_crs(),
            'out_path':        out_path,
            'hh_size':         self.spin_hh.value(),
            'min_m2':          self.spin_min.value(),
            'max_m2':          self.spin_max.value(),
            'floor_h':         self.spin_floor.value(),
        }

        self.btn_run.setEnabled(False)
        self.btn_run.setText(tr('btn_running'))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._log("=" * 55)
        self._log(f"Start  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"  AOI        : {layer_aoi.name()}")
        self._log(f"  Buildings  : {layer_building.name()} ({layer_building.featureCount()})")
        self._log(f"  WSF3D      : {raster_wsf3d.name()}")
        self._log(f"  WorldPop   : {raster_worldpop.name()}")
        self._log(f"  CRS        : {params['crs_id']}")
        self._log(f"  HH size    : {params['hh_size']} pers.")
        self._log(f"  Floor ht   : {params['floor_h']} m")
        self._log(f"  m²/hh      : {params['min_m2']} – {params['max_m2']} m²")
        self._log(f"  Output     : {out_path or 'temporary'}")
        self._log("-" * 55)

        self.worker = PopWorker(params)
        self.worker.log_signal.connect(self._log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_done(self, final_layer):
        self.btn_run.setEnabled(True)
        self.btn_run.setText(tr('btn_run'))
        self.progress_bar.setVisible(False)

        if final_layer and final_layer.isValid():
            QgsProject.instance().addMapLayer(final_layer)
            self._log("  Applying graduated symbology (Pop_settings)...")
            apply_graduated_style(final_layer, field='Pop_settings', n_classes=5)
            self._log("-" * 55)
            self._log("Analysis complete.")
            self._log(f"  Layer    : {final_layer.name()}")
            self._log(f"  Features : {final_layer.featureCount()}")
            self._log("  Columns  : area_m2, h_mean, nb_floors, volume,")
            self._log("             pop_cell, Pop_raw, Pop_settings")
            QMessageBox.information(self, tr('done_title'), tr('done_msg'))
        else:
            self._log("Error: output layer is invalid.")
            QMessageBox.warning(self, tr('err_title'), tr('err_invalid_out'))

    def _on_error(self, err):
        self.btn_run.setEnabled(True)
        self.btn_run.setText(tr('btn_run'))
        self.progress_bar.setVisible(False)
        self._log(f"\nERROR:\n{err}")
        QMessageBox.critical(self, tr('err_title'), f"{err[:700]}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def show_dialog():
    dlg = PopBuildingDialog()
    dlg.show()
    return dlg

_dlg = show_dialog()