# Rapid-Cyclone-Damage-Mapping
This GitHub repo hosts a rapid damage detection tool developed from academic work using Sentinel-1 radar. It provides first-pass maps of potential damage post-cyclone, primarily to support detailed photo-interpretation, guide field and drone missions, and must be validated with high-resolution imagery.
# Rapid Damage Detection Tool
**Language / Langue :** [🇬🇧 English](README.md) | 🇫🇷 Français

---
**Auteur :** Fabrice Renoux  
**Institution :** AgroParisTech - Mastère Spécialisé SILAT (Systèmes d'Informations Localisées pour l'Aménagement des Territoires)  
**Date :** Mars 2026  

---

## Avertissement

Ce projet constitue un **travail universitaire à caractère expérimental**. Il ne doit en aucun cas être considéré comme un outil opérationnel certifié pour des interventions d'urgence.

**Limitations importantes :**
- Les résultats sont fournis à titre indicatif et nécessitent une validation systématique par des experts
- L'outil ne remplace pas la photo-interprétation sur imagerie haute résolution
- Ne doit pas servir de base unique pour des décisions opérationnelles critiques
- Destiné à la recherche et à l'expérimentation académique
- L'auteur décline toute responsabilité quant à l'utilisation des résultats

**Usage recommandé :** Outil d'aide à la décision pour orienter et prioriser les analyses détaillées réalisées par des professionnels qualifiés.

---

## Contexte et Objectifs

### Problématique

Dans les premières heures suivant une catastrophe naturelle (cyclone tropical, séisme), l'évaluation rapide des dégâts se heurte à plusieurs contraintes :

1. **Délai d'acquisition** : Les images satellites optiques haute résolution peuvent nécessiter plusieurs jours avant d'être disponibles
2. **Conditions météorologiques** : La couverture nuageuse post-événement limite l'exploitation de l'imagerie optique
3. **Volume de données** : Le traitement manuel par photo-interprétation est chronophage et nécessite des expertises spécialisées
4. **Prioritisation** : Difficulté à identifier rapidement les zones nécessitant une intervention urgente

### Solution proposée

Cet outil exploite les données radar **Sentinel-1** (bande C, acquisition tout-temps) pour :

1. Générer une première cartographie indicative des zones potentiellement affectées
2. Prioriser les secteurs nécessitant une photo-interprétation détaillée
3. Cibler les reconnaissances terrain et les missions drone
4. Accélérer le processus d'évaluation rapide des équipes d'urgence

**Applications principales :**
- **Post-cyclone tropical** : dégâts structurels, inondations, glissements de terrain
- **Post-séisme** : détection de changements structurels sur le bâti (module damage detection)

**Principe :** L'outil ne produit pas une évaluation définitive, mais une **trame des dommages potentiels** devant être systématiquement validée par analyse visuelle d'imagerie haute résolution et vérifications terrain.

---

## Accès à l'application

**URL de l'application Google Earth Engine :**  
[https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app)

**Prérequis :**
- Navigateur web moderne (Chrome, Firefox, Edge)
- Compte Google (gratuit)
- Connexion internet stable

**Pas d'installation nécessaire** - L'application fonctionne entièrement en ligne via Google Earth Engine Apps.

---

## Table des matières

