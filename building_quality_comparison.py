from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsSpatialIndex,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsApplication,
    QgsSymbol,
    QgsSingleSymbolRenderer,
    QgsLineSymbol,
    QgsPointXY,
    QgsUnitTypes,
    QgsArrowSymbolLayer
)
from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtGui import QColor
from datetime import datetime
import os
import statistics

project = QgsProject.instance()
QgsApplication.processEvents()

# ==================================================
# FONCTIONS STATISTIQUES ROBUSTES
# ==================================================
def calculate_mad(values):
    """Calcule le MAD (Median Absolute Deviation)"""
    if not values:
        return 0
    median_val = statistics.median(values)
    deviations = [abs(v - median_val) for v in values]
    return statistics.median(deviations)


def identify_significant_differences(values, threshold=1.96):
    """Identifie les valeurs significativement différentes de la médiane"""
    if not values:
        return []
    
    median_val = statistics.median(values)
    mad = calculate_mad(values)
    
    if mad == 0:
        return []
    
    significant = []
    for v in values:
        if abs(v - median_val) > threshold * mad:
            significant.append(True)
        else:
            significant.append(False)
    
    return significant


# ==================================================
# FONCTIONS STYLE
# ==================================================
def apply_outline_style(layer, color):
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    if symbol is None:
        return

    symbol_layer = symbol.symbolLayer(0)
    if symbol_layer is None:
        return

    # Remplissage transparent
    symbol.setColor(QColor(0, 0, 0, 0))

    # Contour
    symbol_layer.setStrokeColor(QColor(color))
    symbol_layer.setStrokeWidth(1.2)

    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


def apply_arrow_style(layer):
    """Style pour lignes en pointillés avec flèche bleue"""
    symbol = QgsLineSymbol()
    
    # Couche de flèche
    arrow_layer = QgsArrowSymbolLayer.create({
        'arrow_width': '0.2',
        'arrow_width_at_start': '0',
        'head_length': '1.5',
        'head_thickness': '1',
        'head_type': '0',  # 0 = triangle
        'arrow_type': '0',  # 0 = flèche simple
        'is_curved': '0',
        'is_repeated': '0',
        'offset': '0'
    })
    
    arrow_layer.setColor(QColor('blue'))
    
    # Accéder au sub-symbol de la flèche et modifier son style
    sub_symbol = arrow_layer.subSymbol()
    if sub_symbol:
        sub_symbol.setColor(QColor('blue'))
        # Appliquer le style pointillé au premier symbol layer
        if sub_symbol.symbolLayerCount() > 0:
            sub_layer = sub_symbol.symbolLayer(0)
            sub_layer.setStrokeStyle(Qt.DotLine)
            sub_layer.setStrokeWidth(0.4)
            sub_layer.setStrokeColor(QColor('blue'))
    
    symbol.changeSymbolLayer(0, arrow_layer)
    
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


# ==================================================
# 1. COUCHE DE RÉFÉRENCE
# ==================================================
ref_path, _ = QFileDialog.getOpenFileName(
    None, "Couche de référence (bâti)", "", "Vector (*.shp *.gpkg)"
)
if not ref_path:
    raise Exception("Annulé")

layer_ref = QgsVectorLayer(ref_path, "REF_buildings", "ogr")
if not layer_ref.isValid():
    raise Exception("Erreur chargement couche référence")

project.addMapLayer(layer_ref)
apply_outline_style(layer_ref, "orange")

# ==================================================
# 2. COUCHES À ÉVALUER
# ==================================================
study_paths, _ = QFileDialog.getOpenFileNames(
    None, "Couches à évaluer (1 à 5)", "", "Vector (*.shp *.gpkg)"
)
if not study_paths or len(study_paths) > 5:
    raise Exception("Nombre de couches invalide")

# ==================================================
# 3. DOSSIER DE SORTIE
# ==================================================
out_dir = QFileDialog.getExistingDirectory(None, "Dossier de sortie")
if not out_dir:
    raise Exception("Annulé")

