# Rapid-Cyclone-Damage-Mapping
This GitHub repo hosts a rapid damage detection tool developed from academic work using Sentinel-1 radar. It provides first-pass maps of potential damage post-cyclone, primarily to support detailed photo-interpretation, guide field and drone missions, and must be validated with high-resolution imagery.
# Rapid Damage Detection Tool

**Language / Langue :** 🇬🇧 English | [🇫🇷 Français](README.md)

---

**Author:** Fabrice Renoux  
**Institution:** AgroParisTech - SILAT Master's Program (Systèmes d'Informations Localisées pour l'Aménagement des Territoires)  
**Date:** March 2026  

---

## Disclaimer

This project is an **academic experimental work** developed within a university framework. It should **not be considered as a certified operational tool** for emergency response.

**Important limitations:**
- Results are provided for indicative purposes only and require systematic validation by experts
- The tool does not replace photo-interpretation on high-resolution imagery
- Should not be used as the sole basis for critical operational decisions
- Must not serve as the only source for life-saving interventions without field verification
- Intended for research and academic experimentation
- The author disclaims all responsibility regarding the use of results

**Recommended use:** Decision support tool to guide and prioritize detailed analyses conducted by qualified professionals.

---

## Context and Objectives

### Problem Statement

In the hours following a natural disaster (tropical cyclone, earthquake), rapid damage assessment faces several constraints:

1. **Acquisition delay:** High-resolution satellite optical imagery may require several days before becoming available
2. **Weather conditions:** Post-event cloud cover limits optical imagery exploitation
3. **Data volume:** Manual processing via photo-interpretation is time-consuming and requires specialized expertise
4. **Prioritization:** Difficulty in rapidly identifying areas requiring urgent intervention

### Proposed Solution

This tool exploits **Sentinel-1 radar data** (C-band, all-weather acquisition) to:

1. Generate an initial indicative mapping of potentially affected areas
2. Prioritize sectors requiring detailed photo-interpretation
3. Target ground reconnaissance and drone missions
4. Accelerate the rapid assessment process for emergency teams

**Main applications:**
- **Post-tropical cyclone:** structural damage, flooding, landslides
- **Post-earthquake:** structural change detection on buildings (damage detection module)

**Principle:** The tool does not produce a definitive assessment, but rather a **framework of potential damage** that must be systematically validated through visual analysis of high-resolution imagery and ground verification.

---

## Application Access

**Google Earth Engine Application URL:**  
[https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app)

**Prerequisites:**
- Modern web browser (Chrome, Firefox, Edge)
- Google account (free)
- Stable internet connection

**No installation required** - The application runs entirely online via Google Earth Engine Apps.

---

## Table of Contents