1. [Guide utilisateur](#guide-utilisateur)
   - [Étape 0 : Évaluation qualité des données bâti (optionnel)](#étape-0)
   - [Étape 1 : Utilisation de l'application GEE](#étape-1)
   - [Étape 2 : Estimation de population affectée (post-traitement)](#étape-2)
2. [Méthodologie scientifique](#méthodologie-scientifique)
3. [Sources de données](#sources-données)
4. [Bibliographie](#bibliographie)
5. [Licence et contributions](#licence)

---

<a name="guide-utilisateur"></a>
# 1. Guide utilisateur

<a name="étape-0"></a>
## Étape 0 : Évaluation de la qualité des données bâti (optionnel)

### Contexte

Google Earth Engine propose plusieurs bases de données bâti mondiales dont la qualité varie selon les régions :
- Google Open Buildings v3
- Microsoft Building Footprints (via VIDA Combined)
- Assets personnalisés

Un script Python QGIS permet de comparer ces sources avec une couche de référence locale pour identifier la plus adaptée.

### Prérequis

**Logiciels :**
- QGIS 3.x (version stable recommandée)

**Données nécessaires :**
- **Couche de référence** : Données bâti de haute qualité (cadastre, levé terrain, OpenStreetMap validé)
  - Format : Shapefile (.shp) ou GeoPackage (.gpkg)
  - Géométrie : Polygones
- **Couches à évaluer** (1 à 5 maximum) : Extraits des bases de données à comparer
  - Formats : Shapefile (.shp) ou GeoPackage (.gpkg)
  - Géométrie : Polygones

### Installation

1. Télécharger le script `building_quality_comparison.py` depuis le dépôt :
```
tools/building_quality_comparison.py
```

2. Ouvrir QGIS
3. Menu : **Extensions** > **Console Python**
4. Cliquer sur l'icône **Ouvrir un script**
5. Sélectionner `building_quality_comparison.py`

### Exécution

1. Cliquer sur **Exécuter le script** (icône play)
2. Suivre les dialogues interactifs :

**Dialogue 1 : Couche de référence**
- Sélectionner le fichier vectoriel de référence

**Dialogue 2 : Couches à évaluer**
- Sélectionner 1 à 5 fichiers vectoriels (Ctrl+clic pour multi-sélection)

**Dialogue 3 : Dossier de sortie**
- Définir le répertoire de sauvegarde des résultats

**Dialogue 4 : Paramètres d'appariement**

| Paramètre | Description | Valeur recommandée |
|-----------|-------------|-------------------|
| Distance max (m) | Distance maximale entre centroïdes pour considérer un appariement | 10 m (urbain dense) à 50 m (rural) |
| Recouvrement minimal (%) | Seuil de chevauchement surfacique | 50% |
| Appariements multiples | 0 = mode 1:1 strict, 1 = mode 1:n | 0 |

### Interprétation des résultats

Le script génère :

1. **Fichier texte de synthèse** : `comparison_summary_YYYYMMDD_HHMM.txt`
2. **Couches QGIS** ajoutées au projet :

| Couche | Symbologie | Description |
|--------|-----------|-------------|
| REF_buildings | Contour orange | Bâtiments de référence |
| REF_NON_DETECTES_[nom] | Contour violet | Bâtiments de référence non détectés |
| BATI_ETUDE_APPARIES_[nom] | Contour vert | Bâtiments correctement appariés |
| BATI_ETUDE_NON_APPARIES_[nom] | Contour rouge | Bâtiments en excès (sur-complétude) |
| LIAISONS_[nom] | Lignes bleues pointillées avec flèches | Liaisons centroïdes |

#### Indicateurs clés

Le fichier texte contient pour chaque couche évaluée :

**Statistiques agrégées**
- Nombre de bâtiments (étude vs référence)
- Nombre de bâtiments appariés
- Nombre de bâtiments non détectés
- Nombre de bâtiments en excès

**Indicateurs de qualité**

| Indicateur | Formule | Interprétation | Valeur excellente | Valeur acceptable | Valeur faible |
|------------|---------|----------------|-------------------|-------------------|---------------|
| Exhaustivité | (Bâtiments REF détectés) / (Total bâtiments REF) | Capacité à détecter tous les bâtiments existants | > 90% | 70-90% | < 70% |
| Sur-complétude | (Bâtiments ÉTUDE non appariés) / (Total bâtiments ÉTUDE) | Proportion de détections erronées | < 5% | 5-15% | > 15% |
| Indice de recouvrement | (Surface intersection totale) / (Surface REF appariée) | Qualité surfacique du chevauchement | > 90% | 80-90% | < 80% |

**Analyse positionnelle**
- Distance moyenne et médiane entre centroïdes
- MAD (Median Absolute Deviation) : indicateur robuste de dispersion

**Analyse morphologique**
- Différence d'aire médiane (m²)
- MAD de la différence d'aire
- Pourcentage de différences significatives (test MAD avec seuil à 1.96 σ)

#### Synthèse comparative

Si plusieurs couches sont évaluées, le fichier contient :

**Tableau récapitulatif**
```
Couche                         Exhaust.   Sur-compl.   Recouv.   Dist.méd.
---------------------------------------------------------------------------
google_buildings.shp             88.3%       7.2%      91.5%      2.87m
microsoft_buildings.shp          82.1%       4.1%      89.3%      2.12m
osm_buildings.shp                76.5%      12.8%      85.7%      4.56m
```

**Classement global**

Score composite calculé par moyenne pondérée :
- Exhaustivité : 30%
- Sur-complétude inversée : 25%
- Recouvrement : 25%
- Précision positionnelle inversée : 20%

**Recommandation**

Le script identifie la couche optimale et liste :
- Points forts
- Points d'attention (critères en-dessous des seuils)

### Décision pour l'application GEE

Utiliser la couche ayant obtenu le meilleur score global :
- Si Google Open Buildings est optimal : sélectionner cette option dans l'application
- Si Microsoft Buildings est optimal : sélectionner "Google-Microsoft (VIDA Combined)"
- Si aucune couche publique n'est satisfaisante (score < 70) : envisager l'utilisation d'un asset personnalisé

---

<a name="étape-1"></a>
## Étape 1 : Utilisation de l'application Google Earth Engine

### Interface utilisateur

L'application se compose de trois panneaux principaux :

1. **Panneau de contrôle** (gauche) : Configuration des paramètres d'analyse
2. **Panneau cartographique** (centre) : Visualisation spatiale et dessin de l'AOI
3. **Panneau de résultats** (droite) : Affichage des statistiques et liens de téléchargement

### Configuration des paramètres

#### Quick Start

Menu déroulant proposant des configurations pré-enregistrées :
- **New (blank)** : Configuration vierge
- **Demo: Jamaica Whitehouse (Oct 2025)** : Exemple fonctionnel sur le cyclone Melissa

Pour tester l'application, sélectionner la démo et cliquer directement sur "Run Analysis".

#### 1. Zone Name

Identifiant de la zone d'étude utilisé pour nommer les fichiers d'export.

**Format recommandé :** `Pays_Événement_Année`

**Exemples :**
- `Haiti_Matthew_2016`
- `Mozambique_Idai_2019`
- `Philippines_Haiyan_2013`

#### 2. Dates (format YYYY-MM-DD)

**Pre-date (date de référence)**
- Date antérieure à l'événement, représentant l'état normal
- Choisir une période sans événement majeur
- Recommandation : 1 à 3 mois avant l'événement

**Event date (date de l'événement)**
- Date de la catastrophe
- Peut être la date d'impact ou le lendemain

**Contrainte :** Pre-date < Event date

#### 3. Intervals (intervalles en jours)

**Pre (intervalle avant)**
- Fenêtre temporelle pour rechercher des images Sentinel-1 avant la date de référence
- Plage : 30 à 365 jours
- **Recommandation : 180 jours**
- Plus l'intervalle est étendu, plus la probabilité de trouver des images est élevée

**Post (intervalle après)**
- Fenêtre temporelle pour rechercher des images Sentinel-1 après la date d'événement
- Plage : 1 à 28 jours
- **Recommandation : 6 jours** (correspond à la période de revisite de Sentinel-1)
- Si aucune image n'est trouvée, l'application suggère d'augmenter cet intervalle

**Note technique :** Sentinel-1 a une période de revisite de ~6 jours en moyenne. Un intervalle post-événement trop court (< 6 jours) peut ne pas capturer d'acquisition.

#### 4. Options (modules d'analyse)

**Weather data (données météorologiques)**
- Précipitations cumulées (CHIRPS Daily)
- Vent moyen et maximal (GLDAS)
- Pression atmosphérique moyenne et minimale (GLDAS)
- Graphiques d'évolution temporelle
- **Recommandation :** Toujours activer pour contextualiser l'événement

**Damage detection (détection des dégâts)**
- Détection de changements sur le bâti et les routes
- Basé sur le test t pixelwise (PWTT) appliqué aux données Sentinel-1
- **Applications :** Cyclones, séismes, conflits
- Génère des classes de dégâts (Modéré, Élevé, Très élevé)

**Flood detection (détection des inondations)**
- Cartographie de l'étendue des zones inondées
- Basé sur l'algorithme s1flood (DeVries et al., 2020)
- **Applications :** Cyclones, crues, événements pluviométriques extrêmes
- Identifie les bâtiments et routes inondés

**Landslide detection (détection des glissements de terrain)**
- Cartographie de la susceptibilité aux glissements de terrain
- Combinaison du test t et de facteurs environnementaux (pente, courbure, précipitations, type de sol)
- **Applications :** Séismes, fortes précipitations en zones montagneuses
- Génère des zones d'exposition (runout zones)

**Time series (série temporelle - flood uniquement)**
- Analyse de l'évolution temporelle des inondations
- Nécessite l'activation de "Flood detection"
- Génère un graphique montrant la progression/décrue
- Permet de spécifier une période d'analyse personnalisée

**Recommandation :** Pour un premier test, activer Weather + un seul module (Damage OU Flood) pour réduire le temps de calcul.

#### 5. AOI (Area of Interest)

Trois méthodes de définition de la zone d'étude :

**Méthode 1 : Draw on map**
- Utiliser les outils de dessin intégrés (rectangle ou polygone)
- Tracer directement sur la carte
- **Limitation :** Surface maximale recommandée ~50 km² (pour des temps de calcul < 15 min)

**Méthode 2 : Enter WKT/GeoJSON**
- Coller du texte WKT ou GeoJSON
- Utile si la zone a été définie dans un SIG externe (QGIS)
- **Procédure QGIS :**
  1. Installer le plugin "Get WKT"
  2. Sélectionner le polygone
  3. Clic droit > Get WKT
  4. Copier-coller dans le champ de l'application

**Méthode 3 : Custom asset**
- Utiliser un asset Google Earth Engine pré-uploadé
- Format : `projects/YOUR_PROJECT/assets/YOUR_AOI`
- L'asset doit être un FeatureCollection

**Recommandation :** Zones de 10-50 km² pour un équilibre entre résolution spatiale et temps de calcul.

#### 6. Buildings (source de données bâti)

Trois options disponibles :

| Option | Description | Couverture | Résolution typique |
|--------|-------------|------------|-------------------|
| Google Open Buildings v3 | Base de données Google | Mondiale (hors Europe/USA) | Niveau bâtiment |
| Google-Microsoft (VIDA Combined) | Fusion des deux bases | Mondiale | Niveau bâtiment |
| Custom asset | Asset personnel uploadé sur GEE | Zone spécifique | Variable |

**Sélection recommandée :**
- Si l'étape 0 a été réalisée : utiliser la couche ayant obtenu le meilleur score
- Sinon : privilégier "Google-Microsoft (VIDA Combined)" pour la plupart des régions

**Format pour Custom asset :**
- Type : FeatureCollection
- Géométrie : Polygones
- Path : `projects/YOUR_PROJECT/assets/YOUR_BUILDINGS`

#### 7. Roads (source de données routes)

Deux options :

| Option | Description | Couverture |
|--------|-------------|-----------|
| GRIP4 (auto) | Global Roads Inventory Project | Mondiale (détection automatique de la région) |
| Custom asset | Réseau routier personnalisé | Zone spécifique |

**GRIP4** sélectionne automatiquement la région appropriée (Amérique du Nord, Europe, Afrique, etc.) en fonction de la localisation de l'AOI.

**Format pour Custom asset :**
- Type : FeatureCollection
- Géométrie : LineString
- Path : `projects/YOUR_PROJECT/assets/YOUR_ROADS`

#### 8. DEM Source (modèle numérique de terrain)

Activé uniquement si "Flood detection" ou "Landslide detection" est coché.

| Option | Résolution | Couverture | Usage recommandé |
|--------|-----------|-----------|------------------|
| NASADEM | 30m | Mondiale (60°N-56°S) | Défaut (recommandé) |
| SRTM | 30m | Mondiale (60°N-56°S) | Alternative |
| ALOS | 30m | Mondiale | Zones tropicales |
| ASTER | 30m | Mondiale | Moins précis |
| Custom | Variable | Spécifique | DEM local de meilleure qualité |

**Recommandation :** Conserver NASADEM sauf si un DEM local de résolution supérieure est disponible.

#### 9. Settings (paramètres avancés)

**T-threshold (seuil de détection des dégâts)**
- Plage : 2.0 à 5.0
- Défaut : 2.4
- Principe : Seuil de la statistique t en dessous duquel un changement est considéré comme non significatif
- Augmenter = moins de faux positifs, risque de manquer des dégâts légers
- Diminuer = détection plus sensible, risque de faux positifs accru

**Slope (pente minimale pour landslide)**
- Plage : 5° à 30°
- Défaut : 10°
- Seuil de pente en-dessous duquel le risque de glissement de terrain est considéré comme négligeable

**Curvature (courbure minimale)**
- Plage : 0.01 à 0.2
- Défaut : 0.05
- Courbure du terrain (concavité/convexité) utilisée pour identifier les zones d'instabilité potentielle

**Recommandation :** Conserver les valeurs par défaut pour une première analyse. Ajuster selon les résultats et la connaissance du terrain.

#### 10. Time Series (série temporelle)

Visible uniquement si "Flood detection" est activé.

**From / To** : Définir la période d'analyse
- L'application recherche toutes les images Sentinel-1 disponibles dans cet intervalle
- Génère un graphique montrant l'évolution de la surface inondée
- Permet d'identifier le pic de crue et la dynamique de décrue

**Note :** Le temps de calcul augmente proportionnellement au nombre de dates analysées.

### Lancement de l'analyse

1. Vérifier que tous les paramètres obligatoires sont configurés
2. Cliquer sur **Run Analysis**
3. Observer la barre de progression

**Durée estimée :**
- Petite zone (< 10 km²) : 1-3 minutes
- Zone moyenne (10-30 km²) : 3-8 minutes
- Grande zone (30-50 km²) : 8-15 minutes

**Important :** Ne pas fermer la fenêtre du navigateur pendant le calcul.

### Interprétation des résultats

#### Panneau de résultats (droite)

**Informations générales**
- Surface de l'AOI (km²)
- Population (WorldPop)
- Infrastructure (ports, aéroports, établissements de santé)

**Weather conditions**
- Graphiques de précipitations cumulées
- Graphiques de vent et pression atmosphérique
- Statistiques récapitulatives :
  - Cumulative rainfall (mm)
  - Max daily rainfall (mm)
  - Max wind gust (km/h)
  - Min pressure (hPa)

**Damage statistics (si activé)**

*Buildings*
- Nombre de bâtiments endommagés vs intacts
- Pourcentage de bâtiments endommagés
- Répartition par niveau de sévérité :
  - Very High (T ≥ T_threshold + 2)
  - High (T_threshold + 1 ≤ T < T_threshold + 2)
  - Moderate (T_threshold ≤ T < T_threshold + 1)

*Roads*
- Nombre de segments routiers endommagés vs intacts
- Longueur estimée de routes endommagées (km)

**Flood statistics (si activé)**
- Surface inondée (km²)
- Répartition par type de couverture du sol (WorldCover)
- Nombre de bâtiments en zone inondée
- Longueur de routes inondées (km)

**Landslide statistics (si activé)**
- Surface totale en zone de susceptibilité (km²)
- Répartition par niveau de probabilité (Modéré, Élevé, Très élevé)
- Surface des zones d'exposition (runout zones)
- Nombre de bâtiments en zone à risque
- Longueur de routes en zone à risque (km)

#### Couches cartographiques

Les couches suivantes sont ajoutées au panneau "Layers" :

**AOI**
- Contour orange de la zone d'étude

**Damage (si activé)**
- T-statistic raster : Raster de changement (valeurs continues)
- Buildings intact : Contour vert
- Buildings Very High : Contour rouge foncé
- Buildings High : Contour orange
- Buildings Moderate : Contour jaune
- Roads intact : Ligne verte
- Roads damaged : Ligne rouge
- Density bubbles : Cercles proportionnels à la densité de dégâts
- Logistic hub : Point d'accès logistique suggéré (calculé par barycentre pondéré des dégâts et distance aux infrastructures)

**Flood (si activé)**
- Extent : Étendue des inondations (dégradé de bleus selon la classification)
- Permanent water : Eau permanente (bleu clair)
- Flooded buildings : Bâtiments en zone inondée (contour bleu foncé)
- Flooded roads : Routes en zone inondée (ligne bleue épaisse)
- (Si time series) : Couches datées pour chaque acquisition Sentinel-1

**Landslide (si activé)**
- Susceptibility : Dégradé marron (1 = Modéré, 2 = Élevé, 3 = Très élevé)
- Exposure zones : Zones d'écoulement potentiel (marron clair)
- Buildings at risk : Bâtiments en zone à risque (contour marron)
- Roads at risk : Routes en zone à risque (ligne marron)

**Infrastructure**
- Large/Medium/Small airports : Triangles bleus (taille proportionnelle)
- Heliports : Cercles bleus
- Ports : Carrés bleus
- Health facilities : Croix rouges

### Export des résultats

Deux méthodes d'export sont proposées :

#### Méthode 1 : Téléchargement instantané (client-side)

**Avantages :**
- Aucun compte Google Earth Engine nécessaire
- Téléchargement immédiat dans le navigateur
- Format GeoJSON (compatible QGIS, ArcGIS, etc.)

**Limitations :**
- Maximum 5000 features par couche
- Données vectorielles uniquement (pas de rasters)

**Fichiers disponibles :**
- `Analysis_Summary.csv` : Récapitulatif textuel des statistiques
- `Buildings_Damage.geojson` : Bâtiments endommagés avec attributs (T_statistic, damage, confidence)
- `Roads_Damage.geojson` : Segments routiers endommagés avec attributs
- `Flooded_Buildings.geojson` : Bâtiments en zone inondée
- `Landslide_Buildings.geojson` : Bâtiments en zone à risque glissement

**Procédure :**
1. Dans le panneau de résultats, section "INSTANT DOWNLOAD"
2. Cliquer sur le lien bleu du fichier souhaité
3. Le fichier se télécharge automatiquement

#### Méthode 2 : Export Google Drive (complet)

**Avantages :**
- Dataset complet sans limite de features
- Inclut les rasters (T-statistic, flood extent, landslide susceptibility)
- Format Shapefile + GeoTIFF

**Limitations :**
- Nécessite un compte Google Earth Engine (gratuit)
- Nécessite des actions manuelles dans l'interface Tasks

**Fichiers exportés :**
- `Analysis_Summary.csv`
- `Buildings_Damage.shp` (+ .dbf, .shx, .prj, .cpg)
- `Roads_Damage.shp`
- `T_Statistic_Raster.tif` (GeoTIFF, résolution 10m)
- `Flood_Extent.tif` (GeoTIFF, résolution 10m)
- `Landslide_Susceptibility.tif` (GeoTIFF, résolution 30m)
- `Landslide_Runout_Zones.tif` (GeoTIFF, résolution 30m)

**Procédure :**
1. Dans le panneau de résultats, section "GOOGLE DRIVE EXPORT"
2. Les tâches d'export sont automatiquement créées
3. Cliquer sur l'onglet "Tasks" (icône orange en haut à droite)
4. Pour chaque tâche :
   - Cliquer sur "RUN"
   - Confirmer le dossier de destination (par défaut : `RapidDamage_[Zone]_[Date]`)
   - Patienter (barre bleue → verte une fois terminé)
5. Accéder aux fichiers dans Google Drive

**Durée d'export (via Tasks) :**
- Dépend de la taille de la zone et du nombre de features
- Généralement : 2-10 minutes par tâche

### Résolution de problèmes

| Message d'erreur | Cause probable | Solution |
|------------------|----------------|----------|
| `No POST images - increase Post interval` | Aucune image Sentinel-1 trouvée après l'EVENT-date | Augmenter l'intervalle Post à 7-14 jours |
| `Invalid date format` | Format de date incorrect | Utiliser le format YYYY-MM-DD (ex: 2025-10-28) |
| `Pre-date must be before event` | Dates inversées | Vérifier que Pre-date < Event-date |
| `Draw an AOI first` | Aucune zone d'étude définie | Dessiner un polygone sur la carte ou coller du WKT |
| `Invalid building asset path` | Chemin d'asset erroné | Vérifier le format `projects/[PROJECT]/assets/[ASSET]` |
| Calcul > 15 minutes | Zone trop étendue | Réduire la taille de l'AOI (< 50 km²) |

---

<a name="étape-2"></a>
## Étape 2 : Estimation de population affectée (post-traitement QGIS)

### Contexte

Google Earth Engine n'est pas optimisé pour l'estimation de population à l'échelle du bâtiment. Un traitement post-analyse dans QGIS permet de croiser les bâtiments endommagés avec des données de densité de population pour obtenir une estimation du nombre d'habitants affectés.

### Prérequis

**Logiciels :**
- QGIS 3.x (version stable recommandée)

**Données nécessaires :**

1. **Couche bâti endommagé** (depuis l'application GEE)
   - Format : GeoJSON ou Shapefile
   - Fichier : `Buildings_Damage.geojson` ou `Buildings_Damage.shp`

2. **Données de hauteur de bâtiments** (optionnel mais recommandé)
   - **WSF 3D - Building Height V02**
   - Source : DLR (German Aerospace Center)
   - URL : [https://download.geoservice.dlr.de/WSF3D/files/](https://download.geoservice.dlr.de/WSF3D/files/)
   - Résolution : 90m
   - Format : GeoTIFF

**Téléchargement WSF3D :**
1. Accéder au serveur DLR
2. Identifier la tuile correspondant à la zone d'étude (grille mondiale)
3. Télécharger le fichier `.tif`
4. Exemple de nomenclature : `WSF3D_V02_BuildingHeight_N18W078.tif`

3. **Données de densité de population**
   - Chargées automatiquement par le modèle (WorldPop ou GHS-POP)
   - Nécessite une connexion internet

### Installation du modèle QGIS

1. Télécharger le fichier `Population_building.model3` depuis le dépôt :
```
tools/Population_building.model3
```

2. Ouvrir QGIS
3. Menu : **Traitement** > **Boîte à outils**
4. Cliquer sur l'icône d'options (roue crantée) en haut de la boîte à outils
5. Sélectionner **"Ajouter un modèle à la boîte à outils"**
6. Naviguer vers `Population_building.model3`
7. Cliquer sur **Ouvrir**

Le modèle apparaît dans :
```
Traitement
└── Modèles
    └── Population_building
```

### Préparation des données

**Étape 1 : Charger la couche bâti endommagé**
1. Menu : **Couche** > **Ajouter une couche** > **Ajouter une couche vecteur**
2. Sélectionner `Buildings_Damage.geojson` (ou `.shp`)
3. Cliquer sur **Ajouter**

**Étape 2 : Charger la couche de hauteur (si disponible)**
1. Menu : **Couche** > **Ajouter une couche** > **Ajouter une couche raster**
2. Sélectionner le fichier WSF3D `.tif`
3. Cliquer sur **Ajouter**

### Exécution du modèle

1. Dans la boîte à outils, double-cliquer sur **Population_building**
2. Configurer les paramètres :

| Paramètre | Description | Valeur |
|-----------|-------------|--------|
| Input building layer | Couche vectorielle des bâtiments | Buildings_Damage |
| Building height raster (optional) | Raster de hauteur de bâtiments | WSF3D_BuildingHeight ou laisser vide |
| Population data source | Source de densité de population | WorldPop (auto-download) |
| Output layer | Fichier de sortie | Chemin/nom du fichier (.gpkg ou .shp) |

3. Cliquer sur **Exécuter**

**Durée de traitement :**
- 1000 bâtiments : ~30 secondes
- 5000 bâtiments : ~2 minutes
- 10000 bâtiments : ~5 minutes

### Interprétation des résultats

Le modèle génère une nouvelle couche : `Buildings_with_population`

**Nouveaux champs attributaires :**

| Champ | Type | Description | Unité |
|-------|------|-------------|-------|
| pop_total | Float | Population estimée pour ce bâtiment | habitants |
| pop_density | Float | Densité de population | hab/m² |
| building_height | Float | Hauteur estimée du bâtiment | m |
| building_volume | Float | Volume estimé du bâtiment | m³ |

**Calcul de la population totale affectée :**

1. Ouvrir la table attributaire (clic droit > **Table attributaire**)
2. Cliquer sur l'icône **Σ** (Statistiques de base) en bas de la table
3. Sélectionner le champ `pop_total`
4. Cocher **Somme**
5. Lire la valeur résultante

**Exemple de résultat :**
```
Somme de pop_total : 10547
```
Interprétation : Environ 10 547 personnes sont potentiellement affectées par les dégâts détectés.

**Analyse par niveau de sévérité :**

Pour croiser avec les niveaux de dégâts (Very High, High, Moderate) :

**Méthode 1 : Sélection par expression**
1. Dans la table attributaire, cliquer sur **Sélectionner par expression** (icône ε)
2. Entrer :
```sql
"confidence" = 'Very High'
```
3. Cliquer sur **Sélectionner**
4. Observer le nombre de lignes sélectionnées
5. Utiliser **Σ** > `pop_total` > **Somme** pour obtenir la population dans les bâtiments très endommagés

**Méthode 2 : Statistiques par groupe**
1. Menu : **Vecteur** > **Analyse** > **Statistiques de base pour les champs**
2. Configuration :
   - Couche d'entrée : `Buildings_with_population`
   - Champ à analyser : `pop_total`
   - Champ pour regrouper par catégorie : `confidence`
3. Cliquer sur **Exécuter**

**Résultat type :**
```
Confidence    | Count | Sum pop_total
-----------------------------------------
Very High     |  123  |   3456
High          |  287  |   5234
Moderate      |  472  |   1857
```

**Interprétation :**
- 3 456 personnes dans des bâtiments très fortement endommagés (priorité 1)
- 5 234 personnes dans des bâtiments fortement endommagés (priorité 2)
- 1 857 personnes dans des bâtiments modérément endommagés (priorité 3)

### Export et visualisation

**Cartographie thématique :**
1. Clic droit sur la couche > **Propriétés** > **Symbologie**
2. Type de symbole : **Gradué**
3. Colonne : `pop_total`
4. Mode : **Ruptures naturelles (Jenks)**
5. Rampe de couleur : Dégradé rouge (faible à fort)
6. Cliquer sur **Classer** puis **OK**

**Export des résultats :**
1. Clic droit sur la couche > **Exporter** > **Sauvegarder les entités sous...**
2. Format : GeoPackage (.gpkg) ou Shapefile (.shp)
3. Nom de fichier : `Buildings_Damage_Population`
4. Cliquer sur **OK**

**Création d'une carte de synthèse (optionnel) :**
1. Menu : **Projet** > **Nouvelle mise en page**
2. Ajouter :
   - Vue cartographique
   - Légende
   - Échelle
   - Titre et métadonnées
3. Menu : **Mise en page** > **Exporter en PDF**

### Limitations et précautions

**Limitations méthodologiques :**

1. **Nature des estimations**
   - Les valeurs de population sont des **estimations statistiques**, non des comptages réels
   - Basées sur des données de densité à résolution régionale (~100m pour WorldPop)

2. **Résolution spatiale**
   - WorldPop : ~100m
   - WSF3D : 90m
   - Imprécision potentielle pour les petits bâtiments isolés

3. **Hypothèses du modèle**
   - Distribution uniforme de la population au sein d'un bâtiment
   - Occupation constante (pas de variation jour/nuit)
   - Pas de prise en compte des bâtiments non résidentiels

4. **Données manquantes**
   - Si WSF3D indisponible : hauteur par défaut = 6m (2 étages)
   - Si WorldPop indisponible : densité par défaut basée sur des statistiques régionales

**Recommandations d'usage :**

- Utiliser ces chiffres comme **ordre de grandeur**
- Appliquer une marge d'incertitude de ±30-50%
- Croiser avec d'autres sources (recensements locaux, enquêtes terrain)
- Valider par reconnaissance terrain pour les zones prioritaires
- Communiquer systématiquement les limitations lors de la diffusion des résultats

**Interprétation correcte :**
- "Environ 10 000 personnes sont potentiellement affectées (estimation ±40%)"
- Éviter : "Exactement 10 547 personnes sont affectées"

---

---

<a name="méthodologie-scientifique"></a>
# 2. Méthodologie Scientifique

## 2.1 Architecture générale du système

### 2.1.1 Vue d'ensemble

L'outil Rapid Damage Detection repose sur une architecture modulaire composée de quatre modules principaux :
```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT DATA LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Sentinel-1 GRD    │  DEM Sources   │  Vector Data  │ Ancillary│
│  (SAR C-band)      │  (NASADEM,     │  (Buildings,  │ (WorldPop│
│                    │   SRTM, etc.)  │   Roads)      │  CHIRPS) │
│                                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PROCESSING MODULES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   DAMAGE     │  │    FLOOD     │  │  LANDSLIDE   │          │
│  │  DETECTION   │  │  DETECTION   │  │  DETECTION   │          │
│  │   (PWTT)     │  │  (s1flood)   │  │ (Heatmaps +  │          │
│  │              │  │              │  │  Suscept.)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                            │                                    │
│                            ▼                                    │
│                  ┌──────────────────┐                          │
│                  │     WEATHER      │                          │
│                  │   STATISTICS     │                          │
│                  │ (CHIRPS, GLDAS)  │                          │
│                  └──────────────────┘                          │
│                                                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Damage maps (buildings, roads)                              │
│  • Flood extent maps                                           │
│  • Landslide susceptibility maps                               │
│  • Statistical reports                                         │
│  • Time series charts                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1.2 Flux de traitement principal

Le workflow général suit la séquence suivante :

1. **Définition de l'AOI** par l'utilisateur
2. **Sélection temporelle** (Pre-date, Event-date, Intervals)
3. **Acquisition des données** Sentinel-1 et auxiliaires
4. **Pré-traitement** (filtrage speckle, calibration, reprojection)
5. **Analyse modulaire** selon les options activées
6. **Post-traitement** (agrégation, statistiques)
7. **Export** des résultats

---

## 2.2 Module Damage Detection

### 2.2.1 Principe général

La détection des dégâts repose sur la méthode **Pixel-Wise T-Test (PWTT)** développée par Ballinger (2024). Cette approche compare statistiquement deux périodes temporelles (pré et post-événement) pour identifier les changements significatifs de rétrodiffusion radar.

**Hypothèse fondamentale :** Les dégâts structurels modifient les propriétés de diffusion du signal radar (rugosité de surface, orientation des structures, humidité des matériaux).

### 2.2.2 Acquisition et prétraitement des données SAR

#### Sélection des images Sentinel-1

**Critères de filtrage :**
- Mode d'acquisition : **IW (Interferometric Wide swath)**
- Polarisation : **VV + VH** (dual-pol)
- Type de produit : **GRD (Ground Range Detected)**
- Résolution spatiale : **10m × 10m**

**Fenêtres temporelles :**
```
Pre-window:  [Pre-date - Pre_interval] ────► [Pre-date]
                                                  │
                                                  │  Normal period
                                                  ▼
Post-window:             [Event-date] ────► [Event-date + Post_interval]
```

**Expansion adaptative de la fenêtre post-événement :**

Si aucune image n'est trouvée dans la fenêtre initiale, l'algorithme étend progressivement la fenêtre par incréments de 1 jour jusqu'à :
- Trouver au moins 1 image, OU
- Atteindre une limite maximale de 6 jours supplémentaires

Cette approche garantit une couverture même en cas d'acquisitions irrégulières.

#### Filtrage du speckle

Le bruit de speckle, inhérent à l'imagerie SAR, est atténué par un **filtre de Lee adaptatif** (Lee, 1980).

**Principe :** Réduction du bruit tout en préservant les contours et les détails fins.

**Formule du filtre de Lee :**
```
I_filtered = I_mean + W × (I - I_mean)
```

Où :
- `I` = Valeur du pixel brut
- `I_mean` = Moyenne locale (fenêtre 3×3 pixels)
- `W` = Poids adaptatif fonction de la variance locale
- `η` = Coefficient de variation théorique (speckle multiplicatif)
```
W = (1 - η² / C_v²) / (1 + η²)
```

Où :
- `C_v = σ_local / I_mean` (coefficient de variation local)
- `η = 1 / √N_looks` (pour Sentinel-1 GRD, N_looks ≈ 5)

**Implémentation :**
```javascript
var eta = 1.0 / Math.sqrt(5);  // Sentinel-1 GRD ~ 5 looks
var kernel = ee.Kernel.square(1, 'pixels');  // Fenêtre 3×3
```

#### Transformation logarithmique

Les valeurs de rétrodiffusion sont transformées en échelle logarithmique (dB) :
```
σ_dB = 10 × log₁₀(σ₀)
```

Cette transformation :
- Normalise la distribution des valeurs
- Stabilise la variance
- Linéarise les relations radiométriques

### 2.2.3 Test statistique pixel-wise

#### Calcul de la statistique t de Student

Pour chaque pixel, un test t bilatéral est appliqué pour comparer les moyennes pré et post-événement.

**Hypothèse nulle H₀** : μ_pre = μ_post (pas de changement)  
**Hypothèse alternative H₁** : μ_pre ≠ μ_post (changement significatif)

**Formule de la statistique t :**
```
         μ_post - μ_pre
t = ─────────────────────────
    s_pooled × √(1/n_pre + 1/n_post)
```

Où :
```
         √[(n_pre - 1)s²_pre + (n_post - 1)s²_post]
s_pooled = ────────────────────────────────────────
                    n_pre + n_post - 2
```

Avec :
- `μ_pre` = Moyenne des valeurs pré-événement (dB)
- `μ_post` = Moyenne des valeurs post-événement (dB)
- `s²_pre`, `s²_post` = Variances échantillonnales
- `n_pre`, `n_post` = Nombre d'images (orbites distinctes)
- `s_pooled` = Écart-type pooled

**Degrés de liberté :**
```
df = n_pre + n_post - 2
```

**Implémentation GEE :**
```javascript
var preN = ee.Number(pre.aggregate_array('orbitNumber_start').distinct().size());
var postN = ee.Number(post.aggregate_array('orbitNumber_start').distinct().size());

var pooledSd = pre.reduce(ee.Reducer.stdDev()).pow(2).multiply(preN.subtract(1))
  .add(post.reduce(ee.Reducer.stdDev()).pow(2).multiply(postN.subtract(1)))
  .divide(preN.add(postN).subtract(2)).sqrt();

var denom = pooledSd.multiply(
  ee.Image.constant(1).divide(preN).add(ee.Image.constant(1).divide(postN)).sqrt()
);

var T_stat = postMean.subtract(preMean).divide(denom).abs();
```

**Note :** La valeur absolue est utilisée car seule la magnitude du changement importe (dégâts = augmentation ou diminution de la rétrodiffusion).

#### Traitement multi-orbites

Sentinel-1 acquiert des données selon plusieurs **orbites relatives** (passages ascendants et descendants). Pour éviter les biais angulaires, le test t est calculé **séparément pour chaque orbite**, puis les résultats sont fusionnés par maximum :
```
T_final(x,y) = max [T_orbit1(x,y), T_orbit2(x,y), ..., T_orbitN(x,y)]
```

Cette approche conserve le changement le plus significatif détecté, quelle que soit la géométrie d'acquisition.

### 2.2.4 Lissage spatial multi-échelle

Pour réduire le bruit résiduel et mettre en évidence les structures cohérentes, un **lissage gaussien multi-échelle** est appliqué :
```
T_smooth = (T_raw + T_50m + T_100m + T_150m) / 4
```

Où :
- `T_raw` = Statistique t brute
- `T_50m` = Convolution avec noyau gaussien de rayon 50m
- `T_100m` = Convolution avec noyau gaussien de rayon 100m
- `T_150m` = Convolution avec noyau gaussien de rayon 150m

**Justification :** Les bâtiments endommagés présentent généralement des signatures spatiales cohérentes sur plusieurs pixels. Le lissage multi-échelle :
- Renforce les structures de taille caractéristique 50-150m
- Atténue les faux positifs isolés (bruit, artefacts)
- Préserve les contours des zones endommagées

**Implémentation :**
```javascript
var T_stat_urban = maxChange_raw
  .add(maxChange_raw.convolve(ee.Kernel.circle(50, 'meters', true)))
  .add(maxChange_raw.convolve(ee.Kernel.circle(100, 'meters', true)))
  .add(maxChange_raw.convolve(ee.Kernel.circle(150, 'meters', true)))
  .divide(4);
```

### 2.2.5 Classification des niveaux de dégâts

#### Seuillage de la statistique t

Un seuil `T_threshold` (défaut : 2.4) est appliqué pour classifier les pixels :
```
Damage = {
  0  si T < T_threshold        (pas de dégât)
  1  si T ≥ T_threshold        (dégât détecté)
}
```

**Justification du seuil 2.4 :**
- Pour un test t bilatéral avec df ≈ 10-20 :
  - t = 2.4 correspond approximativement à p < 0.05 (95% de confiance)
- Compromis empirique entre :
  - Sensibilité (détecter les dégâts légers)
  - Spécificité (éviter les faux positifs)

#### Niveaux de confiance

Les bâtiments classés comme endommagés sont sous-divisés en trois niveaux de confiance :

| Niveau | Plage de T | Interprétation |
|--------|-----------|----------------|
| **Moderate** | T_threshold ≤ T < T_threshold + 1 | Changement modéré, validation recommandée |
| **High** | T_threshold + 1 ≤ T < T_threshold + 2 | Changement élevé, forte probabilité de dégât |
| **Very High** | T ≥ T_threshold + 2 | Changement très élevé, dégât quasi-certain |

**Exemple avec T_threshold = 2.4 :**
- Moderate : 2.4 ≤ T < 3.4
- High : 3.4 ≤ T < 4.4
- Very High : T ≥ 4.4

### 2.2.6 Agrégation sur les bâtiments

#### Extraction des statistiques par bâtiment

Pour chaque polygone de bâtiment, la **moyenne** de la statistique t est calculée :
```javascript
var fp = T_stat_image.reduceRegions({
  collection: buildings,
  reducer: ee.Reducer.mean(),
  scale: 10
});
```

**Justification de la moyenne :**
- Robuste aux valeurs extrêmes locales
- Représente le changement global du bâtiment
- Compatible avec la théorie du test t (échantillonnage multiple)

#### Attribution des classes

Chaque bâtiment reçoit :
- **T_statistic** : Valeur moyenne de t
- **damage** : 0 (intact) ou 1 (endommagé)
- **confidence** : Moderate / High / Very High

### 2.2.7 Traitement des routes

#### Segmentation du réseau routier

Les routes linéaires sont segmentées en tronçons de longueur fixe (défaut : 100m) via une grille spatiale :
```
┌────────────────────────────────────────┐
│         │         │         │          │
│  Cell   │  Cell   │  Cell   │  Cell    │
│  (100m) │  (100m) │  (100m) │  (100m)  │
│         │         │         │          │
├─────────┼─────────┼─────────┼──────────┤
│    Road segments intersected           │
└────────────────────────────────────────┘
```

**Algorithme :**
1. Créer une grille régulière de cellules de 100m × 100m
2. Dissoudre toutes les lignes de routes en une seule géométrie
3. Intersecter cette géométrie avec chaque cellule de la grille
4. Conserver les segments non vides

#### Buffer et extraction des statistiques

Chaque segment routier est bufferisé (défaut : 6m de rayon) pour capturer les pixels adjacents :
```
─────────────────  Route (ligne)
     ▓▓▓▓▓         Buffer 6m
─────────────────
```

La statistique **maximum** de t est extraite dans chaque buffer :
```javascript
var roadsStats = T_stat_roads.reduceRegions({
  collection: roadsSegmented.map(function(f) { 
    return f.buffer(BUFFER_ROADS_M); 
  }),
  reducer: ee.Reducer.max(),
  scale: 10
});
```

**Justification du maximum :**
- Les routes endommagées présentent souvent des dégâts ponctuels (cratères, effondrements)
- Le maximum capture ces anomalies locales
- Plus sensible que la moyenne pour les structures linéaires

---

## 2.3 Module Flood Detection

### 2.3.1 Principe général

La détection des inondations exploite la **diminution drastique de la rétrodiffusion radar** en présence d'eau. L'algorithme s1flood (DeVries et al., 2020) utilise une approche par **z-score** (écart normalisé) pour identifier les pixels anormalement sombres.

**Principe physique :**
- Surface d'eau calme : réflexion spéculaire → faible rétrodiffusion (pixels sombres)
- Sol sec ou végétation : diffusion volumique → forte rétrodiffusion (pixels clairs)

### 2.3.2 Calcul du z-score

#### Définition de la période de référence

Une période de référence ("baseline") est définie pour caractériser l'état normal :
```
Baseline: [Pre-date - Pre_interval] ────► [Pre-date]
```

Pour chaque pixel, la **moyenne** (μ_baseline) et l'**écart-type** (σ_baseline) sont calculés sur toutes les images de cette période.

#### Normalisation par z-score

Pour chaque image post-événement, le z-score est calculé :
```
         I_post - μ_baseline
z(x,y) = ───────────────────
            σ_baseline
```

Où :
- `I_post` = Valeur du pixel dans l'image post-événement (dB)
- `μ_baseline` = Moyenne du pixel pendant la période de référence
- `σ_baseline` = Écart-type du pixel pendant la période de référence

**Interprétation :**
- z ≈ 0 : Valeur normale
- z < -2 : Valeur anormalement faible (potentiel d'inondation)
- z < -3 : Valeur très anormalement faible (forte probabilité d'inondation)

#### Séparation par orbite et polarisation

Le z-score est calculé **séparément** pour :
- **Mode d'acquisition** : IW (Interferometric Wide)
- **Direction d'orbite** : Ascendante (ASCENDING) / Descendante (DESCENDING)
- **Polarisation** : VV et VH

Cette séparation garantit la cohérence radiométrique des comparaisons (même géométrie d'acquisition).

**Implémentation :**
```javascript
var z_asc = calcZscore(s1Collection, baseStart, baseEnd, 'IW', 'ASCENDING');
var z_dsc = calcZscore(s1Collection, baseStart, baseEnd, 'IW', 'DESCENDING');
var zAll = ee.ImageCollection(z_asc.merge(z_dsc));
```

### 2.3.3 Classification des inondations

#### Seuils de z-score

Deux seuils sont appliqués sur les polarisations VV et VH :
```
ZVV_threshold = -2.5  (défaut)
ZVH_threshold = -2.5  (défaut)
```

Un pixel est considéré comme potentiellement inondé si :
```
Flood_candidate = (z_VV < ZVV_threshold) ∨ (z_VH < ZVH_threshold)
```

L'opérateur logique **OU** permet de capturer les inondations même si une seule polarisation montre un signal fort.

#### Masquage de l'eau permanente

Pour distinguer les **nouvelles inondations** de l'**eau permanente**, deux sources sont utilisées :

**1. ESA WorldCover v200**
- Classe 80 : Permanent water bodies
- Résolution : 10m
- Année : 2021

**2. JRC Global Surface Water (Monthly History)**
- Fréquence d'occurrence de l'eau (%)
- Résolution : 30m
- Période : 1984-présent

**Algorithme de masquage :**
```javascript
var worldcoverWater = worldcover.eq(80);  // Eau permanente (WorldCover)

var jrcvalid = jrc.map(function(x) { return x.gt(0); }).sum();  // Mois valides
var jrcwat = jrc.map(function(x) { return x.eq(2); }).sum()     // Mois avec eau
  .divide(jrcvalid).multiply(100);                              // Fréquence (%)

var permanentWater = jrcwat.gte(POW_threshold);  // POW_threshold = 90% (défaut)
var inundation = jrcwat.gte(PIN_threshold)       // PIN_threshold = 25% (défaut)
                       .and(jrcwat.lt(POW_threshold));
```

**Classes résultantes :**

| Classe | Code | Description |
|--------|------|-------------|
| Permanent water | 20 | Eau permanente (WorldCover ou JRC > 90%) |
| Flood (VV only) | 1 | z_VV < seuil, z_VH > seuil |
| Flood (VH only) | 2 | z_VH < seuil, z_VV > seuil |
| Flood (VV + VH) | 3 | z_VV < seuil ET z_VH < seuil |
| Flood (Inundation) | 10 | Zone historiquement inondable (25% < JRC < 90%) |

### 2.3.4 Post-traitement morphologique

#### Filtrage par pente

Les zones de forte pente sont exclues car l'eau ne peut s'y accumuler :
```javascript
var slope = ee.Terrain.slope(elevation);
flood = flood.updateMask(slope.lt(MAX_SLOPE));  // MAX_SLOPE = 5° (défaut)
```

**Justification :** Pentes > 5° : ruissellement rapide, accumulation improbable.

#### Filtrage par connectivité

Les pixels isolés (artefacts, ombres) sont éliminés par un filtre de connectivité :
```javascript
var connectedPixels = flood.connectedPixelCount();
flood = flood.updateMask(connectedPixels.gte(MIN_CONNECTIVITY));
// MIN_CONNECTIVITY = 8 pixels (défaut)
```

**Principe :** Un pixel est conservé seulement s'il est connecté à au moins 8 autres pixels inondés (composante connexe de taille ≥ 8).

#### Lissage spatial

Un filtre médian circulaire est appliqué pour régulariser les contours :
```javascript
flood = flood.focal_median(SMOOTHING_RADIUS, 'circle', 'meters');
// SMOOTHING_RADIUS = 25m (défaut)
```

**Effet :** Lissage des contours irréguliers, fermeture des petites discontinuités.

### 2.3.5 Série temporelle (Time Series Mode)

#### Principe

Lorsque l'option "Time Series" est activée, l'algorithme traite **toutes les dates Sentinel-1** disponibles dans la période spécifiée :
```
Time series window: [From_date] ────────────────► [To_date]
                         │                           │
                         ▼                           ▼
                    Image 1, Image 2, ..., Image N
```

Pour chaque date, une carte d'inondation est générée en appliquant l'algorithme s1flood.

#### Calcul de la surface inondée

Pour chaque date, la surface inondée est calculée :
```javascript
var floodMask = floodLayer.gt(0);
var floodArea = floodMask.multiply(ee.Image.pixelArea()).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 10,
  maxPixels: 1e13
});
var areaKm2 = ee.Number(floodArea.get('flood_class')).divide(1e6);
```

**Unité :** km²

#### Séparation par orbite

Les résultats sont séparés par direction d'orbite (Ascendante / Descendante) pour suivre l'évolution indépendamment de la géométrie d'acquisition :
```
Date       │ Ascending (km²) │ Descending (km²)
───────────┼─────────────────┼──────────────────
2025-09-05 │      0.052      │       -
2025-09-08 │       -         │      0.048
2025-09-11 │      0.103      │       -
2025-09-14 │       -         │      0.087
```

#### Graphique d'évolution

Un graphique de type **ColumnChart** (barres verticales) est généré avec :
- Axe X : Dates
- Axe Y : Surface inondée (km²)
- Série 1 : Orbites ascendantes (bleu clair)
- Série 2 : Orbites descendantes (bleu foncé)

**Interprétation :**
- Permet d'identifier le **pic de crue**
- Permet de suivre la **décrue progressive**
- Permet de détecter les **inondations résiduelles**

#### Détection de baseline humide

Si la première date de la série temporelle montre déjà une surface inondée significative (> 0.5 km²), un avertissement est affiché :
```
⚠️ WARNING: Baseline appears wet!
First date (2025-09-05) shows 0.52 km² already flooded
💡 SUGGESTION: Move PRE_DATE earlier to ensure dry baseline
   Recommended PRE_DATE: 2025-08-05
```

Cette détection garantit que la période de référence est bien "sèche".

---

## 2.4 Module Landslide Detection

### 2.4.1 Principe général

La détection des glissements de terrain combine deux approches complémentaires :

1. **Détection de changements SAR** (similaire au module Damage)
2. **Modèle de susceptibilité** basé sur des facteurs environnementaux

**Hypothèse :** Les glissements de terrain se produisent préférentiellement dans des zones combinant :
- Changement de rétrodiffusion SAR (mouvement de terrain)
- Facteurs prédisposants (pente, courbure, précipitations, type de sol)

### 2.4.2 Facteurs de susceptibilité

Le modèle de susceptibilité agrège **cinq facteurs** pondérés, inspiré de Kanani-Sadat et al. (2015) :

#### Facteur 1 : Précipitations cumulées (poids : 0.143)

**Source :** CHIRPS Daily (Climate Hazards Group InfraRed Precipitation with Station data)

**Fenêtre temporelle :** 30 jours précédant l'événement
```javascript
var precipStart = ee.Date(EVENT_DATE).advance(-30, 'day');
var precipEnd = ee.Date(EVENT_DATE);
var precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
  .select('precipitation')
  .filterDate(precipStart, precipEnd)
  .sum();
```

**Normalisation :**
```
precipScore = min(precip / 300, 1) × 0.143
```

**Justification :**
- 300 mm en 30 jours ≈ seuil de saturation du sol
- Poids 0.143 (14.3%) basé sur l'analyse AHP de Kanani-Sadat et al.

#### Facteur 2 : Pente (poids : 0.128)

**Calcul :**
```javascript
var slope = ee.Terrain.slope(elevation);
```

**Normalisation :**
```
slopeScore = min(slope / 30, 1) × 0.128
```

**Justification :**
- Pentes > 30° : susceptibilité maximale
- Poids 0.128 (12.8%)

#### Facteur 3 : Type de sol - Argile (poids : 0.123)

**Source :** SoilGrids ISRIC (teneur en argile, 0-5 cm de profondeur)
```javascript
var clay = ee.Image('projects/soilgrids-isric/clay_mean')
  .select('clay_0-5cm_mean');
```

**Normalisation :**
```
soilScore = (clay / 100) × 0.123
```

**Justification :**
- Sols argileux : faible perméabilité, instabilité en présence d'eau
- Poids 0.123 (12.3%)

#### Facteur 4 : Aspect (orientation du versant) (poids : 0.112)

**Calcul :**
```javascript
var aspect = ee.Terrain.aspect(elevation);
var northFacing = aspect.lte(45).or(aspect.gte(315));
```

**Score :**
```
aspectScore = northFacing ? 1.0 × 0.112 : 0.5 × 0.112
```

**Justification :**
- Versants nord (hémisphère nord) : moins d'ensoleillement, humidité résiduelle
- Poids 0.112 (11.2%)

#### Facteur 5 : Courbure du terrain (poids : 0.100)

**Calcul :** Courbure = divergence du gradient d'élévation
```javascript
var smooth_curv = ee.Kernel.gaussian({
  radius: 60, 
  sigma: 30, 
  units: 'meters', 
  normalize: true
});
var elevation_smooth = elevation.convolve(smooth_curv);
var xyDemGrad = elevation_smooth.gradient();
var xGradient = xyDemGrad.select('x').gradient();
var yGradient = xyDemGrad.select('y').gradient();
var curvature = xGradient.select('x').add(yGradient.select('y'));
```

**Normalisation :**
```
curvatureScore = min(|curvature| / 0.2, 1) × 0.100
```

**Justification :**
- Courbure élevée (concave ou convexe) : zones d'instabilité structurelle
- Poids 0.100 (10.0%)

#### Score de susceptibilité total
```
S_total = precipScore + slopeScore + soilScore + aspectScore + curvatureScore
```

**Plage :** 0 à 0.606 (somme des poids)

### 2.4.3 Masquage par changement SAR

La statistique t issue du module Damage Detection est réutilisée, avec des masques spécifiques :

**Masque 1 : Pente minimale**
```javascript
var mask_slope = slope.gte(MIN_SLOPE);  // MIN_SLOPE = 10° (défaut)
```

**Masque 2 : Courbure minimale**
```javascript
var mask_curvature = curvature.gte(MIN_CURVATURE);  // MIN_CURVATURE = 0.05 (défaut)
```

**Masque 3 : Exclusion des zones d'eau**
```javascript
var waterMask = worldcover.neq(80);  // Exclure classe "eau" de WorldCover
```

**Application :**
```javascript
var T_stat_landslide = maxChange_raw
  .updateMask(mask_slope)
  .updateMask(mask_curvature)
  .updateMask(waterMask);
```

### 2.4.4 Classification des niveaux de probabilité

Les pixels sont classés en fonction de la **combinaison** du score de susceptibilité et de la statistique t :
```
Landslide_level = {
  0  (no landslide)      si S_total < 0.3 OU T < T_threshold
  1  (Moderate)          si S_total ≥ 0.3 ET T_threshold ≤ T < T_threshold + 1
  2  (High)              si S_total ≥ 0.3 ET T_threshold + 1 ≤ T < T_threshold + 2
  3  (Very High)         si S_total ≥ 0.3 ET T ≥ T_threshold + 2
}
```

**Seuil de susceptibilité : 0.3**
- Correspond approximativement à 50% du score maximal possible (0.606)
- Filtre les zones à faible prédisposition

### 2.4.5 Zones d'écoulement (Runout Zones)

Les glissements de terrain peuvent générer des coulées de débris qui s'écoulent vers l'aval. Une **zone d'exposition** est calculée par dilatation morphologique :
```javascript
var kernel = ee.Kernel.circle({radius: 100, units: 'meters'});
var runoutZone = landslides.gt(0).focal_max({kernel: kernel})
  .subtract(landslides.gt(0))
  .selfMask();
```

**Principe :**
1. Dilatation des zones de glissement (rayon : 100m)
2. Soustraction des zones sources
3. Résultat : couronne de 100m autour des glissements

**Interprétation :** Zone potentiellement affectée par l'écoulement de débris, même en l'absence de glissement in-situ.

---

## 2.5 Module Weather Statistics

### 2.5.1 Sources de données

Le module météo agrège des données provenant de deux sources principales :

| Variable | Source | Résolution spatiale | Résolution temporelle |
|----------|--------|--------------------|--------------------|
| Précipitations | CHIRPS Daily | 5.5 km | Quotidienne |
| Vent instantané | GLDAS NOAH v2.1 | 27.8 km | 3-horaire |
| Pression de surface | GLDAS NOAH v2.1 | 27.8 km | 3-horaire |

### 2.5.2 Fenêtre temporelle

**Mode standard :**
```
[Pre-date] ──────────────────────► [Event-date + 3 jours]
```

**Mode Time Series (si activé) :**
```
[TIME_SERIES_START] ─────────────► [TIME_SERIES_END]
```

### 2.5.3 Agrégation quotidienne

Pour chaque jour de la période :

**Précipitations :**
- Somme quotidienne (mm/jour)

**Vent :**
- Conversion en km/h : `wind_kmh = wind_m/s × 3.6`
- Moyenne quotidienne (vent moyen)
- Maximum quotidien (rafale maximale)

**Pression :**
- Conversion en hPa : `pressure_hPa = pressure_Pa / 100`
- Moyenne quotidienne
- Minimum quotidien (indicateur de dépression)

### 2.5.4 Statistiques globales

Pour l'ensemble de la période :
```javascript
var totalPrecip = sum(daily_precip);              // Précipitations cumulées (mm)
var maxPrecip = max(daily_precip);                // Pluie quotidienne maximale (mm)
var maxWind = max(daily_wind_max);                // Rafale maximale (km/h)
var minPressure = min(daily_pressure_min);        // Pression minimale (hPa)
```

Ces valeurs sont affichées dans le panneau de résultats et permettent de caractériser l'intensité de l'événement.

### 2.5.5 Visualisation graphique

**Graphique 1 : Précipitations quotidiennes (ColumnChart)**

- Axe X : Dates (MM/DD)
- Axe Y : Précipitations (mm)
- Couleur : Bleu (normal), Rouge (jour de l'événement)

**Graphique 2 : Vent et Pression (LineChart multi-axes)**

- Axe X : Dates (MM/DD)
- Axe Y gauche : Vent (km/h)
  - Ligne verte continue : Vent moyen
  - Ligne verte pointillée : Vent maximal
- Axe Y droit : Pression (hPa)
  - Ligne jaune continue : Pression moyenne
  - Ligne rouge pointillée : Pression minimale

**Interpolation :** `interpolateNulls: true` pour lisser les données manquantes.

---

## 2.6 Calcul des indicateurs de performance

### 2.6.1 Indicateurs de dégâts (Damage)

**Exhaustivité des dégâts :**
```
         Nombre de bâtiments endommagés
E_d = ────────────────────────────────────
      Nombre total de bâtiments dans l'AOI
```

**Densité spatiale des dégâts :**

Calculée par rasterisation des bâtiments endommagés (résolution : 100m) puis échantillonnage spatial :
```javascript
var damageRaster = damaged.reduceToImage({
  properties: ['damage'],
  reducer: ee.Reducer.count()
}).reproject({crs: 'EPSG:4326', scale: 100});
```

Les "density bubbles" (cercles proportionnels) sont générés par :
```
radius_bubble = √(count) × 25 mètres
```

### 2.6.2 Indicateurs d'inondation (Flood)

**Surface inondée :**
```
                  Σ (pixelArea) pour flood > 0
A_flood (km²) = ─────────────────────────────────
                        1 000 000
```

**Proportion de bâtiments inondés :**
```
         Nombre de bâtiments en zone inondée
P_b = ────────────────────────────────────────
      Nombre total de bâtiments dans l'AOI
```

**Longueur de routes inondées :**
```
L_road (km) = (Nombre de segments inondés) × (Longueur segment) / 1000
```

### 2.6.3 Indicateurs de glissements de terrain (Landslide)

**Surface en zone de susceptibilité :**
```
                    Σ (pixelArea) pour landslide > 0
A_landslide (km²) = ──────────────────────────────────
                            1 000 000
```

**Répartition par niveau :**
```
A_moderate = Σ (pixelArea) pour landslide = 1
A_high = Σ (pixelArea) pour landslide = 2
A_very_high = Σ (pixelArea) pour landslide = 3
```

### 2.6.4 Logistic Hub (Point d'Accès Logistique)

Le "logistic hub" est calculé comme un **barycentre pondéré** des dégâts, ajusté en fonction de la proximité aux infrastructures (ports, aéroports).

**Étape 1 : Barycentre des dégâts**
```
       Σ (lon_i × count_i)
lon_bary = ──────────────────
          Σ (count_i)

       Σ (lat_i × count_i)
lat_bary = ──────────────────
          Σ (count_i)
```

Où :
- `(lon_i, lat_i)` = Coordonnées du point d'échantillonnage i
- `count_i` = Nombre de bâtiments endommagés dans la cellule i

**Étape 2 : Centroïde des infrastructures**

Si des ports ou aéroports sont présents dans l'AOI :
```
centroid_infra = Centroïde (Union de tous les ports et aéroports)
```

**Étape 3 : Hub pondéré**
```
lon_hub = 0.7 × lon_infra + 0.3 × lon_bary
lat_hub = 0.7 × lat_infra + 0.3 × lat_bary
```

**Justification :**
- Poids 70% sur les infrastructures : privilégie l'accessibilité
- Poids 30% sur les dégâts : garantit la proximité aux zones affectées

**Étape 4 : Projection sur le réseau routier**

Le hub est projeté sur le segment routier le plus proche (distance < 10m) pour garantir son accessibilité.

---

## 2.7 Limitations méthodologiques

### 2.7.1 Limitations du module Damage Detection

**Sensibilité aux conditions d'acquisition :**
- La rétrodiffusion SAR est influencée par l'humidité du sol
- Des précipitations entre les acquisitions pré et post peuvent générer des faux positifs

**Confusion avec d'autres changements :**
- Débris végétaux (arbres tombés) : signal similaire aux dégâts structurels
- Inondations résiduelles : diminution de rétrodiffusion confondue avec des dégâts

**Résolution spatiale :**
- Sentinel-1 : 10m × 10m
- Petits bâtiments (< 100 m²) : signature radar faible, détection limitée

**Géométrie radar :**
- Ombres et layover en zones montagneuses
- Foreshortening sur les pentes face au satellite

### 2.7.2 Limitations du module Flood Detection

**Végétation dense :**
- La canopée forestière masque l'eau sous-jacente
- Sous-estimation des inondations en forêt tropicale

**Eaux peu profondes :**
- Faible profondeur (< 10 cm) : signal radar atténué mais non nul
- Risque de non-détection

**Acquisitions limitées :**
- Sentinel-1 : revisite ~6 jours
- Crues éclair de courte durée (< 6 jours) : potentiellement manquées

**Eau permanente :**
- Dépendance aux bases de données JRC et WorldCover
- Zones humides saisonnières parfois mal classées

### 2.7.3 Limitations du module Landslide Detection

**Modèle de susceptibilité empirique :**
- Poids des facteurs issus de la littérature (Kanani-Sadat et al., 2015)
- Non calibrés spécifiquement pour chaque région

**Résolution du DEM :**
- NASADEM / SRTM : 30m
- Incapacité à détecter les micro-topographies (< 30m)

**Délai de détection :**
- Les glissements de terrain se manifestent progressivement
- Signal SAR optimal après consolidation (plusieurs jours/semaines)

**Confusion avec la végétation :**
- Déforestation, coupes forestières : signature radar similaire

### 2.7.4 Limitations du module Weather Statistics

**Résolution spatiale :**
- CHIRPS : 5.5 km
- GLDAS : 27.8 km
- Variabilité infrakilométrique non capturée (orages localisés)

**Précision des mesures :**
- CHIRPS : estimations satellite, non mesures in-situ
- GLDAS : modèle assimilant des observations hétérogènes

**Couverture temporelle :**
- GLDAS : résolution 3-horaire
- Phénomènes de très courte durée (rafales < 1h) : potentiellement manqués

### 2.7.5 Recommandations pour atténuer les limitations

1. **Validation systématique** par photo-interprétation HR
2. **Croisement multi-sources** (SAR + optique + terrain)
3. **Connaissance du contexte local** (géologie, urbanisme, climatologie)
4. **Analyse critique des résultats** (faux positifs, faux négatifs)
5. **Communication transparente des incertitudes** auprès des utilisateurs finaux

---

## 2.8 Perspectives d'amélioration

### 2.8.1 Améliorations algorithmiques

**Fusion SAR + Optique :**
- Intégration de Sentinel-2 (optique) pour réduire les ambiguïtés SAR
- Détection de dégâts par changement de NDVI (végétation)

**Machine Learning :**
- Entraînement de modèles supervisés (Random Forest, CNN) sur des datasets annotés
- Classification automatique des types de dégâts (effondrement, fissuration, etc.)

**Analyse multi-temporelle avancée :**
- Suivi de l'évolution des dégâts sur plusieurs semaines/mois
- Détection de dégâts progressifs (tassement, affaissement)

### 2.8.2 Intégration de nouvelles sources de données

**Imagerie SAR haute résolution :**
- ICEYE (résolution < 1m)
- Capella Space (résolution sub-métrique)

**Données d'élévation LiDAR :**
- Détection de changements d'élévation (effondrements)
- Modélisation 3D précise

**Réseaux sociaux et crowdsourcing :**
- Tweets géolocalisés, photos Flickr
- Validation rapide par les populations locales

### 2.8.3 Développement d'une version mobile/terrain

**Application mobile :**
- Affichage des résultats sur smartphone/tablette
- Collecte de données terrain (photos, GPS)
- Synchronisation bidirectionnelle (cloud ↔ terrain)

**Mode hors-ligne :**
- Pré-téléchargement des cartes et résultats
- Utilisation en zones sans connectivité

---

---

<a name="sources-données"></a>
# 3. Sources de Données

## 3.1 Données satellitaires

### 3.1.1 Sentinel-1 SAR

**Description :** Constellation de satellites radar en bande C (5.405 GHz) de l'Agence Spatiale Européenne (ESA).

**Spécifications techniques :**
- **Satellites :** Sentinel-1A (lancé 2014), Sentinel-1B (lancé 2016, hors service depuis 2021), Sentinel-1C (prévu 2024)
- **Mode d'acquisition utilisé :** Interferometric Wide Swath (IW)
- **Polarisation :** Dual-pol (VV+VH)
- **Résolution spatiale :** 10m × 10m (GRD)
- **Fauchée :** 250 km
- **Période de revisite :** ~6 jours (constellation complète)
- **Orbites :** Ascendantes et descendantes

**Produit utilisé :**
- **Type :** GRD (Ground Range Detected)
- **Processing level :** Level-1
- **Collection GEE :** `COPERNICUS/S1_GRD` et `COPERNICUS/S1_GRD_FLOAT`

**Référence :**
- ESA Sentinel Online: [https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1)

---

### 3.1.2 CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)

**Description :** Données de précipitations quotidiennes à résolution quasi-globale, combinant observations satellite infrarouge et stations au sol.

**Spécifications :**
- **Résolution spatiale :** 0.05° (~5.5 km)
- **Résolution temporelle :** Quotidienne
- **Couverture temporelle :** 1981-présent
- **Couverture spatiale :** 50°N - 50°S
- **Unité :** mm/jour

**Collection GEE :** `UCSB-CHG/CHIRPS/DAILY`

**Référence :**
- Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*, 2, 150066. [https://doi.org/10.1038/sdata.2015.66](https://doi.org/10.1038/sdata.2015.66)
- Site officiel: [https://www.chc.ucsb.edu/data/chirps](https://www.chc.ucsb.edu/data/chirps)

---

### 3.1.3 GLDAS (Global Land Data Assimilation System)

**Description :** Système d'assimilation de données terrestres fournissant des variables météorologiques et hydrologiques à l'échelle globale.

**Version utilisée :** GLDAS-2.1 NOAH

**Spécifications :**
- **Résolution spatiale :** 0.25° (~27.8 km)
- **Résolution temporelle :** 3-horaire
- **Variables utilisées :**
  - `Wind_f_inst` : Vitesse du vent instantanée (m/s)
  - `Psurf_f_inst` : Pression de surface instantanée (Pa)
- **Couverture temporelle :** 2000-présent

**Collection GEE :** `NASA/GLDAS/V021/NOAH/G025/T3H`

**Référence :**
- Rodell, M., Houser, P. R., Jambor, U., et al. (2004). The Global Land Data Assimilation System. *Bulletin of the American Meteorological Society*, 85(3), 381-394. [https://doi.org/10.1175/BAMS-85-3-381](https://doi.org/10.1175/BAMS-85-3-381)

---

## 3.2 Modèles numériques de terrain (DEM)

### 3.2.1 NASADEM

**Description :** Modèle numérique d'élévation global dérivé de la mission SRTM, retraité par la NASA pour améliorer la précision.

**Spécifications :**
- **Résolution spatiale :** 1 arc-seconde (~30m)
- **Couverture spatiale :** 60°N - 56°S
- **Précision verticale :** ±9m (90% de confiance)
- **Année de référence :** 2000 (acquisition SRTM)

**Collection GEE :** `NASA/NASADEM_HGT/001`

**Référence :**
- NASA JPL (2020). NASADEM Merged DEM Global 1 arc second. [https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001)

---

### 3.2.2 SRTM (Shuttle Radar Topography Mission)

**Description :** DEM global acquis par la mission spatiale SRTM en 2000.

**Spécifications :**
- **Résolution spatiale :** 1 arc-seconde (~30m)
- **Couverture spatiale :** 60°N - 56°S
- **Précision verticale :** ±16m (90% de confiance)

**Collection GEE :** `USGS/SRTMGL1_003`

**Référence :**
- Farr, T. G., Rosen, P. A., Caro, E., et al. (2007). The Shuttle Radar Topography Mission. *Reviews of Geophysics*, 45(2). [https://doi.org/10.1029/2005RG000183](https://doi.org/10.1029/2005RG000183)

---

### 3.2.3 ALOS World 3D

**Description :** DEM global basé sur les données du satellite japonais ALOS PRISM.

**Spécifications :**
- **Résolution spatiale :** 1 arc-seconde (~30m)
- **Couverture spatiale :** Globale (82°N - 82°S)
- **Précision verticale :** ±5m (zones plates), ±7m (zones montagneuses)
- **Version :** 3.2

**Collection GEE :** `JAXA/ALOS/AW3D30/V3_2`

**Référence :**
- JAXA (2021). ALOS Global Digital Surface Model "ALOS World 3D-30m" (AW3D30). [https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm](https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm)

---

### 3.2.4 ASTER GDEM

**Description :** DEM global issu du radiomètre ASTER (Advanced Spaceborne Thermal Emission and Reflection Radiometer).

**Spécifications :**
- **Résolution spatiale :** 1 arc-seconde (~30m)
- **Couverture spatiale :** 83°N - 83°S
- **Précision verticale :** ±17m (95% de confiance)
- **Version :** 3

**Collection GEE :** `NASA/ASTER_GED/AG100_003`

**Référence :**
- NASA/METI/AIST/Japan Spacesystems, U.S./Japan ASTER Science Team (2019). ASTER Global Digital Elevation Model V003. [https://doi.org/10.5067/ASTER/ASTGTM.003](https://doi.org/10.5067/ASTER/ASTGTM.003)

---

## 3.3 Données de couverture du sol

### 3.3.1 ESA WorldCover

**Description :** Carte de couverture du sol à 10m de résolution basée sur Sentinel-1 et Sentinel-2.

**Spécifications :**
- **Résolution spatiale :** 10m
- **Année de référence :** 2021
- **Nomenclature :** 11 classes (Tree cover, Shrubland, Grassland, Cropland, Built-up, Bare/sparse vegetation, Snow/ice, Permanent water bodies, Herbaceous wetland, Mangroves, Moss/lichen)
- **Précision globale :** 74.4%

**Collection GEE :** `ESA/WorldCover/v200`

**Référence :**
- Zanaga, D., Van De Kerchove, R., Daems, D., et al. (2022). ESA WorldCover 10 m 2021 v200. [https://doi.org/10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221)

---

### 3.3.2 JRC Global Surface Water

**Description :** Cartes mensuelles et annuelles de présence d'eau de surface basées sur 38 ans d'imagerie Landsat.

**Spécifications :**
- **Résolution spatiale :** 30m
- **Couverture temporelle :** 1984-2022
- **Résolution temporelle :** Mensuelle
- **Produit utilisé :** Monthly History (occurrence d'eau par mois)

**Collection GEE :** `JRC/GSW1_4/MonthlyHistory`

**Référence :**
- Pekel, J.-F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature*, 540, 418-422. [https://doi.org/10.1038/nature20584](https://doi.org/10.1038/nature20584)

---

## 3.4 Données de population

### 3.4.1 WorldPop

**Description :** Estimations de population désagrégées à haute résolution spatiale basées sur des recensements et données auxiliaires.

**Spécifications :**
- **Résolution spatiale :** 100m
- **Unité :** Nombre d'habitants par pixel
- **Méthodologie :** Random Forest sur covariables (bâti, occupation du sol, accessibilité, etc.)
- **Mise à jour :** Annuelle

**Collection GEE :** `WorldPop/GP/100m/pop`

**Référence :**
- Tatem, A. J. (2017). WorldPop, open data for spatial demography. *Scientific Data*, 4, 170004. [https://doi.org/10.1038/sdata.2017.4](https://doi.org/10.1038/sdata.2017.4)
- Site officiel: [https://www.worldpop.org/](https://www.worldpop.org/)

---

### 3.4.2 WSF 3D - Building Height

**Description :** Carte globale de hauteur de bâtiments à 90m de résolution dérivée de données SAR TanDEM-X et optiques Sentinel-2.

**Spécifications :**
- **Résolution spatiale :** 90m (3 arc-secondes)
- **Unité :** Mètres (hauteur du bâtiment)
- **Couverture temporelle :** 2015-2017
- **Précision :** RMSE ~6m pour bâtiments > 15m de hauteur

**Source :** DLR (German Aerospace Center)

**Téléchargement :** [https://download.geoservice.dlr.de/WSF3D/files/](https://download.geoservice.dlr.de/WSF3D/files/)

**Référence :**
- Esch, T., Brzoska, E., Dech, S., et al. (2022). World Settlement Footprint 3D - A first three-dimensional survey of the global building stock. *Remote Sensing of Environment*, 270, 112877. [https://doi.org/10.1016/j.rse.2021.112877](https://doi.org/10.1016/j.rse.2021.112877)

---

## 3.5 Données vectorielles

### 3.5.1 Google Open Buildings v3

**Description :** Base de données de contours de bâtiments détectés par machine learning à partir d'imagerie satellite.

**Spécifications :**
- **Couverture :** Afrique, Asie du Sud, Asie du Sud-Est, Amérique latine (hors USA, Canada, Europe)
- **Nombre de bâtiments :** ~1.8 milliards
- **Résolution source :** 50 cm (imagerie Maxar)
- **Méthodologie :** Détection par réseau de neurones convolutifs (U-Net)
- **Attribut principal :** `confidence` (score de confiance 0-1)

**Collection GEE :** `GOOGLE/Research/open-buildings/v3/polygons`

**Référence :**
- Google Research (2023). Open Buildings V3. [https://sites.research.google/open-buildings/](https://sites.research.google/open-buildings/)

---

### 3.5.2 Microsoft Building Footprints (VIDA Combined)

**Description :** Contours de bâtiments extraits par deep learning à partir d'imagerie aérienne Bing.

**Spécifications :**
- **Couverture :** Mondiale (par pays)
- **Nombre de bâtiments :** >1 milliard
- **Méthodologie :** ResNet-based segmentation
- **Format :** GeoJSON

**Accès via VIDA Combined :**
- **Collection :** Fusion Google Open Buildings + Microsoft Buildings
- **Source :** SAT-IO (Samapriya Roy)
- **Accès GEE :** `projects/sat-io/open-datasets/VIDA_COMBINED/[ISO_CODE]`

**Référence :**
- Microsoft (2023). GlobalMLBuildingFootprints. [https://github.com/microsoft/GlobalMLBuildingFootprints](https://github.com/microsoft/GlobalMLBuildingFootprints)
- Gonzales, J. J. (2023). Building-level comparison of Microsoft and Google open building footprints datasets. *GIScience 2023*.

---

### 3.5.3 GRIP4 (Global Roads Inventory Project)

**Description :** Inventaire global du réseau routier combinant données OpenStreetMap et sources nationales.

**Spécifications :**
- **Couverture :** Mondiale (par région)
- **Types de routes :** Autoroutes, routes nationales, routes régionales
- **Attributs :** Type, surface, nombre de voies
- **Régions disponibles :** 
  - North-America
  - Central-South-America
  - Europe
  - Africa
  - Middle-East-Central-Asia
  - South-East-Asia
  - Oceania

**Accès GEE :** `projects/sat-io/open-datasets/GRIP4/[REGION]`

**Référence :**
- Meijer, J. R., Huijbregts, M. A. J., Schotten, K. C. G. J., & Schipper, A. M. (2018). Global patterns of current and future road infrastructure. *Environmental Research Letters*, 13(6), 064006. [https://doi.org/10.1088/1748-9326/aabd42](https://doi.org/10.1088/1748-9326/aabd42)

---

### 3.5.4 OurAirports

**Description :** Base de données mondiale des aéroports et héliports.

**Spécifications :**
- **Couverture :** Mondiale
- **Types :** Large/Medium/Small airports, Heliports, Closed airports
- **Attributs :** Type, nom, code ICAO/IATA, coordonnées, élévation
- **Mise à jour :** Contributive (crowdsourced)

**Asset utilisé :** `projects/rapiddamagedetection/assets/ourairports`

**Source originale :** [https://ourairports.com/data/](https://ourairports.com/data/)

**Licence :** Public Domain (données accessibles via GitHub)

**Référence :**
- OurAirports (2024). Airport data. GitHub repository: [https://github.com/davidmegginson/ourairports-data](https://github.com/davidmegginson/ourairports-data)

---

### 3.5.5 Upply Seaports Database

**Description :** Base de données mondiale des ports maritimes commerciaux.

**Spécifications :**
- **Couverture :** Mondiale
- **Nombre de ports :** ~9000
- **Attributs :** Nom, pays, coordonnées, type de port
- **Mise à jour :** Régulière

**Asset utilisé :** `projects/rapiddamagedetection/assets/upply-seaports`

**Source originale :** [https://opendata.upply.com/seaports](https://opendata.upply.com/seaports)

**Licence :** Creative Commons Attribution 4.0 (CC BY 4.0)

**Conditions d'utilisation :** Attribution obligatoire : "Source: Upply (upply.com)"

**Référence :**
- Upply (2024). Sea Port Database (Open Data). [https://opendata.upply.com/seaports](https://opendata.upply.com/seaports)

---

### 3.5.6 Health Sites (Humanitaire OpenStreetMap)

**Description :** Localisation des établissements de santé extraits d'OpenStreetMap.

**Spécifications :**
- **Couverture :** Variable selon les contributions OSM
- **Types :** Hôpitaux, cliniques, centres de santé
- **Géométrie :** Points (nodes) et polygones (ways)

**Collections GEE :**
- `projects/sat-io/open-datasets/health-site-node` (points)
- `projects/sat-io/open-datasets/health-site-way` (polygones)

**Référence :**
- Humanitarian OpenStreetMap Team (2024). Health facilities. Accessible via SAT-IO.

---

### 3.5.7 Assets personnalisés - Exemple Jamaica Whitehouse

**Description :** Données locales extraites d'OpenStreetMap pour la zone de Whitehouse, Jamaïque (Cyclone Melissa, octobre 2025).

**Date d'extraction :** 4 mars 2026

**Méthode d'extraction :** Overpass API (OpenStreetMap)

**Assets disponibles :**
- `projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/AOI_whitehouse`
- `projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Building_OSM_whitehouse`
- `projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Road_OSM_whitehouse`

**Licence :** OpenStreetMap Database License (ODbL)

**Attribution :** © OpenStreetMap contributors

---

## 3.6 Données pédologiques

### 3.6.1 SoilGrids - Clay Content

**Description :** Cartes mondiales des propriétés du sol à 250m de résolution.

**Variable utilisée :** Teneur en argile (0-5 cm de profondeur)

**Spécifications :**
- **Résolution spatiale :** 250m
- **Profondeur :** 0-5 cm
- **Unité :** g/kg (grammes d'argile par kilogramme de sol)
- **Méthodologie :** Machine learning sur >150,000 profils de sol

**Collection GEE :** `projects/soilgrids-isric/clay_mean` (bande `clay_0-5cm_mean`)

**Référence :**
- Poggio, L., de Sousa, L. M., Batjes, N. H., et al. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. *SOIL*, 7, 217-240. [https://doi.org/10.5194/soil-7-217-2021](https://doi.org/10.5194/soil-7-217-2021)
- Site officiel: [https://www.isric.org/explore/soilgrids](https://www.isric.org/explore/soilgrids)

---

<a name="bibliographie"></a>
# 4. Bibliographie

## 4.1 Articles scientifiques - Méthodologie

### 4.1.1 Détection de dégâts (Damage Detection)

**Ballinger, O. (2024).** Open access battle damage detection via pixel-wise t-test on Sentinel-1 imagery. *arXiv preprint*. [https://doi.org/10.48550/arXiv.2405.06323](https://doi.org/10.48550/arXiv.2405.06323)

> Article fondateur de la méthode PWTT (Pixel-Wise T-Test) utilisée pour la détection des dégâts. Décrit le test statistique appliqué pixel par pixel sur les séries temporelles Sentinel-1 pour identifier les changements significatifs de rétrodiffusion radar.

---

### 4.1.2 Détection d'inondations (Flood Detection)

**DeVries, B., Huang, C., Armston, J., Huang, W., Jones, J. W., & Lang, M. W. (2020).** Rapid and robust monitoring of flood events using Sentinel-1 and Landsat data on the Google Earth Engine. *Remote Sensing of Environment*, 240, 111664. [https://doi.org/10.1016/j.rse.2020.111664](https://doi.org/10.1016/j.rse.2020.111664)

> Article de référence pour l'algorithme s1flood. Décrit la méthode de détection d'inondations par z-score appliquée aux données Sentinel-1, avec masquage de l'eau permanente et validation multi-temporelle.

---

### 4.1.3 Détection de glissements de terrain (Landslide Detection)

**Handwerger, A. L., Huang, M.-H., Jones, S. Y., Amatya, P., Kerner, H. R., & Kirschbaum, D. B. (2022).** Generating landslide density heatmaps for rapid detection using open-access satellite radar data in Google Earth Engine. *Natural Hazards and Earth System Sciences*, 22(3), 753-774. [https://doi.org/10.5194/nhess-22-753-2022](https://doi.org/10.5194/nhess-22-753-2022)

> Méthode de création de heatmaps de densité de glissements de terrain basée sur des données Sentinel-1. Approche par détection de changements SAR combinée à une analyse de cohérence temporelle.

**Kanani-Sadat, Y., Pradhan, B., Pirasteh, S., & Mansor, S. (2015).** Landslide susceptibility mapping using GIS-based statistical models and remote sensing data in tropical environment. *Scientific Reports*, 5, 9899. [https://doi.org/10.1038/srep09899](https://doi.org/10.1038/srep09899)

> Modèle de susceptibilité aux glissements de terrain par analyse multicritère. Source des poids utilisés pour les facteurs de susceptibilité (précipitations, pente, sol, aspect, courbure) via la méthode AHP (Analytical Hierarchy Process).

---

### 4.1.4 Comparaison de bases de données bâti

**Gonzales, J. J. (2023).** Building-level comparison of Microsoft and Google open building footprints datasets. In *GIScience 2023: 12th International Conference on Geographic Information Science* (LIPIcs, Vol. 277, Article 35). Schloss Dagstuhl – Leibniz-Zentrum für Informatik. [https://doi.org/10.4230/LIPIcs.GIScience.2023.35](https://doi.org/10.4230/LIPIcs.GIScience.2023.35)

> Analyse comparative des bases de données Microsoft et Google Open Buildings. Méthodologie d'appariement géométrique et évaluation de la qualité par indicateurs d'exhaustivité, précision positionnelle et sur-complétude. Inspiration pour le script Python de comparaison.

---

## 4.2 Références de code et implémentations

### 4.2.1 PWTT - Détection de dégâts

**Ballinger, O. (2024).** PWTT: Pixel-Wise T-Test for battle damage detection [Source code]. GitHub repository. [https://github.com/oballinger/PWTT](https://github.com/oballinger/PWTT)

> Implémentation de référence du test t pixel-wise en Python et JavaScript (Google Earth Engine). Code source adapté pour le module Damage Detection de cet outil.

---

### 4.2.2 s1flood - Cartographie d'inondations

**DeVries, B. (2019).** s1flood: Rapid flood mapping with Sentinel-1 on Google Earth Engine [Source code]. GitHub repository. [https://github.com/bendv/s1flood](https://github.com/bendv/s1flood)

> Script JavaScript Google Earth Engine pour la détection rapide d'inondations. Algorithme de z-score et masquage d'eau permanente adaptés pour le module Flood Detection.

---

### 4.2.3 Landslide heatmaps - Google Earth Engine

**Huang, M.-H., & Handwerger, A. L. (2021).** Codes-for-Handwerger-et-al-2021-preprint: Generating landslide density heatmaps for rapid detection using open-access satellite radar data in Google Earth Engine [Source code]. GitHub repository. [https://github.com/MongHanHuang/Codes-for-Handwerger-et-al-2021-preprint](https://github.com/MongHanHuang/Codes-for-Handwerger-et-al-2021-preprint)

> Scripts Google Earth Engine pour la génération de heatmaps de glissements de terrain. Inspiration pour l'approche de détection SAR et agrégation spatiale.

---

### 4.2.4 Comparaison de bâtis - Script Python/QGIS

**Gonzales, J. J. (2023).** Building-Level Comparison of Microsoft and Google Open Buildings [Supplemental code]. Oak Ridge National Laboratory.

> Code source et méthodologie pour la comparaison géométrique de bases de données bâti. Inspiration pour les critères d'appariement (distance, recouvrement) et le calcul des indicateurs de qualité dans le script Python QGIS.

---

## 4.3 Méthodes statistiques et traitement du signal

**Lee, J.-S. (1980).** Digital image enhancement and noise filtering by use of local statistics. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, PAMI-2(2), 165-168. [https://doi.org/10.1109/TPAMI.1980.4766994](https://doi.org/10.1109/TPAMI.1980.4766994)

> Filtre de Lee adaptatif pour la réduction du speckle dans les images SAR. Base théorique pour le prétraitement des données Sentinel-1.

**Student (1908).** The probable error of a mean. *Biometrika*, 6(1), 1-25. [https://doi.org/10.1093/biomet/6.1.1](https://doi.org/10.1093/biomet/6.1.1)

> Article fondateur du test t de Student. Base théorique pour le test statistique pixel-wise utilisé dans la détection de dégâts.

---

## 4.4 Ouvrages de référence

**Ulaby, F. T., & Long, D. G. (2014).** *Microwave Radar and Radiometric Remote Sensing*. University of Michigan Press. ISBN: 978-0-472-11935-6.

> Ouvrage de référence sur la télédétection radar. Théorie de la rétrodiffusion, effets de la rugosité et de l'humidité, interprétation des signatures SAR.

**Richards, J. A. (2009).** *Remote Sensing with Imaging Radar*. Springer. ISBN: 978-3-642-02020-9.

> Principes de l'imagerie radar, géométrie d'acquisition, traitement du speckle, applications aux catastrophes naturelles.

---

## 4.5 Documentation technique et guides utilisateur

**ESA (2022).** Sentinel-1 SAR User Guide. European Space Agency. [https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-1-sar](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-1-sar)

> Guide utilisateur officiel de Sentinel-1. Spécifications techniques, modes d'acquisition, niveaux de traitement, accès aux données.

**Google Earth Engine Team (2024).** Google Earth Engine Documentation. [https://developers.google.com/earth-engine](https://developers.google.com/earth-engine)

> Documentation officielle de Google Earth Engine. API JavaScript, collections de données, tutoriels, exemples de code.

**QGIS Development Team (2024).** QGIS User Guide. QGIS Project. [https://docs.qgis.org/](https://docs.qgis.org/)

> Documentation officielle de QGIS. Traitement de données vectorielles, modélisation graphique, Python API.

---

<a name="licence"></a>
# 5. Licence et Contributions

## 5.1 Licence du projet

Ce projet est distribué sous **licence MIT**.
```
MIT License

Copyright (c) 2026 Fabrice Renoux

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 5.2 Licences des données tierces

L'utilisation de cet outil implique l'accès à des données tierces soumises à leurs propres licences :

| Donnée | Licence | Attribution requise |
|--------|---------|---------------------|
| Sentinel-1 | Copernicus Open Access Hub (gratuit) | "Contains modified Copernicus Sentinel data [Year]" |
| CHIRPS | Creative Commons (CC) | "CHIRPS data provided by UCSB Climate Hazards Center" |
| GLDAS | NASA Open Data (gratuit) | "Data: NASA GLDAS" |
| NASADEM, SRTM, ASTER | NASA/USGS Open Data | "Data: NASA/USGS" |
| ESA WorldCover | ESA Open Data | "Contains ESA WorldCover data [Year]" |
| JRC Global Surface Water | European Commission Open Data | "Data: EC JRC" |
| WorldPop | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: WorldPop (www.worldpop.org)" |
| Google Open Buildings | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: Google Open Buildings" |
| Microsoft Buildings | Open Data Commons Open Database License (ODbL) | "Data: Microsoft" |
| GRIP4 | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: GRIP4 (Meijer et al., 2018)" |
| OurAirports | Public Domain | Aucune (optionnel: "Data: OurAirports") |
| Upply Seaports | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: Upply (upply.com)" - OBLIGATOIRE |
| OpenStreetMap | Open Database License (ODbL) | "© OpenStreetMap contributors" - OBLIGATOIRE |
| SoilGrids | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: ISRIC SoilGrids" |

**Mentions d'attribution recommandées dans les publications :**
```
Ce travail utilise des données Sentinel-1 (ESA Copernicus), CHIRPS (UCSB CHG),
GLDAS (NASA), Google Open Buildings, Microsoft Building Footprints, GRIP4,
Upply Seaports Database, OpenStreetMap contributors, et SoilGrids (ISRIC).
```

---

## 5.3 Citation de cet outil

Si vous utilisez cet outil dans vos travaux de recherche, veuillez le citer comme suit :

**Format APA :**
```
Renoux, F. (2026). Rapid Damage Detection Tool: Post-disaster assessment using 
Sentinel-1 SAR data on Google Earth Engine [Software]. 
GitHub repository: https://github.com/[username]/rapid-damage-detection
```

**Format BibTeX :**
```bibtex
@software{renoux2026rapid,
  author = {Renoux, Fabrice},
  title = {Rapid Damage Detection Tool: Post-disaster assessment using Sentinel-1 SAR data on Google Earth Engine},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/[username]/rapid-damage-detection},
  note = {Master's thesis project, AgroParisTech SILAT}
}
```

---

## 5.4 Contributions et développement collaboratif

### 5.4.1 Comment contribuer

Les contributions sont les bienvenues ! Voici comment participer :

**Types de contributions acceptées :**
- Corrections de bugs
- Améliorations algorithmiques
- Ajout de nouvelles fonctionnalités
- Amélioration de la documentation
- Traductions
- Création d'exemples d'utilisation

**Processus de contribution :**

1. **Fork** le dépôt
2. Créer une **branche** pour votre fonctionnalité :
```bash
   git checkout -b feature/AmazingFeature
```
3. **Commit** vos modifications :
```bash
   git commit -m 'Add some AmazingFeature'
```
4. **Push** vers la branche :
```bash
   git push origin feature/AmazingFeature
```
5. Ouvrir une **Pull Request**

**Règles de contribution :**
- Respecter le style de code existant
- Documenter les nouvelles fonctionnalités
- Inclure des tests si applicable
- Mettre à jour le README si nécessaire

### 5.4.2 Signalement de bugs

Pour signaler un bug, ouvrir une **Issue** sur GitHub avec :
- **Description claire** du problème
- **Étapes pour reproduire** le bug
- **Comportement attendu** vs observé
- **Captures d'écran** si pertinent
- **Configuration** (navigateur, système d'exploitation)

### 5.4.3 Demande de fonctionnalités

Pour proposer une nouvelle fonctionnalité, ouvrir une **Issue** avec le label `enhancement` et décrire :
- Le **besoin** ou problème à résoudre
- La **solution proposée**
- Les **alternatives envisagées**
- Le **contexte d'utilisation**

---

## 5.5 Contact et support

**Auteur :** Fabrice Renoux  
**Institution :** AgroParisTech - Mastère Spécialisé SILAT  
**Email :** [votre_email@example.com]  
**LinkedIn :** [Profil LinkedIn]

**Pour toute question :**
- Ouvrir une **Issue** sur GitHub (recommandé)
- Contacter par email pour des questions confidentielles

**Délai de réponse :** 3-5 jours ouvrés (projet académique, support non garanti)

---

## 5.6 Remerciements

Ce projet a été réalisé dans le cadre du **Mastère Spécialisé SILAT** (Systèmes d'Informations Localisées pour l'Aménagement des Territoires) d'**AgroParisTech**.

**Remerciements particuliers à :**
- **Owen Ballinger** pour le développement de la méthode PWTT et le partage du code source
- **Ben DeVries** pour l'algorithme s1flood et la documentation associée
- **Alexander Handwerger** et **Mong-Han Huang** pour les méthodes de détection de glissements de terrain
- **Google Earth Engine Team** pour la plateforme de traitement et l'accès aux données
- **ESA Copernicus** pour les données Sentinel-1
- L'ensemble des **contributeurs aux bases de données ouvertes** (OpenStreetMap, Google, Microsoft, etc.)
- L'**équipe pédagogique du Mastère SILAT** pour l'encadrement du projet

---

# 6. Structure du Dépôt GitHub
```
rapid-damage-detection/
│
├── README.md                          # Ce fichier (documentation complète)
│
├── LICENSE                            # Licence MIT
│
├── app/
│   └── rapid_damage_detection.js      # Code source JavaScript (Google Earth Engine)
│
├── tools/
│   ├── building_quality_comparison.py # Script QGIS de comparaison bâti
│   └── Population_building.model3     # Modèle QGIS d'estimation de population
│
├── docs/
│   ├── user_guide.md                  # Guide utilisateur détaillé (extraction du README)
│   ├── methodology.md                 # Méthodologie scientifique (extraction du README)
│   ├── data_sources.md                # Sources de données (extraction du README)
│   └── screenshots/                   # Captures d'écran de l'application
│       ├── main_interface.png
│       ├── results_panel.png
│       ├── damage_map.png
│       ├── flood_map.png
│       └── landslide_map.png
│
├── examples/
│   ├── jamaica_whitehouse_2025/
│   │   ├── config.json                # Configuration de l'exemple
│   │   └── README.md                  # Documentation de l'exemple
│   └── [autres_exemples]/
│
├── tests/
│   ├── test_damage_detection.js       # Tests unitaires (module Damage)
│   ├── test_flood_detection.js        # Tests unitaires (module Flood)
│   └── test_landslide_detection.js    # Tests unitaires (module Landslide)
│
├── assets/
│   └── logo.png                       # Logo du projet
│
├── CHANGELOG.md                       # Historique des versions
│
└── CONTRIBUTING.md                    # Guide de contribution
```

---

# 7. Installation et Déploiement

## 7.1 Pour les utilisateurs

**Aucune installation nécessaire** - L'application fonctionne entièrement en ligne.

**Accès direct :**
[https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app)

**Prérequis :**
- Compte Google (gratuit)
- Navigateur web moderne

---

## 7.2 Pour les développeurs

### 7.2.1 Cloner le dépôt
```bash
git clone https://github.com/[username]/rapid-damage-detection.git
cd rapid-damage-detection
```

### 7.2.2 Configuration Google Earth Engine

1. Créer un compte GEE : [https://earthengine.google.com/signup/](https://earthengine.google.com/signup/)
2. Installer l'API Python (optionnel) :
```bash
   pip install earthengine-api
```
3. S'authentifier :
```bash
   earthengine authenticate
```

### 7.2.3 Déploiement de l'application

**Via l'interface web GEE :**
1. Ouvrir Google Earth Engine Code Editor : [https://code.earthengine.google.com/](https://code.earthengine.google.com/)
2. Copier le contenu de `app/rapid_damage_detection.js`
3. Coller dans l'éditeur
4. Cliquer sur **Run** pour tester
5. Cliquer sur **Apps** > **New App** pour déployer

**Via l'API Python :**
```python
import ee
ee.Initialize()

# Charger le script
with open('app/rapid_damage_detection.js', 'r') as f:
    script = f.read()

# Déployer (nécessite permissions appropriées)
```

---

# 8. Feuille de Route (Roadmap)

## Version 1.0 (actuelle)
- ✅ Module Damage Detection (PWTT)
- ✅ Module Flood Detection (s1flood)
- ✅ Module Landslide Detection (heatmaps + susceptibilité)
- ✅ Module Weather Statistics
- ✅ Export client-side (GeoJSON)
- ✅ Export Google Drive (Shapefile + GeoTIFF)
- ✅ Time Series (flood uniquement)
- ✅ Script QGIS de comparaison bâti
- ✅ Modèle QGIS d'estimation de population

## Version 1.1 (planifiée - T2 2026)
- ⬜ Fusion optique (Sentinel-2) pour validation
- ⬜ Détection de dégâts progressifs (suivi multi-temporel)
- ⬜ Export PDF automatisé (cartes + statistiques)
- ⬜ Interface multilingue (EN, FR, ES)
- ⬜ Amélioration de l'interface utilisateur

## Version 2.0 (planifiée - T4 2026)
- ⬜ Intégration de modèles de machine learning
- ⬜ Support de données SAR haute résolution (ICEYE, Capella)
- ⬜ Application mobile (collecte terrain)
- ⬜ API REST pour intégration dans d'autres systèmes
- ⬜ Dashboard temps réel (monitoring continu)

---

# 9. FAQ (Foire Aux Questions)

**Q1 : L'outil peut-il être utilisé pour des interventions opérationnelles ?**

Non. Cet outil est **expérimental** et destiné à la recherche. Les résultats doivent être validés par des experts avant toute utilisation opérationnelle.

---

**Q2 : Pourquoi mes résultats diffèrent-ils entre deux analyses de la même zone ?**

Plusieurs facteurs peuvent expliquer cette variabilité :
- Nouvelles images Sentinel-1 disponibles (acquisitions récentes)
- Modification des paramètres (seuils, intervalles)
- Données auxiliaires mises à jour (WorldPop, WorldCover)
- Variabilité des conditions d'acquisition SAR (humidité du sol, vent)

---

**Q3 : Puis-je utiliser l'outil pour d'autres types de catastrophes (feux de forêt, sécheresses) ?**

Le module **Damage Detection** peut détecter des changements SAR pour les feux de forêt (débris, cendres). Pour les sécheresses, Sentinel-1 seul est insuffisant (privilégier des indices optiques comme NDVI).

---

**Q4 : Combien de temps faut-il attendre après un événement pour lancer l'analyse ?**

**Idéalement : 3-7 jours** après l'événement pour :
- Garantir au moins une acquisition Sentinel-1 post-événement
- Permettre la stabilisation des conditions au sol (évacuation de l'eau, débris)

---

**Q5 : L'outil fonctionne-t-il en zones polaires ou désertiques ?**

**Zones polaires** : Données Sentinel-1 disponibles, mais les DEM (NASADEM, SRTM) sont limités à 60°N-56°S.  
**Zones désertiques** : Oui, mais les changements de sable (dunes) peuvent générer des faux positifs.

---

**Q6 : Puis-je exporter les résultats dans un autre format que GeoJSON/Shapefile ?**

Actuellement : GeoJSON (client-side) et Shapefile (Google Drive).  
**Alternatives :** Convertir les fichiers dans QGIS (Layer > Export > Save As...) vers KML, GeoPackage, CSV, etc.

---

**Q7 : Les données sont-elles stockées quelque part ? Y a-t-il des enjeux de confidentialité ?**

**Non**. L'application ne stocke aucune donnée utilisateur. Toutes les analyses sont effectuées côté serveur (Google Earth Engine) et les résultats sont uniquement accessibles par l'utilisateur connecté. Les exports Google Drive sont stockés dans le Drive personnel de l'utilisateur.

---

**Q8 : L'outil peut-il analyser des zones très étendues (pays entier) ?**

**Non**. Google Earth Engine impose des limites de calcul. Pour des zones > 100 km², le temps de calcul peut dépasser 30 minutes et l'analyse peut échouer. **Solution** : Diviser la zone en plusieurs sous-zones.

---

**Q9 : Comment signaler un bug ou proposer une amélioration ?**

Ouvrir une **Issue** sur GitHub : [https://github.com/[username]/rapid-damage-detection/issues](https://github.com/[username]/rapid-damage-detection/issues)

---

**Q10 : Puis-je utiliser mes propres données bâti/routes au lieu des bases globales ?**

**Oui**. Utiliser l'option "Custom asset" et uploader vos données sur Google Earth Engine. Format requis : FeatureCollection (polygones pour bâti, lignes pour routes).

---

# 10. Glossaire

| Terme | Définition |
|-------|-----------|
| **AOI** | Area of Interest - Zone d'étude définie par l'utilisateur |
| **CHIRPS** | Climate Hazards Group InfraRed Precipitation with Station data - Données de précipitations |
| **DEM** | Digital Elevation Model - Modèle numérique de terrain |
| **GEE** | Google Earth Engine - Plateforme de traitement géospatial |
| **GLDAS** | Global Land Data Assimilation System - Données météorologiques globales |
| **GRD** | Ground Range Detected - Produit Sentinel-1 Level-1 |
| **IW** | Interferometric Wide swath - Mode d'acquisition Sentinel-1 |
| **JRC** | Joint Research Centre - Centre de recherche de la Commission Européenne |
| **MAD** | Median Absolute Deviation - Mesure robuste de dispersion statistique |
| **NASADEM** | DEM global retraité par la NASA à partir de SRTM |
| **PWTT** | Pixel-Wise T-Test - Test t appliqué pixel par pixel |
| **SAR** | Synthetic Aperture Radar - Radar à synthèse d'ouverture |
| **SRTM** | Shuttle Radar Topography Mission - Mission radar topographique |
| **VH/VV** | Polarisations radar (Vertical-Horizontal / Vertical-Vertical) |
| **WorldCover** | Carte ESA de couverture du sol à 10m |
| **WorldPop** | Données de population désagrégées |
| **z-score** | Écart normalisé - (valeur - moyenne) / écart-type |

---

**FIN DU README**

Pour toute question : [votre_email@example.com]  
Application en ligne : [https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app)  
Dépôt GitHub : [https://github.com/[username]/rapid-damage-detection](https://github.com/[username]/rapid-damage-detection)

---

© 2026 Fabrice Renoux - AgroParisTech SILAT - Licence MIT