# ==================================================
# 4. PARAMÈTRES
# ==================================================
MAX_DIST, ok = QInputDialog.getDouble(
    None, "Distance max",
    "Distance max entre centroïdes (m):",
    10, 0, 1000, 1
)
if not ok:
    raise Exception("Annulé")

SEUIL_OVERLAP, ok = QInputDialog.getDouble(
    None, "Recouvrement minimal",
    "Recouvrement minimal (%) :",
    50, 0, 100, 1
)
if not ok:
    raise Exception("Annulé")
SEUIL_OVERLAP /= 100

# Permettre appariements multiples
ALLOW_MULTIPLE, ok = QInputDialog.getInt(
    None, "Appariements multiples",
    "Autoriser appariements multiples ?\n0 = Non (appariement unique)\n1 = Oui (plusieurs correspondances possibles)",
    0, 0, 1, 1
)
if not ok:
    raise Exception("Annulé")
ALLOW_MULTIPLE = bool(ALLOW_MULTIPLE)

# ==================================================
# 5. CRS MÉTRIQUE AUTO (UTM)
# ==================================================
def find_best_utm_crs(layer):
    src_crs = layer.crs()
    extent = layer.extent()

    center = QgsPointXY(
        (extent.xMinimum() + extent.xMaximum()) / 2,
        (extent.yMinimum() + extent.yMaximum()) / 2
    )

    wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    transform = QgsCoordinateTransform(src_crs, wgs84, project)
    center_wgs = transform.transform(center)

    lon = center_wgs.x()
    lat = center_wgs.y()

    zone = int((lon + 180) / 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone

    return QgsCoordinateReferenceSystem(f"EPSG:{epsg}")

ref_crs = find_best_utm_crs(layer_ref)

if ref_crs.mapUnits() != QgsUnitTypes.DistanceMeters:
    raise Exception("CRS métrique non détecté")

QMessageBox.information(
    None,
    "CRS automatique",
    f"CRS métrique détecté : {ref_crs.authid()}"
)

# ==================================================
# 6. INDEX SPATIAL RÉFÉRENCE + ID_BUILDING
# ==================================================
ref_transform = None
if layer_ref.crs() != ref_crs:
    ref_transform = QgsCoordinateTransform(layer_ref.crs(), ref_crs, project)

ref_index = QgsSpatialIndex()
ref_features = {}

# Créer un ID unique pour chaque bâtiment de référence
for idx, f in enumerate(layer_ref.getFeatures()):
    geom = QgsGeometry(f.geometry())
    if ref_transform:
        geom.transform(ref_transform)
    geom = geom.makeValid()

    id_building = f"REF_{idx+1:06d}"  # Ex: REF_000001, REF_000002...

    ref_features[f.id()] = {
        "geom": geom,
        "centroid": geom.centroid(),
        "attrs": f.attributes(),
        "id_building": id_building
    }

    temp_feat = QgsFeature()
    temp_feat.setGeometry(geom)
    temp_feat.setId(f.id())
    ref_index.insertFeature(temp_feat)

# ==================================================
# 7. FICHIER TEXTE - EN-TÊTE COMPLET
# ==================================================
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
summary_path = os.path.join(out_dir, f"comparison_summary_{timestamp}.txt")

with open(summary_path, "w", encoding="utf-8") as f:

    f.write("ÉVALUATION QUALITÉ – BÂTI\n")
    f.write("=" * 50 + "\n\n")
    
    f.write(f"Couche de référence : {os.path.basename(ref_path)}\n")
    f.write(f"Nombre de bâtiments référence : {layer_ref.featureCount()}\n")
    f.write(f"Distance max : {MAX_DIST} m\n")
    f.write(f"Seuil recouvrement : {SEUIL_OVERLAP*100:.1f} %\n")
    f.write(f"Mode appariement : {'Multiple (1:n)' if ALLOW_MULTIPLE else 'Unique (1:1)'}\n")
    f.write(f"CRS : {ref_crs.authid()}\n")
    f.write(f"Date d'analyse : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("DÉFINITION DES INDICATEURS\n")
    f.write("-" * 50 + "\n")
    f.write("• Exhaustivité : part des bâtiments de référence détectés\n")
    f.write("• Sur-complétude : part de bâtiments en trop dans la couche évaluée\n")
    f.write("• Indice de recouvrement : qualité surfacique du chevauchement\n")
    f.write("• Distance moyenne/médiane : précision positionnelle des appariements\n")
    f.write("• MAD : Median Absolute Deviation (dispersion robuste)\n\n")
    f.write("=" * 50 + "\n\n")

    # ==================================================
    # 8. TRAITEMENT DES COUCHES
    # ==================================================
    
    # Stocker les résultats de chaque couche pour la synthèse
    all_results = []
    
    for idx, study_path in enumerate(study_paths):

        QgsApplication.processEvents()

        layer_study = QgsVectorLayer(study_path, os.path.basename(study_path), "ogr")
        if not layer_study.isValid():
            continue

        study_transform = None
        if layer_study.crs() != ref_crs:
            study_transform = QgsCoordinateTransform(
                layer_study.crs(), ref_crs, project
            )

        matched_ref_ids = set()
        matched_study_ids = set()
        distances = []
        area_differences = []
        surface_ref_appariee = 0
        surface_intersection_totale = 0
        
        # Dictionnaire pour stocker les infos d'appariement
        match_info = {}
        
        if ALLOW_MULTIPLE:
            # Mode multiples : autoriser 1:n
            ref_matches_count = {}
        else:
            # Mode unique : forcer 1:1
            ref_best_matches = {}

        # ===== COUCHE REF NON DÉTECTÉS =====
        ref_non_detectes_layer = QgsVectorLayer(
            f"Polygon?crs={ref_crs.authid()}",
            f"REF_NON_DETECTES_{os.path.basename(study_path)}",
            "memory"
        )
        ref_non_detectes_layer.dataProvider().addAttributes(layer_ref.fields())
        ref_non_detectes_layer.dataProvider().addAttributes([
            QgsField("ID_building", QVariant.String)
        ])
        ref_non_detectes_layer.updateFields()

        # ===== COUCHE APPARIÉS (ÉTUDE) avec attributs enrichis =====
        study_matched_layer = QgsVectorLayer(
            f"Polygon?crs={ref_crs.authid()}",
            f"BATI_ETUDE_APPARIES_{os.path.basename(study_path)}",
            "memory"
        )
        study_matched_layer.dataProvider().addAttributes(layer_study.fields())
        study_matched_layer.dataProvider().addAttributes([
            QgsField("ID_building", QVariant.String),
            QgsField("dist_m", QVariant.Double),
            QgsField("overlap_pct", QVariant.Double)
        ])
        study_matched_layer.updateFields()

        # ===== COUCHE NON APPARIÉS (ÉTUDE) =====
        study_remaining_layer = QgsVectorLayer(
            f"Polygon?crs={ref_crs.authid()}",
            f"BATI_ETUDE_NON_APPARIES_{os.path.basename(study_path)}",
            "memory"
        )
        study_remaining_layer.dataProvider().addAttributes(layer_study.fields())
        study_remaining_layer.updateFields()

        # ===== COUCHE LIGNES DE LIAISON =====
        link_layer = QgsVectorLayer(
            f"LineString?crs={ref_crs.authid()}",
            f"LIAISONS_{os.path.basename(study_path)}",
            "memory"
        )
        link_layer.dataProvider().addAttributes([
            QgsField("ID_building", QVariant.String),
            QgsField("dist_m", QVariant.Double)
        ])
        link_layer.updateFields()

        # ===== PHASE 1 : TROUVER TOUS LES CANDIDATS =====
        study_features = {}
        
        for study_feat in layer_study.getFeatures():

            geom = QgsGeometry(study_feat.geometry())
            if study_transform:
                geom.transform(study_transform)
            geom = geom.makeValid()

            study_features[study_feat.id()] = {
                "geom": geom,
                "centroid": geom.centroid(),
                "attrs": study_feat.attributes()
            }

            centroid = geom.centroid()
            candidate_ids = ref_index.intersects(
                centroid.buffer(MAX_DIST, 8).boundingBox()
            )

            for cid in candidate_ids:

                ref_geom = ref_features[cid]["geom"]
                dist = centroid.distance(ref_features[cid]["centroid"])

                if dist > MAX_DIST:
                    continue

                inter = geom.intersection(ref_geom)
                if inter.isEmpty():
                    continue

                overlap = inter.area() / ref_geom.area()

                if overlap >= SEUIL_OVERLAP:
                    
                    area_diff = geom.area() - ref_geom.area()
                    
                    if ALLOW_MULTIPLE:
                        # Mode multiple : accepter tous les matchs
                        if study_feat.id() not in match_info:
                            match_info[study_feat.id()] = []
                        
                        match_info[study_feat.id()].append({
                            "ref_id": cid,
                            "distance": dist,
                            "overlap": overlap,
                            "area_diff": area_diff
                        })
                        
                        matched_ref_ids.add(cid)
                        matched_study_ids.add(study_feat.id())
                        
                        if cid not in ref_matches_count:
                            ref_matches_count[cid] = 0
                        ref_matches_count[cid] += 1
                        
                    else:
                        # Mode unique : garder le meilleur match
                        score = (dist / MAX_DIST) * 0.7 + (1 - overlap) * 0.3
                        
                        if cid not in ref_best_matches:
                            ref_best_matches[cid] = {
                                "study_id": study_feat.id(),
                                "distance": dist,
                                "overlap": overlap,
                                "score": score,
                                "area_diff": area_diff
                            }
                        else:
                            if score < ref_best_matches[cid]["score"]:
                                ref_best_matches[cid] = {
                                    "study_id": study_feat.id(),
                                    "distance": dist,
                                    "overlap": overlap,
                                    "score": score,
                                    "area_diff": area_diff
                                }

        # ===== PHASE 2 : CONSTRUIRE LES APPARIEMENTS FINAUX =====
        if not ALLOW_MULTIPLE:
            # Mode 1:1 : reconstruire match_info
            match_info = {}
            for ref_id, match_data in ref_best_matches.items():
                study_id = match_data["study_id"]
                
                matched_ref_ids.add(ref_id)
                matched_study_ids.add(study_id)
                
                match_info[study_id] = [{
                    "ref_id": ref_id,
                    "distance": match_data["distance"],
                    "overlap": match_data["overlap"],
                    "area_diff": match_data["area_diff"]
                }]
        
        # Collecter les statistiques
        for study_id, matches_list in match_info.items():
            for match in matches_list:
                distances.append(match["distance"])
                area_differences.append(match["area_diff"])
                
                ref_id = match["ref_id"]
                ref_geom = ref_features[ref_id]["geom"]
                study_geom = study_features[study_id]["geom"]
                
                surface_ref_appariee += ref_geom.area()
                surface_intersection_totale += study_geom.intersection(ref_geom).area()

        # ===== CRÉATION DES FEATURES REF NON DÉTECTÉS =====
        for ref_id, ref_data in ref_features.items():
            if ref_id not in matched_ref_ids:
                feat = QgsFeature(ref_non_detectes_layer.fields())
                feat.setGeometry(ref_data["geom"])
                
                attrs = ref_data["attrs"] + [ref_data["id_building"]]
                feat.setAttributes(attrs)
                ref_non_detectes_layer.dataProvider().addFeature(feat)

        # ===== CRÉATION DES FEATURES APPARIÉES ÉTUDE =====
        for study_id in matched_study_ids:
            matches_list = match_info[study_id]
            
            for match in matches_list:
                feat = QgsFeature(study_matched_layer.fields())
                feat.setGeometry(study_features[study_id]["geom"])
                
                ref_id = match["ref_id"]
                
                attrs = study_features[study_id]["attrs"] + [
                    ref_features[ref_id]["id_building"],
                    match["distance"],
                    match["overlap"] * 100
                ]
                feat.setAttributes(attrs)
                study_matched_layer.dataProvider().addFeature(feat)

        # ===== CRÉATION DES LIGNES DE LIAISON AVEC FLÈCHES =====
        for study_id, matches_list in match_info.items():
            for match in matches_list:
                ref_id = match["ref_id"]
                
                ref_centroid = ref_features[ref_id]["centroid"].asPoint()
                study_centroid = study_features[study_id]["centroid"].asPoint()
                
                line_geom = QgsGeometry.fromPolylineXY([ref_centroid, study_centroid])
                
                link_feat = QgsFeature(link_layer.fields())
                link_feat.setGeometry(line_geom)
                link_feat.setAttributes([
                    ref_features[ref_id]["id_building"],
                    match["distance"]
                ])
                link_layer.dataProvider().addFeature(link_feat)

        # ===== ÉTUDE NON APPARIÉE =====
        for study_feat_id, study_data in study_features.items():
            if study_feat_id not in matched_study_ids:
                feat = QgsFeature(study_remaining_layer.fields())
                feat.setGeometry(study_data["geom"])
                feat.setAttributes(study_data["attrs"])
                study_remaining_layer.dataProvider().addFeature(feat)

        # ===== INDICATEURS CLASSIQUES =====
        nb_study = layer_study.featureCount()
        nb_ref = layer_ref.featureCount()
        nb_matched_ref = len(matched_ref_ids)
        nb_matched_study = len(matched_study_ids)

        mean_dist = sum(distances) / len(distances) if distances else 0
        exhaustivite = nb_matched_ref / nb_ref if nb_ref else 0
        sur_compl = (nb_study - nb_matched_study) / nb_study if nb_study else 0
        overlap_idx = (
            surface_intersection_totale / surface_ref_appariee
            if surface_ref_appariee else 0
        )
        
        # ===== STATISTIQUES ROBUSTES =====
        median_dist = statistics.median(distances) if distances else 0
        mad_dist = calculate_mad(distances)
        
        median_area_diff = statistics.median(area_differences) if area_differences else 0
        mad_area_diff = calculate_mad(area_differences)
        
        significant_area = identify_significant_differences(area_differences)
        percent_significant = (sum(significant_area) / len(significant_area) * 100) if significant_area else 0
        
        # Nombre moyen de matchs
        if ALLOW_MULTIPLE:
            total_matches = sum(len(matches) for matches in match_info.values())
            mean_matches_per_study = total_matches / len(match_info) if match_info else 0
            
            if ref_matches_count:
                mean_matches_per_ref = sum(ref_matches_count.values()) / len(ref_matches_count)
            else:
                mean_matches_per_ref = 0
        else:
            mean_matches_per_study = 1.0
            mean_matches_per_ref = 1.0

        # ===== ÉCRITURE DANS LE FICHIER TEXTE =====
        f.write(f"COUCHE : {os.path.basename(study_path)}\n")
        f.write("-" * 50 + "\n\n")
        
        f.write("STATISTIQUES AGRÉGÉES\n")
        f.write(f"Nombre de bâtiments (étude) : {nb_study}\n")
        f.write(f"Nombre de bâtiments (référence) : {nb_ref}\n")
        f.write(f"Bâtiments appariés (réf) : {nb_matched_ref}\n")
        f.write(f"Bâtiments appariés (étude) : {nb_matched_study}\n")
        f.write(f"Bâtiments non détectés (réf) : {nb_ref - nb_matched_ref}\n")
        f.write(f"Bâtiments en trop (étude) : {nb_study - nb_matched_study}\n")
        f.write(f"Pourcentage REF avec match : {(nb_matched_ref/nb_ref*100):.1f}%\n")
        f.write(f"Pourcentage ÉTUDE avec match : {(nb_matched_study/nb_study*100):.1f}%\n\n")
        
        f.write("INDICATEURS DE QUALITÉ\n")
        f.write(f"Exhaustivité : {exhaustivite*100:.1f} %\n")
        f.write(f"Sur-complétude : {sur_compl*100:.1f} %\n")
        f.write(f"Indice recouvrement : {overlap_idx*100:.1f} %\n\n")
        
        f.write("ANALYSE POSITIONNELLE\n")
        f.write(f"Distance moyenne : {mean_dist:.2f} m\n")
        f.write(f"Distance médiane : {median_dist:.2f} m\n")
        f.write(f"MAD distance : {mad_dist:.2f} m\n\n")
        
        f.write("ANALYSE MORPHOLOGIQUE\n")
        f.write(f"Différence aire médiane : {median_area_diff:.2f} m²\n")
        f.write(f"MAD aire : {mad_area_diff:.2f} m²\n")
        f.write(f"% différences significatives : {percent_significant:.1f} %\n\n")
        
        if ALLOW_MULTIPLE:
            f.write("ANALYSE SÉMANTIQUE\n")
            f.write(f"Moyenne matchs / bât. ÉTUDE : {mean_matches_per_study:.2f}\n")
            f.write(f"Moyenne matchs / bât. REF : {mean_matches_per_ref:.2f}\n\n")
        
        f.write("=" * 50 + "\n\n")
        
        # Stocker les résultats pour la synthèse comparative
        all_results.append({
            "nom": os.path.basename(study_path),
            "exhaustivite": exhaustivite,
            "sur_compl": sur_compl,
            "overlap_idx": overlap_idx,
            "mean_dist": mean_dist,
            "median_dist": median_dist,
            "mad_dist": mad_dist,
            "median_area_diff": median_area_diff,
            "mad_area_diff": mad_area_diff,
            "percent_significant": percent_significant,
            "nb_matched_ref": nb_matched_ref,
            "nb_matched_study": nb_matched_study,
            "mean_matches_per_study": mean_matches_per_study if ALLOW_MULTIPLE else 1.0
        })

        # ===== AJOUT DES COUCHES AU PROJET =====
        ref_non_detectes_layer.updateExtents()
        study_matched_layer.updateExtents()
        study_remaining_layer.updateExtents()
        link_layer.updateExtents()

        project.addMapLayer(ref_non_detectes_layer)
        project.addMapLayer(study_matched_layer)
        project.addMapLayer(study_remaining_layer)
        project.addMapLayer(link_layer)

        apply_outline_style(ref_non_detectes_layer, "purple")
        apply_outline_style(study_matched_layer, "lime")
        apply_outline_style(study_remaining_layer, "red")
        apply_arrow_style(link_layer)

    # ==================================================
    # 9. SYNTHÈSE COMPARATIVE (si plusieurs couches)
    # ==================================================
    if len(all_results) > 1:
        f.write("\n")
        f.write("=" * 50 + "\n")
        f.write("SYNTHÈSE COMPARATIVE\n")
        f.write("=" * 50 + "\n\n")
        
        # Trouver les meilleures couches pour chaque critère
        best_exhaustivite = max(all_results, key=lambda x: x["exhaustivite"])
        best_sur_compl = min(all_results, key=lambda x: x["sur_compl"])
        best_overlap = max(all_results, key=lambda x: x["overlap_idx"])
        best_position = min(all_results, key=lambda x: x["median_dist"])
        best_morpho = min(all_results, key=lambda x: x["mad_area_diff"])
        
        f.write("MEILLEURE COUCHE PAR CRITÈRE\n")
        f.write("-" * 50 + "\n")
        f.write(f"Exhaustivité : {best_exhaustivite['nom']}")
        f.write(f" ({best_exhaustivite['exhaustivite']*100:.1f}%)\n")
        
        f.write(f"Sur-complétude : {best_sur_compl['nom']}")
        f.write(f" ({best_sur_compl['sur_compl']*100:.1f}%)\n")
        
        f.write(f"Recouvrement : {best_overlap['nom']}")
        f.write(f" ({best_overlap['overlap_idx']*100:.1f}%)\n")
        
        f.write(f"Précision positionnelle : {best_position['nom']}")
        f.write(f" (médiane: {best_position['median_dist']:.2f}m)\n")
        
        f.write(f"Homogénéité morphologique : {best_morpho['nom']}")
        f.write(f" (MAD: {best_morpho['mad_area_diff']:.2f}m²)\n\n")
        
        # Tableau de comparaison
        f.write("TABLEAU COMPARATIF\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Couche':<30} {'Exhaust.':<10} {'Sur-compl.':<12} {'Recouv.':<10} {'Dist.méd.':<10}\n")
        f.write("-" * 50 + "\n")
        
        for result in all_results:
            nom_court = result['nom'][:28] if len(result['nom']) > 28 else result['nom']
            f.write(f"{nom_court:<30} ")
            f.write(f"{result['exhaustivite']*100:>6.1f}%   ")
            f.write(f"{result['sur_compl']*100:>8.1f}%    ")
            f.write(f"{result['overlap_idx']*100:>6.1f}%   ")
            f.write(f"{result['median_dist']:>7.2f}m\n")
        
        f.write("\n")
        
        # Score global (méthode composite)
        f.write("CLASSEMENT GLOBAL\n")
        f.write("-" * 50 + "\n")
        f.write("Méthode : moyenne pondérée normalisée\n")
        f.write("  • Exhaustivité (30%)\n")
        f.write("  • Sur-complétude inversée (25%)\n")
        f.write("  • Recouvrement (25%)\n")
        f.write("  • Précision positionnelle inversée (20%)\n\n")
        
        # Normaliser et calculer les scores
        max_exhaust = max(r["exhaustivite"] for r in all_results)
        max_sur_compl = max(r["sur_compl"] for r in all_results)
        max_overlap = max(r["overlap_idx"] for r in all_results)
        max_dist = max(r["median_dist"] for r in all_results) if max(r["median_dist"] for r in all_results) > 0 else 1
        
        for result in all_results:
            score_exhaust = (result["exhaustivite"] / max_exhaust) if max_exhaust > 0 else 0
            score_sur_compl = 1 - (result["sur_compl"] / max_sur_compl) if max_sur_compl > 0 else 1
            score_overlap = (result["overlap_idx"] / max_overlap) if max_overlap > 0 else 0
            score_dist = 1 - (result["median_dist"] / max_dist)
            
            score_global = (score_exhaust * 0.30 + 
                           score_sur_compl * 0.25 + 
                           score_overlap * 0.25 + 
                           score_dist * 0.20)
            
            result["score_global"] = score_global * 100
        
        # Trier par score global
        all_results_sorted = sorted(all_results, key=lambda x: x["score_global"], reverse=True)
        
        for rank, result in enumerate(all_results_sorted, 1):
            f.write(f"{rank}. {result['nom']}")
            f.write(f" (score: {result['score_global']:.1f}/100)\n")
        
        f.write("\n")
        
        # Recommandation
        best_overall = all_results_sorted[0]
        f.write("RECOMMANDATION\n")
        f.write("-" * 50 + "\n")
        f.write(f"Couche recommandée : {best_overall['nom']}\n\n")
        f.write("Points forts :\n")
        
        if best_overall["exhaustivite"] >= 0.80:
            f.write(f"  • Excellente exhaustivité ({best_overall['exhaustivite']*100:.1f}%)\n")
        if best_overall["sur_compl"] <= 0.15:
            f.write(f"  • Faible sur-complétude ({best_overall['sur_compl']*100:.1f}%)\n")
        if best_overall["overlap_idx"] >= 0.85:
            f.write(f"  • Excellent recouvrement ({best_overall['overlap_idx']*100:.1f}%)\n")
        if best_overall["median_dist"] <= 5:
            f.write(f"  • Bonne précision positionnelle ({best_overall['median_dist']:.2f}m)\n")
        
        # Points d'attention
        f.write("\nPoints d'attention :\n")
        if best_overall["exhaustivite"] < 0.70:
            f.write(f"  • Exhaustivité à améliorer ({best_overall['exhaustivite']*100:.1f}%)\n")
        if best_overall["sur_compl"] > 0.20:
            f.write(f"  • Sur-complétude élevée ({best_overall['sur_compl']*100:.1f}%)\n")
        if best_overall["median_dist"] > 10:
            f.write(f"  • Décalage positionnel significatif ({best_overall['median_dist']:.2f}m)\n")
        
        f.write("\n" + "=" * 50 + "\n")

QMessageBox.information(
    None,
    "Analyse terminée",
    f"Analyse terminée avec succès.\n\nRésultats :\n{summary_path}"
)