1. [User Guide](#user-guide)
   - [Step 0: Building data quality assessment (optional)](#step-0)
   - [Step 1: Using the GEE application](#step-1)
   - [Step 2: Affected population estimation (post-processing)](#step-2)
2. [Scientific Methodology](#scientific-methodology)
3. [Data Sources](#data-sources)
4. [Bibliography](#bibliography)
5. [License and Contributions](#license)

---

<a name="user-guide"></a>
# 1. User Guide

<a name="step-0"></a>
## Step 0: Building Data Quality Assessment (Optional)

### Context

Google Earth Engine offers several global building databases with variable quality depending on regions:
- Google Open Buildings v3
- Microsoft Building Footprints (via VIDA Combined)
- Custom assets

A Python QGIS script allows comparing these sources with a local reference layer to identify the most suitable one.

### Prerequisites

**Software:**
- QGIS 3.x (stable version recommended)

**Required data:**
- **Reference layer:** High-quality building data (cadastre, field survey, validated OpenStreetMap)
  - Format: Shapefile (.shp) or GeoPackage (.gpkg)
  - Geometry: Polygons
- **Layers to evaluate** (1 to 5 maximum): Extracts from databases to compare
  - Formats: Shapefile (.shp) or GeoPackage (.gpkg)
  - Geometry: Polygons

### Installation

1. Download the script `building_quality_comparison.py` from the repository:
```
tools/building_quality_comparison.py
```

2. Open QGIS
3. Menu: **Plugins** > **Python Console**
4. Click the **Open script** icon
5. Select `building_quality_comparison.py`

### Execution

1. Click **Run script** (play icon)
2. Follow the interactive dialogs:

**Dialog 1: Reference layer**
- Select the reference vector file

**Dialog 2: Layers to evaluate**
- Select 1 to 5 vector files (Ctrl+click for multi-selection)

**Dialog 3: Output folder**
- Define the results save directory

**Dialog 4: Matching parameters**

| Parameter | Description | Recommended value |
|-----------|-------------|-------------------|
| Max distance (m) | Maximum distance between centroids to consider a match | 10 m (dense urban) to 50 m (rural) |
| Minimum overlap (%) | Surface overlap threshold | 50% |
| Multiple matches | 0 = strict 1:1 mode, 1 = 1:n mode | 0 |

### Results Interpretation

The script generates:

1. **Summary text file:** `comparison_summary_YYYYMMDD_HHMM.txt`
2. **QGIS layers** (added to project):

| Layer | Symbology | Description |
|--------|-----------|-------------|
| REF_buildings | Orange outline | Reference buildings |
| REF_NON_DETECTES_[name] | Purple outline | Undetected reference buildings |
| BATI_ETUDE_APPARIES_[name] | Green outline | Correctly matched buildings |
| BATI_ETUDE_NON_APPARIES_[name] | Red outline | Excess buildings (over-completeness) |
| LIAISONS_[name] | Blue dashed lines with arrows | Centroid connections |

#### Key Indicators

The text file contains for each evaluated layer:

**Aggregate statistics**
- Number of buildings (study vs reference)
- Number of matched buildings
- Number of undetected buildings
- Number of excess buildings

**Quality indicators**

| Indicator | Formula | Interpretation | Excellent | Acceptable | Poor |
|-----------|---------|----------------|-----------|------------|------|
| Completeness | (Detected REF buildings) / (Total REF buildings) | Ability to detect all existing buildings | > 90% | 70-90% | < 70% |
| Over-completeness | (Unmatched STUDY buildings) / (Total STUDY buildings) | Proportion of erroneous detections | < 5% | 5-15% | > 15% |
| Overlap index | (Total intersection area) / (Matched REF area) | Surface quality of overlap | > 90% | 80-90% | < 80% |

**Positional analysis**
- Mean and median distance between centroids
- MAD (Median Absolute Deviation): robust dispersion indicator

**Morphological analysis**
- Median area difference (m²)
- MAD of area difference
- Percentage of significant differences (MAD test with 1.96 σ threshold)

#### Comparative Summary

If multiple layers are evaluated, the file contains:

**Summary table**
```
Layer                          Complete.  Over-compl.  Overlap   Dist.med.
---------------------------------------------------------------------------
google_buildings.shp             88.3%       7.2%      91.5%      2.87m
microsoft_buildings.shp          82.1%       4.1%      89.3%      2.12m
osm_buildings.shp                76.5%      12.8%      85.7%      4.56m
```

**Global ranking**

Composite score calculated by weighted average:
- Completeness: 30%
- Inverted over-completeness: 25%
- Overlap: 25%
- Inverted positional accuracy: 20%

**Recommendation**

The script identifies the optimal layer and lists:
- Strengths
- Attention points (criteria below thresholds)

### Decision for GEE Application

Use the layer with the best global score:
- If Google Open Buildings is optimal: select this option in the application
- If Microsoft Buildings is optimal: select "Google-Microsoft (VIDA Combined)"
- If no public layer is satisfactory (score < 70): consider using a custom asset

---

<a name="step-1"></a>
## Step 1: Using the Google Earth Engine Application

### User Interface

The application consists of three main panels:

1. **Control panel** (left): Analysis parameter configuration
2. **Map panel** (center): Spatial visualization and AOI drawing
3. **Results panel** (right): Statistics display and download links

### Parameter Configuration

#### Quick Start

Dropdown menu offering pre-recorded configurations:
- **New (blank):** Empty configuration
- **Demo: Jamaica Whitehouse (Oct 2025):** Functional example on Hurricane Melissa

To test the application, select the demo and click directly on "Run Analysis".

#### 1. Zone Name

Study area identifier used for export file naming.

**Recommended format:** `Country_Event_Year`

**Examples:**
- `Haiti_Matthew_2016`
- `Mozambique_Idai_2019`
- `Philippines_Haiyan_2013`

#### 2. Dates (YYYY-MM-DD format)

**Pre-date (reference date)**
- Date prior to the event, representing normal state
- Choose a period without major events
- Recommendation: 1 to 3 months before the event

**Event date**
- Disaster date
- Can be the impact date or the following day

**Constraint:** Pre-date < Event date

#### 3. Intervals (days)

**Pre (before interval)**
- Time window to search for Sentinel-1 images before the reference date
- Range: 30 to 365 days
- **Recommendation: 180 days**
- The longer the interval, the higher the probability of finding images

**Post (after interval)**
- Time window to search for Sentinel-1 images after the event date
- Range: 1 to 28 days
- **Recommendation: 6 days** (corresponds to Sentinel-1 revisit period)
- If no image is found, the application suggests increasing this interval

**Technical note:** Sentinel-1 has an average revisit period of ~6 days. A post-event interval too short (< 6 days) may not capture any acquisition.

#### 4. Options (analysis modules)

**Weather data**
- Cumulative precipitation (CHIRPS Daily)
- Mean and maximum wind (GLDAS)
- Mean and minimum atmospheric pressure (GLDAS)
- Temporal evolution graphs
- **Recommendation:** Always activate to contextualize the event

**Damage detection**
- Building and road change detection
- Based on pixel-wise t-test (PWTT) applied to Sentinel-1 data
- **Applications:** Cyclones, earthquakes, conflicts
- Generates damage classes (Moderate, High, Very High)

**Flood detection**
- Flooded area mapping
- Based on s1flood algorithm (DeVries et al., 2020)
- **Applications:** Cyclones, floods, extreme rainfall events
- Identifies flooded buildings and roads

**Landslide detection**
- Landslide susceptibility mapping
- Combination of t-test and environmental factors (slope, curvature, precipitation, soil type)
- **Applications:** Earthquakes, heavy rainfall in mountainous areas
- Generates exposure zones (runout zones)

**Time series (flood only)**
- Temporal evolution analysis of flooding
- Requires "Flood detection" activation
- Generates a progression/recession graph
- Allows specifying a custom analysis period

**Recommendation:** For initial testing, activate Weather + one module (Damage OR Flood) to reduce calculation time.

#### 5. AOI (Area of Interest)

Three methods for defining the study area:

**Method 1: Draw on map**
- Use integrated drawing tools (rectangle or polygon)
- Draw directly on the map
- **Limitation:** Maximum recommended area ~50 km² (for calculation times < 15 min)

**Method 2: Enter WKT/GeoJSON**
- Paste WKT or GeoJSON text
- Useful if the area was defined in external GIS (QGIS)
- **QGIS procedure:**
  1. Install the "Get WKT" plugin
  2. Select the polygon
  3. Right-click > Get WKT
  4. Copy-paste into application field

**Method 3: Custom asset**
- Use a pre-uploaded Google Earth Engine asset
- Format: `projects/YOUR_PROJECT/assets/YOUR_AOI`
- Asset must be a FeatureCollection

**Recommendation:** Areas of 10-50 km² for balance between spatial resolution and calculation time.

#### 6. Buildings (building data source)

Three available options:

| Option | Description | Coverage | Typical resolution |
|--------|-------------|----------|-------------------|
| Google Open Buildings v3 | Google database | Global (except Europe/USA) | Building level |
| Google-Microsoft (VIDA Combined) | Fusion of both databases | Global | Building level |
| Custom asset | Personal asset uploaded to GEE | Specific area | Variable |

**Recommended selection:**
- If Step 0 was performed: use the layer with the best score
- Otherwise: favor "Google-Microsoft (VIDA Combined)" for most regions

**Format for Custom asset:**
- Type: FeatureCollection
- Geometry: Polygons
- Path: `projects/YOUR_PROJECT/assets/YOUR_BUILDINGS`

#### 7. Roads (road data source)

Two options:

| Option | Description | Coverage |
|--------|-------------|----------|
| GRIP4 (auto) | Global Roads Inventory Project | Global (automatic region detection) |
| Custom asset | Custom road network | Specific area |

**GRIP4** automatically selects the appropriate region (North America, Europe, Africa, etc.) based on AOI location.

**Format for Custom asset:**
- Type: FeatureCollection
- Geometry: LineString
- Path: `projects/YOUR_PROJECT/assets/YOUR_ROADS`

#### 8. DEM Source (Digital Elevation Model)

Activated only if "Flood detection" or "Landslide detection" is checked.

| Option | Resolution | Coverage | Recommended use |
|--------|-----------|----------|-----------------|
| NASADEM | 30m | Global (60°N-56°S) | Default (recommended) |
| SRTM | 30m | Global (60°N-56°S) | Alternative |
| ALOS | 30m | Global | Tropical areas |
| ASTER | 30m | Global | Less accurate |
| Custom | Variable | Specific | Local higher-quality data |

**Recommendation:** Keep NASADEM by default unless you have a local DEM of better quality.

#### 9. Settings (advanced parameters)

**T-threshold (damage detection threshold)**
- Range: 2.0 to 5.0
- Default: 2.4
- Principle: t-statistic threshold below which a change is considered non-significant
- Increase = fewer false positives, risk of missing slight damage
- Decrease = more sensitive detection, increased false positive risk

**Slope (minimum slope for landslides)**
- Range: 5° to 30°
- Default: 10°
- Slope threshold below which landslide risk is considered negligible

**Curvature (minimum curvature)**
- Range: 0.01 to 0.2
- Default: 0.05
- Terrain curvature (concavity/convexity) used to identify potential instability zones

**Recommendation:** Keep default values for initial analysis. Adjust based on results and terrain knowledge.

#### 10. Time Series

Visible only if "Flood detection" is activated.

**From / To:** Define analysis period
- Application searches all available Sentinel-1 images in this interval
- Generates a graph showing flooded area evolution
- Allows identifying flood peak and recession dynamics

**Note:** Calculation time increases proportionally with the number of analyzed dates.

### Launching Analysis

1. Verify all mandatory parameters are configured
2. Click **Run Analysis** button

**Progress bar:**
```
████████████░░░░░░░░ 60% - Detecting flood extent...
```

**Estimated duration:**
- Small area (< 10 km²): 1-3 minutes
- Medium area (10-30 km²): 3-8 minutes
- Large area (30-50 km²): 8-15 minutes

**Important:** Do not close browser window during calculation!

### Results Interpretation

#### Results Panel (right)

Once analysis is complete, the right panel displays:

**General information**
- AOI area (km²)
- Population (WorldPop)
- Infrastructure (ports, airports, health facilities)

**Weather conditions**
- Cumulative precipitation graphs
- Wind and atmospheric pressure graphs
- Summary statistics:
  - Cumulative rainfall (mm)
  - Max daily rainfall (mm)
  - Max wind gust (km/h)
  - Min pressure (hPa)

**Damage statistics (if activated)**

*Buildings*
- Number of damaged vs intact buildings
- Percentage of damaged buildings
- Distribution by severity level:
  - Very High (T ≥ T_threshold + 2)
  - High (T_threshold + 1 ≤ T < T_threshold + 2)
  - Moderate (T_threshold ≤ T < T_threshold + 1)

*Roads*
- Number of damaged vs intact road segments
- Estimated length of damaged roads (km)

**Flood statistics (if activated)**
- Flooded area (km²)
- Distribution by land cover type (WorldCover)
- Number of buildings in flooded area
- Length of flooded roads (km)

**Landslide statistics (if activated)**
- Total area in susceptibility zone (km²)
- Distribution by probability level (Moderate, High, Very High)
- Exposure zone area (runout zones)
- Number of buildings at risk
- Length of roads at risk (km)

#### Map Layers

The following layers are added to the "Layers" panel:

**AOI**
- Orange outline of study area

**Damage (if activated)**
- T-statistic raster: Change raster (continuous values)
- Buildings intact: Green outline
- Buildings Very High: Dark red outline
- Buildings High: Orange outline
- Buildings Moderate: Yellow outline
- Roads intact: Green line
- Roads damaged: Red line
- Density bubbles: Circles proportional to damage density
- Logistic hub: Suggested access point (calculated by weighted barycenter of damages and distance to infrastructure)

**Flood (if activated)**
- Extent: Flood extent (blue gradient according to classification)
- Permanent water: Permanent water (light blue)
- Flooded buildings: Buildings in flooded area (dark blue outline)
- Flooded roads: Roads in flooded area (thick blue line)
- (If time series): Dated layers for each Sentinel-1 acquisition

**Landslide (if activated)**
- Susceptibility: Brown gradient (1 = Moderate, 2 = High, 3 = Very High)
- Exposure zones: Potential flow zones (light brown)
- Buildings at risk: Buildings in risk zone (brown outline)
- Roads at risk: Roads in risk zone (brown line)

**Infrastructure**
- Large/Medium/Small airports: Blue triangles (proportional size)
- Heliports: Blue circles
- Ports: Blue squares
- Health facilities: Red crosses

### Results Export

Two export methods are offered:

#### Method 1: Instant Download (client-side)

**Advantages:**
- No Google Earth Engine account required
- Immediate download in browser
- GeoJSON format (compatible QGIS, ArcGIS, etc.)

**Limitations:**
- Maximum 5000 features per layer
- Vector data only (no rasters)

**Available files:**
- `Analysis_Summary.csv`: Textual statistics summary
- `Buildings_Damage.geojson`: Damaged buildings with attributes (T_statistic, damage, confidence)
- `Roads_Damage.geojson`: Damaged road segments with attributes
- `Flooded_Buildings.geojson`: Buildings in flooded area
- `Landslide_Buildings.geojson`: Buildings in landslide risk zone

**Procedure:**
1. In results panel, "INSTANT DOWNLOAD" section
2. Click on blue link of desired file
3. File downloads automatically

#### Method 2: Google Drive Export (complete)

**Advantages:**
- Complete dataset without feature limits
- Includes rasters (T-statistic, flood extent, landslide susceptibility)
- Shapefile + GeoTIFF format

**Limitations:**
- Requires Google Earth Engine account (free)
- Requires manual actions in Tasks interface

**Exported files:**
- `Analysis_Summary.csv`
- `Buildings_Damage.shp` (+ .dbf, .shx, .prj, .cpg)
- `Roads_Damage.shp`
- `T_Statistic_Raster.tif` (GeoTIFF, 10m resolution)
- `Flood_Extent.tif` (GeoTIFF, 10m resolution)
- `Landslide_Susceptibility.tif` (GeoTIFF, 30m resolution)
- `Landslide_Runout_Zones.tif` (GeoTIFF, 30m resolution)

**Procedure:**
1. In results panel, "GOOGLE DRIVE EXPORT" section
2. Export tasks are automatically created
3. Click on "Tasks" tab (orange icon top-right)
4. For each task:
   - Click "RUN"
   - Confirm destination folder (default: `RapidDamage_[Zone]_[Date]`)
   - Wait (blue bar → green once completed)
5. Access files in Google Drive

**Export duration (via Tasks):**
- Depends on zone size and number of features
- Generally: 2-10 minutes per task

### Troubleshooting

| Error message | Probable cause | Solution |
|---------------|----------------|----------|
| `No POST images - increase Post interval` | No Sentinel-1 image found after EVENT-date | Increase Post interval to 7-14 days |
| `Invalid date format` | Incorrect date format | Use YYYY-MM-DD format (e.g., 2025-10-28) |
| `Pre-date must be before event` | Inverted dates | Verify Pre-date < Event-date |
| `Draw an AOI first` | No study area defined | Draw polygon on map or paste WKT |
| `Invalid building asset path` | Erroneous asset path | Verify format `projects/[PROJECT]/assets/[ASSET]` |
| Calculation > 15 minutes | Area too large | Reduce AOI size (< 50 km²) |

---

<a name="step-2"></a>
## Step 2: Affected Population Estimation (QGIS post-processing)

### Context

Google Earth Engine is not optimized for building-level population estimation. Post-analysis processing in QGIS allows crossing damaged buildings with population density data to obtain an estimate of affected inhabitants.

### Prerequisites

**Software:**
- QGIS 3.x (stable version recommended)

**Required data:**

1. **Damaged building layer** (from GEE application)
   - Format: GeoJSON or Shapefile
   - File: `Buildings_Damage.geojson` or `Buildings_Damage.shp`

2. **Building height data** (optional but recommended)
   - **WSF 3D - Building Height V02**
   - Source: DLR (German Aerospace Center)
   - URL: [https://download.geoservice.dlr.de/WSF3D/files/](https://download.geoservice.dlr.de/WSF3D/files/)
   - Resolution: 90m
   - Format: GeoTIFF

**WSF3D download:**
1. Access DLR server
2. Identify tile corresponding to study area (global grid)
3. Download `.tif` file
4. Nomenclature example: `WSF3D_V02_BuildingHeight_N18W078.tif`

3. **Population density data**
   - Automatically loaded by model (WorldPop or GHS-POP)
   - Requires internet connection

### QGIS Model Installation

1. Download file `Population_building.model3` from repository:
```
tools/Population_building.model3
```

2. Open QGIS
3. Menu: **Processing** > **Toolbox**
4. Click options icon (gear) at top of toolbox
5. Select **"Add model to toolbox"**
6. Navigate to `Population_building.model3`
7. Click **Open**

Model appears in:
```
Processing
└── Models
    └── Population_building
```

### Data Preparation

**Step 1: Load damaged building layer**
1. Menu: **Layer** > **Add Layer** > **Add Vector Layer**
2. Select `Buildings_Damage.geojson` (or `.shp`)
3. Click **Add**

**Step 2: Load height layer (if available)**
1. Menu: **Layer** > **Add Layer** > **Add Raster Layer**
2. Select WSF3D `.tif` file
3. Click **Add**

### Model Execution

1. In toolbox, double-click **Population_building**
2. Configure parameters:

| Parameter | Description | Value |
|-----------|-------------|-------|
| Input building layer | Building vector layer | Buildings_Damage |
| Building height raster (optional) | Building height raster | WSF3D_BuildingHeight or leave empty |
| Population data source | Population density source | WorldPop (auto-download) |
| Output layer | Output file | Path/filename (.gpkg or .shp) |

3. Click **Run**

**Processing time:**
- 1000 buildings: ~30 seconds
- 5000 buildings: ~2 minutes
- 10000 buildings: ~5 minutes

### Results Interpretation

The model generates a new layer: `Buildings_with_population`

**New attribute fields:**

| Field | Type | Description | Unit |
|-------|------|-------------|------|
| pop_total | Float | Estimated population for this building | inhabitants |
| pop_density | Float | Population density | inhab/m² |
| building_height | Float | Estimated building height | m |
| building_volume | Float | Estimated building volume | m³ |

**Calculating total affected population:**

1. Open attribute table (right-click > **Attribute table**)
2. Click **Σ** icon (Basic statistics) at bottom of table
3. Select `pop_total` field
4. Check **Sum**
5. Read resulting value

**Example result:**
```
Sum of pop_total: 10547
```
Interpretation: Approximately 10,547 people are potentially affected by detected damage.

**Analysis by severity level:**

To cross with damage levels (Very High, High, Moderate):

**Method 1: Selection by expression**
1. In attribute table, click **Select by expression** (ε icon)
2. Enter:
```sql
"confidence" = 'Very High'
```
3. Click **Select**
4. Observe number of selected rows
5. Use **Σ** > `pop_total` > **Sum** to get population in very damaged buildings

**Method 2: Statistics by group**
1. Menu: **Vector** > **Analysis** > **Basic statistics for fields**
2. Configuration:
   - Input layer: `Buildings_with_population`
   - Field to analyze: `pop_total`
   - Field to group by category: `confidence`
3. Click **Run**

**Typical result:**
```
Confidence    | Count | Sum pop_total
-----------------------------------------
Very High     |  123  |   3456
High          |  287  |   5234
Moderate      |  472  |   1857
```

**Interpretation:**
- 3,456 people in very severely damaged buildings (priority 1)
- 5,234 people in severely damaged buildings (priority 2)
- 1,857 people in moderately damaged buildings (priority 3)

### Export and Visualization

**Thematic mapping:**
1. Right-click on layer > **Properties** > **Symbology**
2. Symbol type: **Graduated**
3. Column: `pop_total`
4. Mode: **Natural Breaks (Jenks)**
5. Color ramp: Red gradient (low to high)
6. Click **Classify** then **OK**

**Results export:**
1. Right-click on layer > **Export** > **Save Features As...**
2. Format: GeoPackage (.gpkg) or Shapefile (.shp)
3. Filename: `Buildings_Damage_Population`
4. Click **OK**

**Creating summary map (optional):**
1. Menu: **Project** > **New Print Layout**
2. Add:
   - Map view
   - Legend
   - Scale
   - Title and metadata
3. Menu: **Layout** > **Export as PDF**

### Limitations and Precautions

**Methodological limitations:**

1. **Nature of estimates**
   - Population values are **statistical estimates**, not actual counts
   - Based on density data at regional scale resolution (~100m for WorldPop)

2. **Spatial resolution**
   - WorldPop: ~100m
   - WSF3D: 90m
   - Imprecision potential for small isolated buildings

3. **Model assumptions**
   - Uniform population distribution within a building
   - Constant occupancy (no day/night variations)
   - No accounting for non-residential buildings

4. **Missing data**
   - If WSF3D unavailable: default height = 6m (2 floors)
   - If WorldPop unavailable: default regional statistical density

**Usage recommendations:**

- Use these figures as **order of magnitude**
- Apply uncertainty margin of ±30-50%
- Cross-reference with other sources (local censuses, field surveys)
- Validate in field for priority areas
- Systematically communicate limitations when disseminating results

**Correct interpretation:**
- "Approximately 10,000 people are potentially affected (estimate ±40%)"
- Avoid: "Exactly 10,547 people are affected"

---

---

<a name="scientific-methodology"></a>
# 2. Scientific Methodology

## 2.1 General System Architecture

### 2.1.1 Overview

The Rapid Damage Detection tool is based on a modular architecture composed of four main modules:
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

### 2.1.2 Main Processing Workflow

The general workflow follows this sequence:

1. **AOI definition** by user
2. **Temporal selection** (Pre-date, Event-date, Intervals)
3. **Data acquisition** Sentinel-1 and auxiliary
4. **Pre-processing** (speckle filtering, calibration, reprojection)
5. **Modular analysis** according to activated options
6. **Post-processing** (aggregation, statistics)
7. **Export** of results

---

## 2.2 Damage Detection Module

### 2.2.1 General Principle

Damage detection is based on the **Pixel-Wise T-Test (PWTT)** method developed by Ballinger (2024). This approach statistically compares two temporal periods (pre and post-event) to identify significant changes in radar backscatter.

**Fundamental hypothesis:** Structural damage modifies signal scattering properties (surface roughness, structure orientation, material moisture).

### 2.2.2 SAR Data Acquisition and Pre-processing

#### Sentinel-1 Image Selection

**Filtering criteria:**
- Acquisition mode: **IW (Interferometric Wide swath)**
- Polarization: **VV + VH** (dual-pol)
- Product type: **GRD (Ground Range Detected)**
- Spatial resolution: **10m × 10m**

**Temporal windows:**
```
Pre-window:  [Pre-date - Pre_interval] ────► [Pre-date]
                                                  │
                                                  │  Normal period
                                                  ▼
Post-window:             [Event-date] ────► [Event-date + Post_interval]
```

**Adaptive post-event window expansion:**

If no image is found in the initial window, the algorithm progressively extends the window by 1-day increments until:
- Finding at least 1 image, OR
- Reaching a maximum limit of 6 additional days

This approach ensures coverage even with irregular acquisitions.

#### Speckle Filtering

Speckle noise, inherent to SAR imagery, is attenuated by an **adaptive Lee filter** (Lee, 1980).

**Principle:** Noise reduction while preserving edges and fine details.

**Lee filter formula:**
```
I_filtered = I_mean + W × (I - I_mean)
```

Where:
- `I` = Raw pixel value
- `I_mean` = Local mean (3×3 pixel window)
- `W` = Adaptive weight function of local variance
- `η` = Theoretical coefficient of variation (multiplicative speckle)
```
W = (1 - η² / C_v²) / (1 + η²)
```

Where:
- `C_v = σ_local / I_mean` (local coefficient of variation)
- `η = 1 / √N_looks` (for Sentinel-1 GRD, N_looks ≈ 5)

**Implementation:**
```javascript
var eta = 1.0 / Math.sqrt(5);  // Sentinel-1 GRD ~ 5 looks
var kernel = ee.Kernel.square(1, 'pixels');  // 3×3 window
```

#### Logarithmic Transformation

Backscatter values are transformed to logarithmic scale (dB):
```
σ_dB = 10 × log₁₀(σ₀)
```

This transformation:
- Normalizes value distribution
- Stabilizes variance
- Linearizes radiometric relationships

### 2.2.3 Pixel-wise Statistical Test

#### Student's t-statistic Calculation

For each pixel, a two-tailed t-test is applied to compare pre and post-event means.

**Null hypothesis H₀:** μ_pre = μ_post (no change)  
**Alternative hypothesis H₁:** μ_pre ≠ μ_post (significant change)

**t-statistic formula:**
```
         μ_post - μ_pre
t = ─────────────────────────
    s_pooled × √(1/n_pre + 1/n_post)
```

Where:
```
         √[(n_pre - 1)s²_pre + (n_post - 1)s²_post]
s_pooled = ────────────────────────────────────────
                    n_pre + n_post - 2
```

With:
- `μ_pre` = Mean of pre-event values (dB)
- `μ_post` = Mean of post-event values (dB)
- `s²_pre`, `s²_post` = Sample variances
- `n_pre`, `n_post` = Number of images (distinct orbits)
- `s_pooled` = Pooled standard deviation

**Degrees of freedom:**
```
df = n_pre + n_post - 2
```

**GEE implementation:**
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

**Note:** Absolute value is used because only change magnitude matters (damage = increase or decrease in backscatter).

#### Multi-orbit Processing

Sentinel-1 acquires data along multiple **relative orbits** (ascending and descending passes). To avoid angular biases, the t-test is calculated **separately for each orbit**, then results are merged by maximum:
```
T_final(x,y) = max [T_orbit1(x,y), T_orbit2(x,y), ..., T_orbitN(x,y)]
```

This approach preserves the most significant detected change, regardless of acquisition geometry.

### 2.2.4 Multi-scale Spatial Smoothing

To reduce residual noise and highlight coherent structures, **multi-scale Gaussian smoothing** is applied:
```
T_smooth = (T_raw + T_50m + T_100m + T_150m) / 4
```

Where:
- `T_raw` = Raw t-statistic
- `T_50m` = Convolution with 50m radius Gaussian kernel
- `T_100m` = Convolution with 100m radius Gaussian kernel
- `T_150m` = Convolution with 150m radius Gaussian kernel

**Justification:** Damaged buildings generally present coherent spatial signatures over multiple pixels. Multi-scale smoothing:
- Reinforces structures of characteristic size 50-150m
- Attenuates isolated false positives (noise, artifacts)
- Preserves damaged area contours

**Implementation:**
```javascript
var T_stat_urban = maxChange_raw
  .add(maxChange_raw.convolve(ee.Kernel.circle(50, 'meters', true)))
  .add(maxChange_raw.convolve(ee.Kernel.circle(100, 'meters', true)))
  .add(maxChange_raw.convolve(ee.Kernel.circle(150, 'meters', true)))
  .divide(4);
```

### 2.2.5 Damage Level Classification

#### t-statistic Thresholding

A threshold `T_threshold` (default: 2.4) is applied to classify pixels:
```
Damage = {
  0  if T < T_threshold        (no damage)
  1  if T ≥ T_threshold        (damage detected)
}
```

**Justification for 2.4 threshold:**
- For a two-tailed t-test with df ≈ 10-20:
  - t = 2.4 corresponds approximately to p < 0.05 (95% confidence)
- Empirical compromise between:
  - Sensitivity (detecting slight damage)
  - Specificity (avoiding false positives)

#### Confidence Levels

Buildings classified as damaged are subdivided into three confidence levels:

| Level | T Range | Interpretation |
|--------|---------|----------------|
| **Moderate** | T_threshold ≤ T < T_threshold + 1 | Moderate change, validation recommended |
| **High** | T_threshold + 1 ≤ T < T_threshold + 2 | High change, strong damage probability |
| **Very High** | T ≥ T_threshold + 2 | Very high change, damage quasi-certain |

**Example with T_threshold = 2.4:**
- Moderate: 2.4 ≤ T < 3.4
- High: 3.4 ≤ T < 4.4
- Very High: T ≥ 4.4

### 2.2.6 Building-level Aggregation

#### Per-building Statistics Extraction

For each building polygon, the **mean** t-statistic is calculated:
```javascript
var fp = T_stat_image.reduceRegions({
  collection: buildings,
  reducer: ee.Reducer.mean(),
  scale: 10
});
```

**Justification for mean:**
- Robust to local extreme values
- Represents building's global change
- Compatible with t-test theory (multiple sampling)

#### Class Attribution

Each building receives:
- **T_statistic:** Mean t value
- **damage:** 0 (intact) or 1 (damaged)
- **confidence:** Moderate / High / Very High

### 2.2.7 Road Processing

#### Road Network Segmentation

Linear roads are segmented into fixed-length sections (default: 100m) via spatial grid:
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

**Algorithm:**
1. Create regular grid of 100m × 100m cells
2. Dissolve all road lines into single geometry
3. Intersect this geometry with each grid cell
4. Keep non-empty segments

#### Buffer and Statistics Extraction

Each road segment is buffered (default: 6m radius) to capture adjacent pixels:
```
─────────────────  Road (line)
     ▓▓▓▓▓         Buffer 6m
─────────────────
```

The **maximum** t-statistic is extracted within each buffer:
```javascript
var roadsStats = T_stat_roads.reduceRegions({
  collection: roadsSegmented.map(function(f) { 
    return f.buffer(BUFFER_ROADS_M); 
  }),
  reducer: ee.Reducer.max(),
  scale: 10
});
```

**Justification for maximum:**
- Damaged roads often show localized damage (craters, collapses)
- Maximum captures these local anomalies
- More sensitive than mean for linear structures

---

## 2.3 Flood Detection Module

### 2.3.1 General Principle

Flood detection exploits the **drastic decrease in radar backscatter** in presence of water. The s1flood algorithm (DeVries et al., 2020) uses a **z-score** (normalized deviation) approach to identify abnormally dark pixels.

**Physical principle:**
- Calm water surface: specular reflection → low backscatter (dark pixels)
- Dry soil or vegetation: volume scattering → high backscatter (bright pixels)

### 2.3.2 Z-score Calculation

#### Baseline Period Definition

A reference ("baseline") period is defined to characterize normal state:
```
Baseline: [Pre-date - Pre_interval] ────► [Pre-date]
```

For each pixel, **mean** (μ_baseline) and **standard deviation** (σ_baseline) are calculated over all images in this period.

#### Z-score Normalization

For each post-event image, the z-score is calculated:
```
         I_post - μ_baseline
z(x,y) = ───────────────────
            σ_baseline
```

Where:
- `I_post` = Pixel value in post-event image (dB)
- `μ_baseline` = Pixel mean during baseline period
- `σ_baseline` = Pixel standard deviation during baseline period

**Interpretation:**
- z ≈ 0: Normal value
- z < -2: Abnormally low value (flood potential)
- z < -3: Very abnormally low value (high flood probability)

#### Orbit and Polarization Separation

Z-score is calculated **separately** for:
- **Acquisition mode:** IW (Interferometric Wide)
- **Orbit direction:** Ascending / Descending
- **Polarization:** VV and VH

This separation ensures radiometric consistency of comparisons (same acquisition geometry).

**Implementation:**
```javascript
var z_asc = calcZscore(s1Collection, baseStart, baseEnd, 'IW', 'ASCENDING');
var z_dsc = calcZscore(s1Collection, baseStart, baseEnd, 'IW', 'DESCENDING');
var zAll = ee.ImageCollection(z_asc.merge(z_dsc));
```

### 2.3.3 Flood Classification

#### Z-score Thresholds

Two thresholds are applied on VV and VH polarizations:
```
ZVV_threshold = -2.5  (default)
ZVH_threshold = -2.5  (default)
```

A pixel is considered potentially flooded if:
```
Flood_candidate = (z_VV < ZVV_threshold) ∨ (z_VH < ZVH_threshold)
```

The logical **OR** operator captures floods even if only one polarization shows strong signal.

#### Permanent Water Masking

To distinguish **new floods** from **permanent water**, two sources are used:

**1. ESA WorldCover v200**
- Class 80: Permanent water bodies
- Resolution: 10m
- Year: 2021

**2. JRC Global Surface Water (Monthly History)**
- Water occurrence frequency (%)
- Resolution: 30m
- Period: 1984-present

**Masking algorithm:**
```javascript
var worldcoverWater = worldcover.eq(80);  // Permanent water (WorldCover)

var jrcvalid = jrc.map(function(x) { return x.gt(0); }).sum();  // Valid months
var jrcwat = jrc.map(function(x) { return x.eq(2); }).sum()     // Months with water
  .divide(jrcvalid).multiply(100);                              // Frequency (%)

var permanentWater = jrcwat.gte(POW_threshold);  // POW_threshold = 90% (default)
var inundation = jrcwat.gte(PIN_threshold)       // PIN_threshold = 25% (default)
                       .and(jrcwat.lt(POW_threshold));
```

**Resulting classes:**

| Class | Code | Description |
|--------|------|-------------|
| Permanent water | 20 | Permanent water (WorldCover or JRC > 90%) |
| Flood (VV only) | 1 | z_VV < threshold, z_VH > threshold |
| Flood (VH only) | 2 | z_VH < threshold, z_VV > threshold |
| Flood (VV + VH) | 3 | z_VV < threshold AND z_VH < threshold |
| Flood (Inundation) | 10 | Historically floodable zone (25% < JRC < 90%) |

### 2.3.4 Morphological Post-processing

#### Slope Filtering

High slope areas are excluded as water cannot accumulate there:
```javascript
var slope = ee.Terrain.slope(elevation);
flood = flood.updateMask(slope.lt(MAX_SLOPE));  // MAX_SLOPE = 5° (default)
```

**Justification:** Slopes > 5°: rapid runoff, improbable accumulation.

#### Connectivity Filtering

Isolated pixels (artifacts, shadows) are eliminated by connectivity filter:
```javascript
var connectedPixels = flood.connectedPixelCount();
flood = flood.updateMask(connectedPixels.gte(MIN_CONNECTIVITY));
// MIN_CONNECTIVITY = 8 pixels (default)
```

**Principle:** A pixel is kept only if connected to at least 8 other flooded pixels (connected component of size ≥ 8).

#### Spatial Smoothing

A circular median filter is applied to regularize contours:
```javascript
flood = flood.focal_median(SMOOTHING_RADIUS, 'circle', 'meters');
// SMOOTHING_RADIUS = 25m (default)
```

**Effect:** Smoothing irregular contours, closing small discontinuities.

### 2.3.5 Time Series (Time Series Mode)

#### Principle

When "Time Series" option is activated, the algorithm processes **all available Sentinel-1 dates** in the specified period:
```
Time series window: [From_date] ────────────────► [To_date]
                         │                           │
                         ▼                           ▼
                    Image 1, Image 2, ..., Image N
```

For each date, a flood map is generated by applying the s1flood algorithm.

#### Flooded Area Calculation

For each date, flooded area is calculated:
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

**Unit:** km²

#### Orbit Separation

Results are separated by orbit direction (Ascending / Descending) to track evolution independently of acquisition geometry:
```
Date       │ Ascending (km²) │ Descending (km²)
───────────┼─────────────────┼──────────────────
2025-09-05 │      0.052      │       -
2025-09-08 │       -         │      0.048
2025-09-11 │      0.103      │       -
2025-09-14 │       -         │      0.087
```

#### Evolution Graph

A **ColumnChart** (vertical bars) graph is generated with:
- X-axis: Dates
- Y-axis: Flooded area (km²)
- Series 1: Ascending orbits (light blue)
- Series 2: Descending orbits (dark blue)

**Interpretation:**
- Identifies **flood peak**
- Tracks **progressive recession**
- Detects **residual flooding**

#### Wet Baseline Detection

If the first date in time series already shows significant flooded area (> 0.5 km²), a warning is displayed:
```
WARNING: Baseline appears wet!
First date (2025-09-05) shows 0.52 km² already flooded
SUGGESTION: Move PRE_DATE earlier to ensure dry baseline
   Recommended PRE_DATE: 2025-08-05
```

This detection ensures the reference period is indeed "dry".

---

## 2.4 Landslide Detection Module

### 2.4.1 General Principle

Landslide detection combines two complementary approaches:

1. **SAR change detection** (similar to Damage module)
2. **Susceptibility model** based on environmental factors

**Hypothesis:** Landslides occur preferentially in zones combining:
- SAR backscatter change (ground movement)
- Predisposing factors (slope, curvature, precipitation, soil type)

### 2.4.2 Susceptibility Factors

The susceptibility model aggregates **five weighted factors**, inspired by Kanani-Sadat et al. (2015):

#### Factor 1: Cumulative Precipitation (weight: 0.143)

**Source:** CHIRPS Daily (Climate Hazards Group InfraRed Precipitation with Station data)

**Time window:** 30 days preceding event
```javascript
var precipStart = ee.Date(EVENT_DATE).advance(-30, 'day');
var precipEnd = ee.Date(EVENT_DATE);
var precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
  .select('precipitation')
  .filterDate(precipStart, precipEnd)
  .sum();
```

**Normalization:**
```
precipScore = min(precip / 300, 1) × 0.143
```

**Justification:**
- 300 mm in 30 days ≈ soil saturation threshold
- Weight 0.143 (14.3%) based on Kanani-Sadat et al. AHP analysis

#### Factor 2: Slope (weight: 0.128)

**Calculation:**
```javascript
var slope = ee.Terrain.slope(elevation);
```

**Normalization:**
```
slopeScore = min(slope / 30, 1) × 0.128
```

**Justification:**
- Slopes > 30°: maximum susceptibility
- Weight 0.128 (12.8%)

#### Factor 3: Soil Type - Clay (weight: 0.123)

**Source:** SoilGrids ISRIC (clay content, 0-5 cm depth)
```javascript
var clay = ee.Image('projects/soilgrids-isric/clay_mean')
  .select('clay_0-5cm_mean');
```

**Normalization:**
```
soilScore = (clay / 100) × 0.123
```

**Justification:**
- Clay soils: low permeability, instability in presence of water
- Weight 0.123 (12.3%)

#### Factor 4: Aspect (slope orientation) (weight: 0.112)

**Calculation:**
```javascript
var aspect = ee.Terrain.aspect(elevation);
var northFacing = aspect.lte(45).or(aspect.gte(315));
```

**Score:**
```
aspectScore = northFacing ? 1.0 × 0.112 : 0.5 × 0.112
```

**Justification:**
- North-facing slopes (northern hemisphere): less sunlight, residual moisture
- Weight 0.112 (11.2%)

#### Factor 5: Terrain Curvature (weight: 0.100)

**Calculation:** Curvature = divergence of elevation gradient
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

**Normalization:**
```
curvatureScore = min(|curvature| / 0.2, 1) × 0.100
```

**Justification:**
- High curvature (concave or convex): structural instability zones
- Weight 0.100 (10.0%)

#### Total Susceptibility Score
```
S_total = precipScore + slopeScore + soilScore + aspectScore + curvatureScore
```

**Range:** 0 to 0.606 (sum of weights)

### 2.4.3 SAR Change Masking

The t-statistic from the Damage Detection module is reused, with specific masks:

**Mask 1: Minimum slope**
```javascript
var mask_slope = slope.gte(MIN_SLOPE);  // MIN_SLOPE = 10° (default)
```

**Mask 2: Minimum curvature**
```javascript
var mask_curvature = curvature.gte(MIN_CURVATURE);  // MIN_CURVATURE = 0.05 (default)
```

**Mask 3: Water area exclusion**
```javascript
var waterMask = worldcover.neq(80);  // Exclude "water" class from WorldCover
```

**Application:**
```javascript
var T_stat_landslide = maxChange_raw
  .updateMask(mask_slope)
  .updateMask(mask_curvature)
  .updateMask(waterMask);
```

### 2.4.4 Probability Level Classification

Pixels are classified based on **combination** of susceptibility score and t-statistic:
```
Landslide_level = {
  0  (no landslide)      if S_total < 0.3 OR T < T_threshold
  1  (Moderate)          if S_total ≥ 0.3 AND T_threshold ≤ T < T_threshold + 1
  2  (High)              if S_total ≥ 0.3 AND T_threshold + 1 ≤ T < T_threshold + 2
  3  (Very High)         if S_total ≥ 0.3 AND T ≥ T_threshold + 2
}
```

**Susceptibility threshold: 0.3**
- Corresponds approximately to 50% of maximum possible score (0.606)
- Filters low predisposition zones

### 2.4.5 Flow Zones (Runout Zones)

Landslides can generate debris flows that flow downslope. An **exposure zone** is calculated by morphological dilation:
```javascript
var kernel = ee.Kernel.circle({radius: 100, units: 'meters'});
var runoutZone = landslides.gt(0).focal_max({kernel: kernel})
  .subtract(landslides.gt(0))
  .selfMask();
```

**Principle:**
1. Dilation of landslide zones (radius: 100m)
2. Subtraction of source zones
3. Result: 100m ring around landslides

**Interpretation:** Zone potentially affected by debris flow, even without in-situ landslide.

---

## 2.5 Weather Statistics Module

### 2.5.1 Data Sources

The weather module aggregates data from two main sources:

| Variable | Source | Spatial resolution | Temporal resolution |
|----------|--------|-------------------|---------------------|
| Precipitation | CHIRPS Daily | 5.5 km | Daily |
| Instantaneous wind | GLDAS NOAH v2.1 | 27.8 km | 3-hourly |
| Surface pressure | GLDAS NOAH v2.1 | 27.8 km | 3-hourly |

### 2.5.2 Time Window

**Standard mode:**
```
[Pre-date] ──────────────────────► [Event-date + 3 days]
```

**Time Series mode (if activated):**
```
[TIME_SERIES_START] ─────────────► [TIME_SERIES_END]
```

### 2.5.3 Daily Aggregation

For each day of the period:

**Precipitation:**
- Daily sum (mm/day)

**Wind:**
- Conversion to km/h: `wind_kmh = wind_m/s × 3.6`
- Daily average (mean wind)
- Daily maximum (maximum gust)

**Pressure:**
- Conversion to hPa: `pressure_hPa = pressure_Pa / 100`
- Daily average
- Daily minimum (depression indicator)

### 2.5.4 Global Statistics

For the entire period:
```javascript
var totalPrecip = sum(daily_precip);              // Cumulative precipitation (mm)
var maxPrecip = max(daily_precip);                // Maximum daily rain (mm)
var maxWind = max(daily_wind_max);                // Maximum gust (km/h)
var minPressure = min(daily_pressure_min);        // Minimum pressure (hPa)
```

These values are displayed in the results panel and characterize event intensity.

### 2.5.5 Graphical Visualization

**Graph 1: Daily Precipitation (ColumnChart)**

- X-axis: Dates (MM/DD)
- Y-axis: Precipitation (mm)
- Color: Blue (normal), Red (event day)

**Graph 2: Wind and Pressure (LineChart multi-axis)**

- X-axis: Dates (MM/DD)
- Y-axis left: Wind (km/h)
  - Solid green line: Mean wind
  - Dashed green line: Maximum wind
- Y-axis right: Pressure (hPa)
  - Solid yellow line: Mean pressure
  - Dashed red line: Minimum pressure

**Interpolation:** `interpolateNulls: true` to smooth missing data.

---

## 2.6 Performance Indicator Calculation

### 2.6.1 Damage Indicators

**Damage completeness:**
```
         Number of damaged buildings
E_d = ────────────────────────────────
      Total number of buildings in AOI
```

**Spatial damage density:**

Calculated by rasterization of damaged buildings (resolution: 100m) then spatial sampling:
```javascript
var damageRaster = damaged.reduceToImage({
  properties: ['damage'],
  reducer: ee.Reducer.count()
}).reproject({crs: 'EPSG:4326', scale: 100});
```

"Density bubbles" (proportional circles) are generated by:
```
radius_bubble = √(count) × 25 meters
```

### 2.6.2 Flood Indicators

**Flooded area:**
```
                  Σ (pixelArea) for flood > 0
A_flood (km²) = ─────────────────────────────
                        1,000,000
```

**Proportion of flooded buildings:**
```
         Number of buildings in flooded area
P_b = ─────────────────────────────────────
      Total number of buildings in AOI
```

**Length of flooded roads:**
```
L_road (km) = (Number of flooded segments) × (Segment length) / 1000
```

### 2.6.3 Landslide Indicators

**Area in susceptibility zone:**
```
                    Σ (pixelArea) for landslide > 0
A_landslide (km²) = ──────────────────────────────
                            1,000,000
```

**Distribution by level:**
```
A_moderate = Σ (pixelArea) for landslide = 1
A_high = Σ (pixelArea) for landslide = 2
A_very_high = Σ (pixelArea) for landslide = 3
```

### 2.6.4 Logistic Hub

The "logistic hub" is calculated as a **weighted barycenter** of damages, adjusted based on proximity to infrastructure (ports, airports).

**Step 1: Damage barycenter**
```
       Σ (lon_i × count_i)
lon_bary = ──────────────────
          Σ (count_i)

       Σ (lat_i × count_i)
lat_bary = ──────────────────
          Σ (count_i)
```

Where:
- `(lon_i, lat_i)` = Coordinates of sampling point i
- `count_i` = Number of damaged buildings in cell i

**Step 2: Infrastructure centroid**

If ports or airports are present in AOI:
```
centroid_infra = Centroid (Union of all ports and airports)
```

**Step 3: Weighted hub**
```
lon_hub = 0.7 × lon_infra + 0.3 × lon_bary
lat_hub = 0.7 × lat_infra + 0.3 × lat_bary
```

**Justification:**
- 70% weight on infrastructure: favors accessibility
- 30% weight on damages: ensures proximity to affected areas

**Step 4: Road network projection**

Hub is projected onto nearest road segment (distance < 10m) to ensure accessibility.

---

## 2.7 Methodological Limitations

### 2.7.1 Damage Detection Module Limitations

**Sensitivity to acquisition conditions:**
- SAR backscatter is influenced by soil moisture
- Precipitation between pre and post acquisitions can generate false positives

**Confusion with other changes:**
- Vegetation debris (fallen trees): signal similar to structural damage
- Residual flooding: backscatter decrease confused with damage

**Spatial resolution:**
- Sentinel-1: 10m × 10m
- Small buildings (< 100 m²): weak radar signature, limited detection

**Radar geometry:**
- Shadows and layover in mountainous areas
- Foreshortening on slopes facing satellite

### 2.7.2 Flood Detection Module Limitations

**Dense vegetation:**
- Forest canopy masks underlying water
- Underestimation of flooding in tropical forest

**Shallow water:**
- Low depth (< 10 cm): attenuated but non-null radar signal
- Risk of non-detection

**Limited acquisitions:**
- Sentinel-1: ~6 day revisit
- Short-duration flash floods (< 6 days): potentially missed

**Permanent water:**
- Dependence on JRC and WorldCover databases
- Seasonal wetlands sometimes misclassified

### 2.7.3 Landslide Detection Module Limitations

**Empirical susceptibility model:**
- Factor weights from literature (Kanani-Sadat et al., 2015)
- Not specifically calibrated for each region

**DEM resolution:**
- NASADEM / SRTM: 30m
- Inability to detect micro-topographies (< 30m)

**Detection delay:**
- Landslides manifest progressively
- Optimal SAR signal after consolidation (several days/weeks)

**Confusion with vegetation:**
- Deforestation, forest cuts: similar radar signature

### 2.7.4 Weather Statistics Module Limitations

**Spatial resolution:**
- CHIRPS: 5.5 km
- GLDAS: 27.8 km
- Sub-kilometer variability not captured (localized storms)

**Measurement accuracy:**
- CHIRPS: satellite estimates, not in-situ measurements
- GLDAS: model assimilating heterogeneous observations

**Temporal coverage:**
- GLDAS: 3-hourly resolution
- Very short-duration phenomena (gusts < 1h): potentially missed

### 2.7.5 Recommendations to Mitigate Limitations

1. **Systematic validation** by HR photo-interpretation
2. **Multi-source cross-referencing** (SAR + optical + field)
3. **Local context knowledge** (geology, urban planning, climatology)
4. **Critical analysis of results** (false positives, false negatives)
5. **Transparent communication of uncertainties** to end users

---

## 2.8 Improvement Perspectives

### 2.8.1 Algorithmic Improvements

**SAR + Optical fusion:**
- Integration of Sentinel-2 (optical) to reduce SAR ambiguities
- Damage detection by NDVI change (vegetation)

**Machine Learning:**
- Training supervised models (Random Forest, CNN) on annotated datasets
- Automatic classification of damage types (collapse, cracking, etc.)

**Advanced multi-temporal analysis:**
- Tracking damage evolution over weeks/months
- Detection of progressive damage (settlement, subsidence)

### 2.8.2 New Data Source Integration

**High-resolution SAR imagery:**
- ICEYE (resolution < 1m)
- Capella Space (sub-meter resolution)

**LiDAR elevation data:**
- Detection of elevation changes (collapses)
- Precise 3D modeling

**Social media and crowdsourcing:**
- Geolocated tweets, Flickr photos
- Rapid validation by local populations

### 2.8.3 Mobile/Field Version Development

**Mobile application:**
- Display results on smartphone/tablet
- Field data collection (photos, GPS)
- Bidirectional synchronization (cloud ↔ field)

**Offline mode:**
- Pre-download maps and results
- Use in areas without connectivity

---

---

<a name="data-sources"></a>
# 3. Data Sources

## 3.1 Satellite Data

### 3.1.1 Sentinel-1 SAR

**Description:** Constellation of C-band radar satellites (5.405 GHz) from the European Space Agency (ESA).

**Technical specifications:**
- **Satellites:** Sentinel-1A (launched 2014), Sentinel-1B (launched 2016, out of service since 2021), Sentinel-1C (planned 2024)
- **Acquisition mode used:** Interferometric Wide Swath (IW)
- **Polarization:** Dual-pol (VV+VH)
- **Spatial resolution:** 10m × 10m (GRD)
- **Swath:** 250 km
- **Revisit period:** ~6 days (full constellation)
- **Orbits:** Ascending and descending

**Product used:**
- **Type:** GRD (Ground Range Detected)
- **Processing level:** Level-1
- **GEE Collection:** `COPERNICUS/S1_GRD` and `COPERNICUS/S1_GRD_FLOAT`

**Reference:**
- ESA Sentinel Online: [https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1)

---

### 3.1.2 CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)

**Description:** Daily precipitation data at quasi-global resolution, combining infrared satellite observations and ground stations.

**Specifications:**
- **Spatial resolution:** 0.05° (~5.5 km)
- **Temporal resolution:** Daily
- **Temporal coverage:** 1981-present
- **Spatial coverage:** 50°N - 50°S
- **Unit:** mm/day

**GEE Collection:** `UCSB-CHG/CHIRPS/DAILY`

**Reference:**
- Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*, 2, 150066. [https://doi.org/10.1038/sdata.2015.66](https://doi.org/10.1038/sdata.2015.66)
- Official website: [https://www.chc.ucsb.edu/data/chirps](https://www.chc.ucsb.edu/data/chirps)

---

### 3.1.3 GLDAS (Global Land Data Assimilation System)

**Description:** Land data assimilation system providing meteorological and hydrological variables at global scale.

**Version used:** GLDAS-2.1 NOAH

**Specifications:**
- **Spatial resolution:** 0.25° (~27.8 km)
- **Temporal resolution:** 3-hourly
- **Variables used:**
  - `Wind_f_inst`: Instantaneous wind speed (m/s)
  - `Psurf_f_inst`: Instantaneous surface pressure (Pa)
- **Temporal coverage:** 2000-present

**GEE Collection:** `NASA/GLDAS/V021/NOAH/G025/T3H`

**Reference:**
- Rodell, M., Houser, P. R., Jambor, U., et al. (2004). The Global Land Data Assimilation System. *Bulletin of the American Meteorological Society*, 85(3), 381-394. [https://doi.org/10.1175/BAMS-85-3-381](https://doi.org/10.1175/BAMS-85-3-381)

---

## 3.2 Digital Elevation Models (DEM)

### 3.2.1 NASADEM

**Description:** Global digital elevation model derived from SRTM mission, reprocessed by NASA for improved accuracy.

**Specifications:**
- **Spatial resolution:** 1 arc-second (~30m)
- **Spatial coverage:** 60°N - 56°S
- **Vertical accuracy:** ±9m (90% confidence)
- **Reference year:** 2000 (SRTM acquisition)

**GEE Collection:** `NASA/NASADEM_HGT/001`

**Reference:**
- NASA JPL (2020). NASADEM Merged DEM Global 1 arc second. [https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001](https://doi.org/10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001)

---

### 3.2.2 SRTM (Shuttle Radar Topography Mission)

**Description:** Global DEM acquired by SRTM space mission in 2000.

**Specifications:**
- **Spatial resolution:** 1 arc-second (~30m)
- **Spatial coverage:** 60°N - 56°S
- **Vertical accuracy:** ±16m (90% confidence)

**GEE Collection:** `USGS/SRTMGL1_003`

**Reference:**
- Farr, T. G., Rosen, P. A., Caro, E., et al. (2007). The Shuttle Radar Topography Mission. *Reviews of Geophysics*, 45(2). [https://doi.org/10.1029/2005RG000183](https://doi.org/10.1029/2005RG000183)

---

### 3.2.3 ALOS World 3D

**Description:** Global DEM based on Japanese ALOS PRISM satellite data.

**Specifications:**
- **Spatial resolution:** 1 arc-second (~30m)
- **Spatial coverage:** Global (82°N - 82°S)
- **Vertical accuracy:** ±5m (flat areas), ±7m (mountainous areas)
- **Version:** 3.2

**GEE Collection:** `JAXA/ALOS/AW3D30/V3_2`

**Reference:**
- JAXA (2021). ALOS Global Digital Surface Model "ALOS World 3D-30m" (AW3D30). [https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm](https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm)

---

### 3.2.4 ASTER GDEM

**Description:** Global DEM from ASTER (Advanced Spaceborne Thermal Emission and Reflection Radiometer) radiometer.

**Specifications:**
- **Spatial resolution:** 1 arc-second (~30m)
- **Spatial coverage:** 83°N - 83°S
- **Vertical accuracy:** ±17m (95% confidence)
- **Version:** 3

**GEE Collection:** `NASA/ASTER_GED/AG100_003`

**Reference:**
- NASA/METI/AIST/Japan Spacesystems, U.S./Japan ASTER Science Team (2019). ASTER Global Digital Elevation Model V003. [https://doi.org/10.5067/ASTER/ASTGTM.003](https://doi.org/10.5067/ASTER/ASTGTM.003)

---

## 3.3 Land Cover Data

### 3.3.1 ESA WorldCover

**Description:** 10m resolution land cover map based on Sentinel-1 and Sentinel-2.

**Specifications:**
- **Spatial resolution:** 10m
- **Reference year:** 2021
- **Nomenclature:** 11 classes (Tree cover, Shrubland, Grassland, Cropland, Built-up, Bare/sparse vegetation, Snow/ice, Permanent water bodies, Herbaceous wetland, Mangroves, Moss/lichen)
- **Global accuracy:** 74.4%

**GEE Collection:** `ESA/WorldCover/v200`

**Reference:**
- Zanaga, D., Van De Kerchove, R., Daems, D., et al. (2022). ESA WorldCover 10 m 2021 v200. [https://doi.org/10.5281/zenodo.7254221](https://doi.org/10.5281/zenodo.7254221)

---

### 3.3.2 JRC Global Surface Water

**Description:** Monthly and annual maps of surface water presence based on 38 years of Landsat imagery.

**Specifications:**
- **Spatial resolution:** 30m
- **Temporal coverage:** 1984-2022
- **Temporal resolution:** Monthly
- **Product used:** Monthly History (water occurrence per month)

**GEE Collection:** `JRC/GSW1_4/MonthlyHistory`

**Reference:**
- Pekel, J.-F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). High-resolution mapping of global surface water and its long-term changes. *Nature*, 540, 418-422. [https://doi.org/10.1038/nature20584](https://doi.org/10.1038/nature20584)

---

## 3.4 Population Data

### 3.4.1 WorldPop

**Description:** Disaggregated population estimates at high spatial resolution based on censuses and auxiliary data.

**Specifications:**
- **Spatial resolution:** 100m
- **Unit:** Number of inhabitants per pixel
- **Methodology:** Random Forest on covariates (built-up, land use, accessibility, etc.)
- **Update:** Annual

**GEE Collection:** `WorldPop/GP/100m/pop`

**Reference:**
- Tatem, A. J. (2017). WorldPop, open data for spatial demography. *Scientific Data*, 4, 170004. [https://doi.org/10.1038/sdata.2017.4](https://doi.org/10.1038/sdata.2017.4)
- Official website: [https://www.worldpop.org/](https://www.worldpop.org/)

---

### 3.4.2 WSF 3D - Building Height

**Description:** Global map of building heights at 90m resolution derived from TanDEM-X SAR and Sentinel-2 optical data.

**Specifications:**
- **Spatial resolution:** 90m (3 arc-seconds)
- **Unit:** Meters (building height)
- **Temporal coverage:** 2015-2017
- **Accuracy:** RMSE ~6m for buildings > 15m height

**Source:** DLR (German Aerospace Center)

**Download:** [https://download.geoservice.dlr.de/WSF3D/files/](https://download.geoservice.dlr.de/WSF3D/files/)

**Reference:**
- Esch, T., Brzoska, E., Dech, S., et al. (2022). World Settlement Footprint 3D - A first three-dimensional survey of the global building stock. *Remote Sensing of Environment*, 270, 112877. [https://doi.org/10.1016/j.rse.2021.112877](https://doi.org/10.1016/j.rse.2021.112877)

---

## 3.5 Vector Data

### 3.5.1 Google Open Buildings v3

**Description:** Building footprint database detected by machine learning from satellite imagery.

**Specifications:**
- **Coverage:** Africa, South Asia, Southeast Asia, Latin America (excluding USA, Canada, Europe)
- **Number of buildings:** ~1.8 billion
- **Source resolution:** 50 cm (Maxar imagery)
- **Methodology:** Detection by convolutional neural networks (U-Net)
- **Main attribute:** `confidence` (confidence score 0-1)

**GEE Collection:** `GOOGLE/Research/open-buildings/v3/polygons`

**Reference:**
- Google Research (2023). Open Buildings V3. [https://sites.research.google/open-buildings/](https://sites.research.google/open-buildings/)

---

### 3.5.2 Microsoft Building Footprints (VIDA Combined)

**Description:** Building footprints extracted by deep learning from Bing aerial imagery.

**Specifications:**
- **Coverage:** Global (by country)
- **Number of buildings:** >1 billion
- **Methodology:** ResNet-based segmentation
- **Format:** GeoJSON

**Access via VIDA Combined:**
- **Collection:** Fusion Google Open Buildings + Microsoft Buildings
- **Source:** SAT-IO (Samapriya Roy)
- **GEE Access:** `projects/sat-io/open-datasets/VIDA_COMBINED/[ISO_CODE]`

**Reference:**
- Microsoft (2023). GlobalMLBuildingFootprints. [https://github.com/microsoft/GlobalMLBuildingFootprints](https://github.com/microsoft/GlobalMLBuildingFootprints)
- Gonzales, J. J. (2023). Building-level comparison of Microsoft and Google open building footprints datasets. *GIScience 2023*.

---

### 3.5.3 GRIP4 (Global Roads Inventory Project)

**Description:** Global road network inventory combining OpenStreetMap data and national sources.

**Specifications:**
- **Coverage:** Global (by region)
- **Road types:** Highways, national roads, regional roads
- **Attributes:** Type, surface, number of lanes
- **Available regions:** 
  - North-America
  - Central-South-America
  - Europe
  - Africa
  - Middle-East-Central-Asia
  - South-East-Asia
  - Oceania

**GEE Access:** `projects/sat-io/open-datasets/GRIP4/[REGION]`

**Reference:**
- Meijer, J. R., Huijbregts, M. A. J., Schotten, K. C. G. J., & Schipper, A. M. (2018). Global patterns of current and future road infrastructure. *Environmental Research Letters*, 13(6), 064006. [https://doi.org/10.1088/1748-9326/aabd42](https://doi.org/10.1088/1748-9326/aabd42)

---

### 3.5.4 OurAirports

**Description:** Global database of airports and heliports.

**Specifications:**
- **Coverage:** Global
- **Types:** Large/Medium/Small airports, Heliports, Closed airports
- **Attributes:** Type, name, ICAO/IATA code, coordinates, elevation
- **Update:** Contributive (crowdsourced)

**Asset used:** `projects/rapiddamagedetection/assets/ourairports`

**Original source:** [https://ourairports.com/data/](https://ourairports.com/data/)

**License:** Public Domain (data accessible via GitHub)

**Reference:**
- OurAirports (2024). Airport data. GitHub repository: [https://github.com/davidmegginson/ourairports-data](https://github.com/davidmegginson/ourairports-data)

---

### 3.5.5 Upply Seaports Database

**Description:** Global database of commercial seaports.

**Specifications:**
- **Coverage:** Global
- **Number of ports:** ~9000
- **Attributes:** Name, country, coordinates, port type
- **Update:** Regular

**Asset used:** `projects/rapiddamagedetection/assets/upply-seaports`

**Original source:** [https://opendata.upply.com/seaports](https://opendata.upply.com/seaports)

**License:** Creative Commons Attribution 4.0 (CC BY 4.0)

**Terms of use:** Mandatory attribution: "Source: Upply (upply.com)"

**Reference:**
- Upply (2024). Sea Port Database (Open Data). [https://opendata.upply.com/seaports](https://opendata.upply.com/seaports)

---

### 3.5.6 Health Sites (Humanitarian OpenStreetMap)

**Description:** Health facility locations extracted from OpenStreetMap.

**Specifications:**
- **Coverage:** Variable according to OSM contributions
- **Types:** Hospitals, clinics, health centers
- **Geometry:** Points (nodes) and polygons (ways)

**GEE Collections:**
- `projects/sat-io/open-datasets/health-site-node` (points)
- `projects/sat-io/open-datasets/health-site-way` (polygons)

**Reference:**
- Humanitarian OpenStreetMap Team (2024). Health facilities. Accessible via SAT-IO.

---

### 3.5.7 Custom Assets - Jamaica Whitehouse Example

**Description:** Local data extracted from OpenStreetMap for Whitehouse area, Jamaica (Hurricane Melissa, October 2025).

**Extraction date:** March 4, 2026

**Extraction method:** Overpass API (OpenStreetMap)

**Available assets:**
- `projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/AOI_whitehouse`
- `projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Building_OSM_whitehouse`
- `projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Road_OSM_whitehouse`

**License:** OpenStreetMap Database License (ODbL)

**Attribution:** © OpenStreetMap contributors

---

## 3.6 Soil Data

### 3.6.1 SoilGrids - Clay Content

**Description:** Global soil property maps at 250m resolution.

**Variable used:** Clay content (0-5 cm depth)

**Specifications:**
- **Spatial resolution:** 250m
- **Depth:** 0-5 cm
- **Unit:** g/kg (grams of clay per kilogram of soil)
- **Methodology:** Machine learning on >150,000 soil profiles

**GEE Collection:** `projects/soilgrids-isric/clay_mean` (band `clay_0-5cm_mean`)

**Reference:**
- Poggio, L., de Sousa, L. M., Batjes, N. H., et al. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. *SOIL*, 7, 217-240. [https://doi.org/10.5194/soil-7-217-2021](https://doi.org/10.5194/soil-7-217-2021)
- Official website: [https://www.isric.org/explore/soilgrids](https://www.isric.org/explore/soilgrids)

---

<a name="bibliography"></a>
# 4. Bibliography

## 4.1 Scientific Articles - Methodology

### 4.1.1 Damage Detection

**Ballinger, O. (2024).** Open access battle damage detection via pixel-wise t-test on Sentinel-1 imagery. *arXiv preprint*. [https://doi.org/10.48550/arXiv.2405.06323](https://doi.org/10.48550/arXiv.2405.06323)

> Foundational article for PWTT (Pixel-Wise T-Test) method used for damage detection. Describes statistical test applied pixel-by-pixel on Sentinel-1 time series to identify significant backscatter changes.

---

### 4.1.2 Flood Detection

**DeVries, B., Huang, C., Armston, J., Huang, W., Jones, J. W., & Lang, M. W. (2020).** Rapid and robust monitoring of flood events using Sentinel-1 and Landsat data on the Google Earth Engine. *Remote Sensing of Environment*, 240, 111664. [https://doi.org/10.1016/j.rse.2020.111664](https://doi.org/10.1016/j.rse.2020.111664)

> Reference article for s1flood algorithm. Describes flood detection method by z-score applied to Sentinel-1 data, with permanent water masking and multi-temporal validation.

---

### 4.1.3 Landslide Detection

**Handwerger, A. L., Huang, M.-H., Jones, S. Y., Amatya, P., Kerner, H. R., & Kirschbaum, D. B. (2022).** Generating landslide density heatmaps for rapid detection using open-access satellite radar data in Google Earth Engine. *Natural Hazards and Earth System Sciences*, 22(3), 753-774. [https://doi.org/10.5194/nhess-22-753-2022](https://doi.org/10.5194/nhess-22-753-2022)

> Method for creating landslide density heatmaps based on Sentinel-1 data. Approach through SAR change detection combined with temporal coherence analysis.

**Kanani-Sadat, Y., Pradhan, B., Pirasteh, S., & Mansor, S. (2015).** Landslide susceptibility mapping using GIS-based statistical models and remote sensing data in tropical environment. *Scientific Reports*, 5, 9899. [https://doi.org/10.1038/srep09899](https://doi.org/10.1038/srep09899)

> Landslide susceptibility model by multi-criteria analysis. Source of weights used for susceptibility factors (precipitation, slope, soil, aspect, curvature) via AHP (Analytical Hierarchy Process) method.

---

### 4.1.4 Building Database Comparison

**Gonzales, J. J. (2023).** Building-level comparison of Microsoft and Google open building footprints datasets. In *GIScience 2023: 12th International Conference on Geographic Information Science* (LIPIcs, Vol. 277, Article 35). Schloss Dagstuhl – Leibniz-Zentrum für Informatik. [https://doi.org/10.4230/LIPIcs.GIScience.2023.35](https://doi.org/10.4230/LIPIcs.GIScience.2023.35)

> Comparative analysis of Microsoft and Google Open Buildings databases. Geometric matching methodology and quality evaluation by completeness, positional accuracy, and over-completeness indicators. Inspiration for Python comparison script.

---

## 4.2 Code References and Implementations

### 4.2.1 PWTT - Damage Detection

**Ballinger, O. (2024).** PWTT: Pixel-Wise T-Test for battle damage detection [Source code]. GitHub repository. [https://github.com/oballinger/PWTT](https://github.com/oballinger/PWTT)

> Reference implementation of pixel-wise t-test in Python and JavaScript (Google Earth Engine). Source code adapted for this tool's Damage Detection module.

---

### 4.2.2 s1flood - Flood Mapping

**DeVries, B. (2019).** s1flood: Rapid flood mapping with Sentinel-1 on Google Earth Engine [Source code]. GitHub repository. [https://github.com/bendv/s1flood](https://github.com/bendv/s1flood)

> JavaScript Google Earth Engine script for rapid flood detection. Z-score algorithm and permanent water masking adapted for Flood Detection module.

---

### 4.2.3 Landslide Heatmaps - Google Earth Engine

**Huang, M.-H., & Handwerger, A. L. (2021).** Codes-for-Handwerger-et-al-2021-preprint: Generating landslide density heatmaps for rapid detection using open-access satellite radar data in Google Earth Engine [Source code]. GitHub repository. [https://github.com/MongHanHuang/Codes-for-Handwerger-et-al-2021-preprint](https://github.com/MongHanHuang/Codes-for-Handwerger-et-al-2021-preprint)

> Google Earth Engine scripts for landslide heatmap generation. Inspiration for SAR detection approach and spatial aggregation.

---

### 4.2.4 Building Comparison - Python/QGIS Script

**Gonzales, J. J. (2023).** Building-Level Comparison of Microsoft and Google Open Buildings [Supplemental code]. Oak Ridge National Laboratory.

> Source code and methodology for geometric comparison of building databases. Inspiration for matching criteria (distance, overlap) and quality indicator calculation in Python QGIS script.

---

## 4.3 Statistical Methods and Signal Processing

**Lee, J.-S. (1980).** Digital image enhancement and noise filtering by use of local statistics. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, PAMI-2(2), 165-168. [https://doi.org/10.1109/TPAMI.1980.4766994](https://doi.org/10.1109/TPAMI.1980.4766994)

> Adaptive Lee filter for speckle reduction in SAR images. Theoretical basis for Sentinel-1 data pre-processing.

**Student (1908).** The probable error of a mean. *Biometrika*, 6(1), 1-25. [https://doi.org/10.1093/biomet/6.1.1](https://doi.org/10.1093/biomet/6.1.1)

> Foundational article for Student's t-test. Theoretical basis for pixel-wise statistical test used in damage detection.

---

## 4.4 Reference Books

**Ulaby, F. T., & Long, D. G. (2014).** *Microwave Radar and Radiometric Remote Sensing*. University of Michigan Press. ISBN: 978-0-472-11935-6.

> Reference book on radar remote sensing. Backscatter theory, roughness and moisture effects, SAR signature interpretation.

**Richards, J. A. (2009).** *Remote Sensing with Imaging Radar*. Springer. ISBN: 978-3-642-02020-9.

> Principles of radar imaging, acquisition geometry, speckle processing, natural disaster applications.

---

## 4.5 Technical Documentation and User Guides

**ESA (2022).** Sentinel-1 SAR User Guide. European Space Agency. [https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-1-sar](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-1-sar)

> Official Sentinel-1 user guide. Technical specifications, acquisition modes, processing levels, data access.

**Google Earth Engine Team (2024).** Google Earth Engine Documentation. [https://developers.google.com/earth-engine](https://developers.google.com/earth-engine)

> Official Google Earth Engine documentation. JavaScript API, data collections, tutorials, code examples.

**QGIS Development Team (2024).** QGIS User Guide. QGIS Project. [https://docs.qgis.org/](https://docs.qgis.org/)

> Official QGIS documentation. Vector data processing, graphical modeling, Python API.

---

<a name="license"></a>
# 5. License and Contributions

## 5.1 Project License

This project is distributed under **MIT License**.
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

## 5.2 Third-Party Data Licenses

Use of this tool involves access to third-party data subject to their own licenses:

| Data | License | Attribution required |
|------|---------|---------------------|
| Sentinel-1 | Copernicus Open Access Hub (free) | "Contains modified Copernicus Sentinel data [Year]" |
| CHIRPS | Creative Commons (CC) | "CHIRPS data provided by UCSB Climate Hazards Center" |
| GLDAS | NASA Open Data (free) | "Data: NASA GLDAS" |
| NASADEM, SRTM, ASTER | NASA/USGS Open Data | "Data: NASA/USGS" |
| ESA WorldCover | ESA Open Data | "Contains ESA WorldCover data [Year]" |
| JRC Global Surface Water | European Commission Open Data | "Data: EC JRC" |
| WorldPop | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: WorldPop (www.worldpop.org)" |
| Google Open Buildings | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: Google Open Buildings" |
| Microsoft Buildings | Open Data Commons Open Database License (ODbL) | "Data: Microsoft" |
| GRIP4 | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: GRIP4 (Meijer et al., 2018)" |
| OurAirports | Public Domain | None (optional: "Data: OurAirports") |
| Upply Seaports | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: Upply (upply.com)" - MANDATORY |
| OpenStreetMap | Open Database License (ODbL) | "© OpenStreetMap contributors" - MANDATORY |
| SoilGrids | Creative Commons Attribution 4.0 (CC BY 4.0) | "Data: ISRIC SoilGrids" |

**Recommended attribution mentions in publications:**
```
This work uses Sentinel-1 data (ESA Copernicus), CHIRPS (UCSB CHG),
GLDAS (NASA), Google Open Buildings, Microsoft Building Footprints, GRIP4,
Upply Seaports Database, OpenStreetMap contributors, and SoilGrids (ISRIC).
```

---

## 5.3 Citation of This Tool

If you use this tool in your research work, please cite it as follows:

**APA format:**
```
Renoux, F. (2026). Rapid Damage Detection Tool: Post-disaster assessment using 
Sentinel-1 SAR data on Google Earth Engine [Software]. 
GitHub repository: https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping
```

**BibTeX format:**
```bibtex
@software{renoux2026rapid,
  author = {Renoux, Fabrice},
  title = {Rapid Damage Detection Tool: Post-disaster assessment using Sentinel-1 SAR data on Google Earth Engine},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping},
  note = {Master's thesis project, AgroParisTech SILAT}
}
```

---

## 5.4 Contributions and Collaborative Development

### 5.4.1 How to Contribute

Contributions are welcome! Here's how to participate:

**Accepted contribution types:**
- Bug fixes
- Algorithmic improvements
- New feature additions
- Documentation improvements
- Translations
- Use case examples

**Contribution process:**

1. **Fork** the repository
2. Create a **branch** for your feature:
```bash
   git checkout -b feature/AmazingFeature
```
3. **Commit** your changes:
```bash
   git commit -m 'Add some AmazingFeature'
```
4. **Push** to the branch:
```bash
   git push origin feature/AmazingFeature
```
5. Open a **Pull Request**

**Contribution rules:**
- Respect existing code style
- Document new features
- Include tests if applicable
- Update README if necessary

### 5.4.2 Bug Reporting

To report a bug, open an **Issue** on GitHub with:
- **Clear description** of the problem
- **Steps to reproduce** the bug
- **Expected behavior** vs observed
- **Screenshots** if relevant
- **Configuration** (browser, operating system)

### 5.4.3 Feature Requests

To propose a new feature, open an **Issue** with `enhancement` label and describe:
- The **need** or problem to solve
- The **proposed solution**
- **Alternatives** considered
- **Usage context**

---

## 5.5 Contact and Support

**Author:** Fabrice Renoux  
**Institution:** AgroParisTech - SILAT Master's Program  
**Email:** renoux.fabrice@hotmail.fr

**For any questions:**
- Open an **Issue** on GitHub (recommended)
- Email contact for confidential questions

**Response time:** 3-5 business days (academic project, support not guaranteed)

---

## 5.6 Acknowledgments

This project was carried out as part of the **SILAT Master's Program** (Systèmes d'Informations Localisées pour l'Aménagement des Territoires) at **AgroParisTech**.

**Special thanks to:**
- **Owen Ballinger** for developing the PWTT method and sharing source code
- **Ben DeVries** for the s1flood algorithm and associated documentation
- **Alexander Handwerger** and **Mong-Han Huang** for landslide detection methods
- **Google Earth Engine Team** for the processing platform and data access
- **ESA Copernicus** for Sentinel-1 data
- All **open database contributors** (OpenStreetMap, Google, Microsoft, etc.)
- **SILAT Master's teaching team** for project supervision

---

# 6. GitHub Repository Structure
```
Rapid-Cyclone-Damage-Mapping/
│
├── README.md                          # This file (English version)
├── README.fr.md                       # French version
│
├── LICENSE                            # MIT License
│
├── app/
│   └── rapid_damage_detection.js      # JavaScript source code (Google Earth Engine)
│
├── tools/
│   ├── building_quality_comparison.py # QGIS building comparison script
│   └── Population_building.model3     # QGIS population estimation model
│
├── docs/
│   ├── user_guide.md                  # Detailed user guide
│   ├── methodology.md                 # Scientific methodology
│   ├── data_sources.md                # Data sources
│   └── screenshots/                   # Application screenshots
│       ├── main_interface.png
│       ├── results_panel.png
│       ├── damage_map.png
│       ├── flood_map.png
│       └── landslide_map.png
│
├── examples/
│   ├── jamaica_whitehouse_2025/
│   │   ├── config.json                # Example configuration
│   │   └── README.md                  # Example documentation
│   └── [other_examples]/
│
├── tests/
│   ├── test_damage_detection.js       # Unit tests (Damage module)
│   ├── test_flood_detection.js        # Unit tests (Flood module)
│   └── test_landslide_detection.js    # Unit tests (Landslide module)
│
├── assets/
│   └── logo.png                       # Project logo
│
├── CHANGELOG.md                       # Version history
│
└── CONTRIBUTING.md                    # Contribution guide
```

---

# 7. Installation and Deployment

## 7.1 For Users

**No installation required** - The application runs entirely online.

**Direct access:**
[https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app)

**Prerequisites:**
- Google account (free)
- Modern web browser

---

## 7.2 For Developers

### 7.2.1 Clone Repository
```bash
git clone https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping.git
cd Rapid-Cyclone-Damage-Mapping
```

### 7.2.2 Google Earth Engine Configuration

1. Create GEE account: [https://earthengine.google.com/signup/](https://earthengine.google.com/signup/)
2. Install Python API (optional):
```bash
   pip install earthengine-api
```
3. Authenticate:
```bash
   earthengine authenticate
```

### 7.2.3 Application Deployment

**Via GEE web interface:**
1. Open Google Earth Engine Code Editor: [https://code.earthengine.google.com/](https://code.earthengine.google.com/)
2. Copy content of `app/rapid_damage_detection.js`
3. Paste into editor
4. Click **Run** to test
5. Click **Apps** > **New App** to deploy

**Via Python API:**
```python
import ee
ee.Initialize()

# Load script
with open('app/rapid_damage_detection.js', 'r') as f:
    script = f.read()

# Deploy (requires appropriate permissions)
```

---
---

# 8. Roadmap

## Version 1.0 (current)
- ✅ Damage Detection module (PWTT)
- ✅ Flood Detection module (s1flood)
- ✅ Landslide Detection module (heatmaps + susceptibility)
- ✅ Weather Statistics module
- ✅ Client-side export (GeoJSON)
- ✅ Google Drive export (Shapefile + GeoTIFF)
- ✅ Time Series (flood only)
- ✅ QGIS building comparison script
- ✅ QGIS population estimation model

## Version 1.1 (planned - Q2 2026)
- ⬜ Optical fusion (Sentinel-2) for validation
- ⬜ Progressive damage detection (multi-temporal tracking)
- ⬜ Automated PDF export (maps + statistics)
- ⬜ Multilingual interface (EN, FR, ES)
- ⬜ User interface improvements

## Version 2.0 (planned - Q4 2026)
- ⬜ Machine learning model integration
- ⬜ High-resolution SAR data support (ICEYE, Capella)
- ⬜ Mobile application (field data collection)
- ⬜ REST API for integration into other systems
- ⬜ Real-time dashboard (continuous monitoring)

---

# 9. FAQ (Frequently Asked Questions)

**Q1: Can this tool be used for operational interventions?**

No. This tool is **experimental** and intended for research. Results must be validated by experts before any operational use.

---

**Q2: Why do my results differ between two analyses of the same area?**

Several factors can explain this variability:
- New Sentinel-1 images available (recent acquisitions)
- Modified parameters (thresholds, intervals)
- Updated auxiliary data (WorldPop, WorldCover)
- Variability in SAR acquisition conditions (soil moisture, wind)

---

**Q3: Can I use the tool for other disaster types (wildfires, droughts)?**

The **Damage Detection** module can detect SAR changes for wildfires (debris, ash). For droughts, Sentinel-1 alone is insufficient (prefer optical indices like NDVI).

---

**Q4: How long should I wait after an event to run the analysis?**

**Ideally: 3-7 days** after the event to:
- Ensure at least one post-event Sentinel-1 acquisition
- Allow stabilization of ground conditions (water evacuation, debris)

---

**Q5: Does the tool work in polar or desert areas?**

**Polar areas:** Sentinel-1 data available, but DEMs (NASADEM, SRTM) are limited to 60°N-56°S.  
**Desert areas:** Yes, but sand changes (dunes) can generate false positives.

---

**Q6: Can I export results in formats other than GeoJSON/Shapefile?**

Currently: GeoJSON (client-side) and Shapefile (Google Drive).  
**Alternatives:** Convert files in QGIS (Layer > Export > Save As...) to KML, GeoPackage, CSV, etc.

---

**Q7: Is data stored somewhere? Are there privacy concerns?**

**No.** The application stores no user data. All analyses are performed server-side (Google Earth Engine) and results are only accessible by the connected user. Google Drive exports are stored in the user's personal Drive.

---

**Q8: Can the tool analyze very large areas (entire country)?**

**No.** Google Earth Engine imposes computation limits. For areas > 100 km², calculation time can exceed 30 minutes and analysis may fail. **Solution:** Divide area into multiple sub-areas.

---

**Q9: How do I report a bug or suggest an improvement?**

Open an **Issue** on GitHub: [https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping/issues](https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping/issues)

---

**Q10: Can I use my own building/road data instead of global databases?**

**Yes.** Use the "Custom asset" option and upload your data to Google Earth Engine. Required format: FeatureCollection (polygons for buildings, lines for roads).

---

# 10. Glossary

| Term | Definition |
|------|-----------|
| **AOI** | Area of Interest - Study area defined by user |
| **CHIRPS** | Climate Hazards Group InfraRed Precipitation with Station data - Precipitation data |
| **DEM** | Digital Elevation Model - Terrain elevation model |
| **GEE** | Google Earth Engine - Geospatial processing platform |
| **GLDAS** | Global Land Data Assimilation System - Global meteorological data |
| **GRD** | Ground Range Detected - Sentinel-1 Level-1 product |
| **IW** | Interferometric Wide swath - Sentinel-1 acquisition mode |
| **JRC** | Joint Research Centre - European Commission research center |
| **MAD** | Median Absolute Deviation - Robust statistical dispersion measure |
| **NASADEM** | Global DEM reprocessed by NASA from SRTM |
| **PWTT** | Pixel-Wise T-Test - T-test applied pixel by pixel |
| **SAR** | Synthetic Aperture Radar - Synthetic aperture radar |
| **SRTM** | Shuttle Radar Topography Mission - Radar topography mission |
| **VH/VV** | Radar polarizations (Vertical-Horizontal / Vertical-Vertical) |
| **WorldCover** | ESA 10m land cover map |
| **WorldPop** | Disaggregated population data |
| **z-score** | Normalized deviation - (value - mean) / standard deviation |

---

# 11. Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "Memory limit exceeded" error

**Symptom:** Analysis fails with memory error message

**Causes:**
- AOI too large (> 100 km²)
- Too many buildings/roads in area
- Time series with many dates

**Solutions:**
1. Reduce AOI size
2. Divide area into smaller sub-regions
3. Reduce time series date range
4. Disable unnecessary modules

---

### Issue 2: No results displayed

**Symptom:** Analysis completes but no layers appear

**Causes:**
- No Sentinel-1 images found
- Threshold too high (no damage detected)
- Data source unavailable

**Solutions:**
1. Check pre/post intervals - increase if needed
2. Lower T-threshold to 2.0
3. Verify internet connection
4. Check GEE service status

---

### Issue 3: Exports fail

**Symptom:** Google Drive export tasks show errors

**Causes:**
- Insufficient Drive storage
- GEE quota exceeded
- Asset too large

**Solutions:**
1. Free up Google Drive space
2. Wait 24 hours (quota resets)
3. Use client-side export for smaller datasets
4. Reduce AOI size

---

### Issue 4: Results seem incorrect

**Symptom:** Damage/flood detected in unexpected locations

**Causes:**
- Wet baseline (pre-event rain)
- Agricultural changes (harvesting, plowing)
- Urban development
- Sensor artifacts

**Solutions:**
1. Move Pre-date earlier (avoid recent rain)
2. Verify with Google Earth imagery
3. Increase T-threshold
4. Cross-validate with optical imagery

---

### Issue 5: Population estimates unrealistic

**Symptom:** Population numbers too high/low

**Causes:**
- Non-residential buildings included
- Wrong WorldPop region
- Missing building height data

**Solutions:**
1. Filter by building type if available
2. Verify area corresponds to residential zones
3. Download WSF3D height data
4. Apply ±40% uncertainty margin

---

## Performance Optimization Tips

### For Large Areas

1. **Divide and conquer:**
   - Split into 20-30 km² tiles
   - Process separately
   - Merge results in QGIS

2. **Selective module activation:**
   - Run Damage only first
   - Then Flood separately
   - Combine results afterward

3. **Use custom assets:**
   - Pre-filter buildings to residential only
   - Clip roads to main arteries
   - Upload to GEE

### For Slow Internet

1. **Reduce data transfer:**
   - Use Google Drive export (server-side)
   - Download during off-peak hours
   - Use compressed formats

2. **Optimize analysis:**
   - Minimize time series dates
   - Use coarser DEM (SRTM instead of NASADEM)
   - Disable density bubbles

---

# 12. Best Practices

## Pre-Analysis Checklist

- [ ] Verify event date accuracy
- [ ] Check Sentinel-1 availability for area
- [ ] Assess cloud-free optical imagery availability
- [ ] Identify appropriate building/road sources
- [ ] Define realistic AOI size (< 50 km²)
- [ ] Determine priority modules to run

## During Analysis

- [ ] Monitor progress bar
- [ ] Note any warning messages
- [ ] Check intermediate results in Layers panel
- [ ] Verify statistics seem reasonable
- [ ] Screenshot key findings

## Post-Analysis

- [ ] Export all relevant layers
- [ ] Document parameter settings used
- [ ] Cross-validate with optical imagery
- [ ] Calculate population estimates if needed
- [ ] Prepare summary report

## Validation Workflow

1. **Rapid assessment** (this tool)
   - Identify potential damage zones
   - Calculate approximate statistics
   - Generate priority maps

2. **Photo-interpretation** (HR imagery)
   - Validate damage locations
   - Assess damage severity
   - Identify false positives/negatives

3. **Field verification** (on-ground)
   - Visit high-priority areas
   - Collect ground truth data
   - Refine population estimates

4. **Report generation**
   - Combine all sources
   - Communicate uncertainties
   - Provide actionable recommendations

---

# 13. Use Cases and Examples

## Case Study 1: Post-Hurricane Assessment

**Scenario:** Category 4 hurricane made landfall on coastal city

**Workflow:**
1. Define AOI around affected city (30 km²)
2. Set Event-date = landfall date
3. Set Pre-date = 2 months before
4. Activate: Weather + Damage + Flood
5. Use Time Series for flood evolution
6. Export results within 10 minutes
7. Generate priority map for field teams

**Key outputs:**
- Damaged buildings: 2,847 (23%)
- Flooded area: 12.3 km²
- Affected population: ~18,500
- Prioritized zones for immediate response

---

## Case Study 2: Earthquake Damage Mapping

**Scenario:** Magnitude 7.2 earthquake in mountainous region

**Workflow:**
1. Define AOI around epicenter (40 km²)
2. Set Event-date = earthquake date
3. Set Pre-date = 1 month before
4. Activate: Damage + Landslide
5. Increase T-threshold to 3.0 (reduce noise)
6. Use custom building asset (local cadastre)
7. Cross-validate with seismic intensity map

**Key outputs:**
- Very high damage: 342 buildings
- Landslide zones: 8.7 km²
- Roads at risk: 23 km
- Logistic hub identified near heliport

---

## Case Study 3: Flood Monitoring

**Scenario:** Monsoon flooding over 2-week period

**Workflow:**
1. Define AOI along river basin (60 km²)
2. Enable Time Series mode
3. Set range = flood start to 2 weeks after
4. Activate: Flood + Weather only
5. Generate evolution graph
6. Identify peak flood extent
7. Track recession rate

**Key outputs:**
- Peak flood: 18.2 km² (Day 5)
- Recession: -2.1 km²/day
- Flooded infrastructure: 4 health facilities
- Estimated timeline to dry: 8 days

---

# 14. Known Limitations and Future Work

## Current Limitations

### Technical Constraints

1. **Spatial resolution:** 10m (Sentinel-1) insufficient for individual small buildings
2. **Temporal resolution:** 6-day revisit may miss short-duration events
3. **Computation limits:** Large areas (> 100 km²) require subdivision
4. **Export limits:** 5000 features max for client-side export

### Methodological Constraints

1. **SAR ambiguities:** Cannot distinguish damage types (collapse vs fire vs flood)
2. **Vegetation masking:** Dense canopy hides underlying damage/flooding
3. **Urban complexity:** Multi-story buildings, underground structures not detected
4. **Empirical thresholds:** T-threshold, susceptibility weights not universally optimal

### Data Constraints

1. **Building databases:** Variable quality, outdated in rapidly developing areas
2. **DEM accuracy:** 30m insufficient for micro-topography landslides
3. **Population data:** Statistical estimates, not census-based counts
4. **Weather data:** Coarse resolution misses localized phenomena

## Planned Improvements

### Short-term (2026)

- [ ] Integrate Sentinel-2 for damage type classification
- [ ] Add uncertainty quantification to all outputs
- [ ] Implement automated quality control checks
- [ ] Create standardized validation dataset
- [ ] Develop batch processing for multiple events

### Medium-term (2027)

- [ ] Machine learning damage classifier
- [ ] High-resolution SAR integration (ICEYE, Capella)
- [ ] Mobile field validation app
- [ ] Multi-language support
- [ ] Automated report generation

### Long-term (2028+)

- [ ] Near-real-time monitoring system
- [ ] Integration with UN/humanitarian dashboards
- [ ] Crowdsourced validation platform
- [ ] 3D damage visualization
- [ ] Climate scenario modeling

---

# 15. Contributing to the Project

## Ways to Contribute

### For Researchers

- **Validate results** in your study areas
- **Compare** with ground truth data
- **Publish** case studies using the tool
- **Share** parameter optimization findings
- **Propose** methodological improvements

### For Developers

- **Optimize** code performance
- **Add** new features
- **Write** unit tests
- **Improve** documentation
- **Translate** interface

### For Data Providers

- **Share** high-quality building datasets
- **Provide** validation imagery
- **Contribute** local DEM data
- **Add** regional infrastructure databases

### For End Users

- **Report** bugs and issues
- **Suggest** interface improvements
- **Share** use cases
- **Provide** feedback on accuracy
- **Recommend** features

## Contribution Guidelines

### Code Contributions

1. Follow Google JavaScript Style Guide
2. Comment complex algorithms
3. Test on multiple browsers
4. Document parameter changes
5. Update README if needed

### Documentation Contributions

1. Use clear, concise language
2. Provide examples
3. Include screenshots
4. Translate accurately
5. Maintain consistent formatting

### Data Contributions

1. Ensure proper licensing
2. Provide metadata
3. Document quality assessment
4. Share processing scripts
5. Attribute sources correctly

---

# 16. Support and Community

## Getting Help

### Official Resources

- **GitHub Issues:** [https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping/issues](https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping/issues)
- **Documentation:** This README (English/French)
- **Email:** renoux.fabrice@hotmail.fr

### Response Times

- **Bug reports:** 3-7 days
- **Feature requests:** Review monthly
- **General questions:** Best effort basis

**Note:** This is an academic project with limited support resources.

## Community Guidelines

### Be Respectful

- Professional communication
- Constructive criticism
- Acknowledge contributions
- Help newcomers

### Share Knowledge

- Document solutions
- Create tutorials
- Answer questions
- Contribute examples

### Give Credit

- Cite this tool in publications
- Acknowledge data sources
- Credit contributors
- Respect licenses

---

# 17. Legal and Ethical Considerations

## Disclaimer of Liability

This tool is provided "as is" without warranty. The author and AgroParisTech:

- Make no guarantees of accuracy
- Are not liable for decisions based on results
- Do not endorse operational use without validation
- Disclaim responsibility for data quality
- Are not responsible for third-party data licenses

## Ethical Use Guidelines

### DO:
- ✅ Use for research and education
- ✅ Validate results before decisions
- ✅ Communicate uncertainties clearly
- ✅ Attribute data sources properly
- ✅ Respect privacy and sovereignty

### DO NOT:
- ❌ Use as sole basis for life-safety decisions
- ❌ Claim results are ground truth
- ❌ Ignore validation requirements
- ❌ Violate data licenses
- ❌ Use for military targeting

## Data Privacy

- No personal data collected
- No user tracking
- No data sharing with third parties
- Google Drive exports = user's private storage
- Analysis results = user's exclusive access

## Academic Integrity

If using this tool for academic work:

1. **Cite properly** (see Citation section)
2. **Acknowledge limitations** in methodology
3. **Document** all parameters used
4. **Share** code/data when possible
5. **Validate** results independently

---

# 18. Version History

## Version 1.0.0 (March 2026)

**Initial release**

### Features
- Damage detection (PWTT algorithm)
- Flood detection (s1flood algorithm)
- Landslide susceptibility mapping
- Weather statistics module
- Time series flood analysis
- Client-side GeoJSON export
- Google Drive export (Shapefile + GeoTIFF)
- QGIS building comparison script
- QGIS population estimation model
- English and French documentation

### Known Issues
- Large areas (> 100 km²) may timeout
- Client-side export limited to 5000 features
- No batch processing capability
- Manual parameter tuning required

### Credits
- Damage detection: Based on Ballinger (2024)
- Flood detection: Based on DeVries et al. (2020)
- Landslide detection: Based on Handwerger et al. (2022)
- Building comparison: Inspired by Gonzales (2023)

---

# 19. Related Projects and Resources

## Similar Tools

### Global
- **UNOSAT Rapid Mapping:** [https://unitar.org/maps](https://unitar.org/maps)
- **Copernicus EMS:** [https://emergency.copernicus.eu/](https://emergency.copernicus.eu/)
- **NASA ARIA Damage Proxy Maps:** [https://aria.jpl.nasa.gov/](https://aria.jpl.nasa.gov/)

### SAR-based
- **Sentinel-1 Toolbox (SNAP):** [https://step.esa.int/main/toolboxes/snap/](https://step.esa.int/main/toolboxes/snap/)
- **PyRAT (Python Radar Tools):** [https://github.com/birgander2/PyRAT](https://github.com/birgander2/PyRAT)

### Flood-specific
- **Global Flood Database:** [https://global-flood-database.cloudtostreet.ai/](https://global-flood-database.cloudtostreet.ai/)
- **FloodMapper:** [https://github.com/cloudtostreet/floodmapper](https://github.com/cloudtostreet/floodmapper)

## Educational Resources

### SAR Remote Sensing
- **ESA SAR Training:** [https://eo-college.org/](https://eo-college.org/)
- **NASA ARSET:** [https://appliedsciences.nasa.gov/what-we-do/capacity-building/arset](https://appliedsciences.nasa.gov/what-we-do/capacity-building/arset)

### Google Earth Engine
- **GEE Tutorials:** [https://developers.google.com/earth-engine/tutorials](https://developers.google.com/earth-engine/tutorials)
- **Earth Engine Community:** [https://developers.google.com/earth-engine/tutorials/community/explore](https://developers.google.com/earth-engine/tutorials/community/explore)

### Disaster Response
- **MapAction:** [https://mapaction.org/](https://mapaction.org/)
- **HOT (Humanitarian OpenStreetMap Team):** [https://www.hotosm.org/](https://www.hotosm.org/)

---

# 20. Conclusion

## Summary

The Rapid Damage Detection Tool provides:

1. **Fast assessment** of disaster impacts using Sentinel-1 SAR
2. **Multi-hazard approach** (damage, floods, landslides)
3. **Open-source** implementation on Google Earth Engine
4. **Complementary tools** for quality assessment and population estimation
5. **Comprehensive documentation** for users and developers

## Target Audience

- **Emergency responders** for initial assessment
- **Humanitarian organizations** for resource allocation
- **Researchers** for methodological validation
- **Students** for disaster mapping education
- **Civil protection agencies** for rapid reconnaissance

## Key Strengths

- ✅ No installation required
- ✅ All-weather SAR data (cloud-independent)
- ✅ Rapid processing (5-15 minutes)
- ✅ Free and open-source
- ✅ Complementary validation tools

## Key Limitations

- ⚠️ Experimental tool (not operational)
- ⚠️ Requires expert validation
- ⚠️ Limited spatial resolution (10m)
- ⚠️ Area size constraints (< 100 km²)
- ⚠️ Statistical estimates (not census data)

## Future Vision

This tool represents a **first step** toward rapid, accessible disaster assessment. Future development will focus on:

- Enhanced accuracy through machine learning
- Integration with operational systems
- Real-time monitoring capabilities
- Community-validated datasets
- Multi-platform deployment

## Final Words

**Remember:** This tool provides a **framework for prioritization**, not definitive damage assessment. Always validate results through:

1. High-resolution imagery analysis
2. Field verification
3. Expert interpretation
4. Local knowledge integration

**Use responsibly. Validate thoroughly. Save lives.**

---

# 21. Quick Reference

## Essential Links

| Resource | URL |
|----------|-----|
| **Application** | [https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app) |
| **GitHub Repository** | [https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping](https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping) |
| **French Documentation** | [README.fr.md](README.fr.md) |
| **Report Issues** | [GitHub Issues](https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping/issues) |
| **Contact** | renoux.fabrice@hotmail.fr |

## Default Parameters

| Parameter | Default Value | Range | Purpose |
|-----------|---------------|-------|---------|
| Pre-interval | 180 days | 30-365 | Baseline image search window |
| Post-interval | 6 days | 1-28 | Post-event image search window |
| T-threshold | 2.4 | 2.0-5.0 | Damage detection sensitivity |
| Min slope (landslide) | 10° | 5-30° | Landslide slope threshold |
| Min curvature | 0.05 | 0.01-0.2 | Landslide curvature threshold |
| Max flood slope | 5° | 1-10° | Flood exclusion slope |

## File Naming Conventions

### Exports
```
RapidDamage_[ZONE_NAME]_[EVENT_DATE]/
├── Analysis_Summary.csv
├── Buildings_Damage.geojson / .shp
├── Roads_Damage.geojson / .shp
├── T_Statistic_Raster.tif
├── Flood_Extent.tif
└── Landslide_Susceptibility.tif
```

### Assets
```
projects/YOUR_PROJECT/assets/
├── aoi_[area_name]
├── buildings_[source]_[area]
└── roads_[source]_[area]
```

---

---

© 2026 Fabrice Renoux - AgroParisTech SILAT Master's Program - MIT License

**For questions:** renoux.fabrice@hotmail.fr  
**Application:** [https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app](https://rapiddamagedetection.projects.earthengine.app/view/rapid-damage-detection-app)  
**Repository:** [https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping](https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping)

---

**Acknowledgments**

This project builds upon the foundational work of Owen Ballinger (PWTT), Ben DeVries (s1flood), Alexander Handwerger (landslide heatmaps), and numerous open data contributors. Special thanks to the Google Earth Engine team, ESA Copernicus program, and the AgroParisTech SILAT teaching staff.

**Citation**

If you use this tool, please cite:
```
Renoux, F. (2026). Rapid Damage Detection Tool: Post-disaster assessment 
using Sentinel-1 SAR data on Google Earth Engine. GitHub repository: 
https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping
```

**Disclaimer**

This is an experimental academic tool. Results must be validated by experts before operational use. The author and AgroParisTech are not liable for decisions made based on this tool's outputs.

---

**Made with dedication for disaster response and humanitarian action**
