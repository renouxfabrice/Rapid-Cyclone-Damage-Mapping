// ============================================================
// RAPID DAMAGE DETECTION – APPLICATION VERSION
// ============================================================

var USE_CUSTOM_ASSETS = false;

var CUSTOM_AOI        = 'projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/AOI_whitehouse';
var CUSTOM_FOOTPRINTS = 'projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Building_OSM_whitehouse';
var CUSTOM_ROADS      = 'projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Road_OSM_whitehouse';

var PRE_DATE      = '2025-09-01';
var EVENT_DATE    = '2025-10-28';
var PRE_INTERVAL  = 180;
var POST_INTERVAL = 6;

var ENABLE_TIME_SERIES = false;
var TIME_SERIES_START = '';
var TIME_SERIES_END = '';

var ZONE_NAME = '';

var T_THRESHOLD     = 2.4;
var BUFFER_ROADS_M  = 6;
var ROAD_SEGMENT_M  = 100;

var MIN_SLOPE = 10;
var MIN_CURVATURE = 0.05;

var ZVV_THRESHOLD = -2.5;
var ZVH_THRESHOLD = -2.5;
var POW_THRESHOLD = 90;
var PIN_THRESHOLD = 25;

var MAX_SLOPE = 5;
var MIN_CONNECTIVITY = 8;
var SMOOTHING_RADIUS = 25;

var DEM_SOURCE = 'NASADEM';
var CUSTOM_DEM_ASSET = '';

var ENABLE_DAMAGE_DETECTION    = false;
var ENABLE_FLOOD_DETECTION     = false;
var ENABLE_LANDSLIDE_DETECTION = false;
var ENABLE_WEATHER_DATA        = true;

var CURRENT_AOI = null;
var LANDSLIDE_RUNOUT_ZONES;

// Global variables for exports
var fp, roadsStats, image, floods, landslides, permanentWater;
var footprintsAll, roadsAll;
var buildingsInFlood, roadsInFlood;
var buildingsInLandslide, roadsInLandslide;

// Variable pour tracker l'état du help panel
var helpPanelOpen = null;

// ============================================================
// RESULTS PANEL (replaces console for app)
// ============================================================
var resultsPanel = ui.Panel({
  style: {
    width: '380px',
    position: 'top-right',
    maxHeight: '90%',
    padding: '10px',
    backgroundColor: 'white',
    border: '2px solid #FF5722'
  }
});

var resultsPanelContent = ui.Panel();

// Toggle button for Results Panel - FLECHE NOIRE PERMANENTE
var resultsPanelCollapsed = false;
var resultsPanelToggleBtn = ui.Button({
  label: '▼',
  style: {
    padding: '2px 8px',
    margin: '0 0 0 8px',
    backgroundColor: 'white',
    color: 'black',
    fontWeight: 'bold',
    fontSize: '12px',
    border: 'none'
  }
});

resultsPanelToggleBtn.onClick(function() {
  resultsPanelCollapsed = !resultsPanelCollapsed;
  resultsPanelContent.style().set('shown', !resultsPanelCollapsed);
  resultsPanelToggleBtn.setLabel(resultsPanelCollapsed ? '▶' : '▼');
});

// Add toggle button to title
var titleRow = ui.Panel([
  ui.Label('📊 Analysis Results', {fontWeight: 'bold', fontSize: '16px', margin: '0'}),
  resultsPanelToggleBtn
], ui.Panel.Layout.Flow('horizontal'), {stretch: 'horizontal'});

resultsPanel.add(titleRow);
resultsPanel.add(resultsPanelContent);

// Helper function to add results
function addResult(text, style) {
  style = style || {};
  var defaultStyle = {fontSize: '11px', margin: '2px 0', whiteSpace: 'pre'};
  Object.keys(style).forEach(function(key) {
    defaultStyle[key] = style[key];
  });
  resultsPanelContent.add(ui.Label(text, defaultStyle));
}

function clearResults() {
  resultsPanelContent.clear();
}

function addSeparator() {
  addResult('━━━━━━━━━━━━━━━━━━━━━━━━━━━━', {color: '#888'});
}

function addChart(chartData, chartType, options) {
  var chart = ui.Chart(chartData, chartType, options);
  resultsPanelContent.add(chart);
}

// ============================================================
// CLIENT-SIDE DOWNLOAD (NO GEE ACCOUNT NEEDED)
// ============================================================
function downloadResultsClientSide() {
  if (!CURRENT_AOI) {
    addResult('⚠️ No analysis to download', {color: 'orange'});
    return;
  }
  
  var today = new Date().toISOString().split('T')[0];
  var prefix = (ZONE_NAME || 'Analysis') + '_' + today;
  
  addResult('📥 INSTANT DOWNLOAD (No account needed)', {
    fontWeight: 'bold', 
    color: '#4CAF50',
    fontSize: '13px'
  });
  addResult('Click the links below to download:', {fontSize: '11px', color: '#666'});
  addResult('');
  
  // 1. SUMMARY TEXT
  var summaryLines = [];
  summaryLines.push('RAPID DAMAGE DETECTION - ANALYSIS SUMMARY');
  summaryLines.push('=========================================');
  summaryLines.push('Zone: ' + ZONE_NAME);
  summaryLines.push('Date: ' + today);
  summaryLines.push('Pre-date: ' + PRE_DATE);
  summaryLines.push('Event date: ' + EVENT_DATE);
  summaryLines.push('');
  
  var widgets = resultsPanelContent.widgets();
  for (var i = 0; i < widgets.length(); i++) {
    var w = widgets.get(i);
    if (w.widgets) continue;
    var label = w.getValue ? w.getValue() : '';
    if (label) summaryLines.push(label);
  }
  
  var summaryText = summaryLines.join('\n');
  var summaryFC = ee.FeatureCollection([
    ee.Feature(null, {summary: summaryText})
  ]);
  
  var summaryUrl = summaryFC.getDownloadURL({
    format: 'CSV',
    filename: prefix + '_Summary'
  });
  
  var summaryLink = ui.Label({
    value: '📄 ' + prefix + '_Summary.csv',
    style: {color: 'blue', fontSize: '12px', margin: '4px 0 4px 8px', fontWeight: 'bold'},
    targetUrl: summaryUrl
  });
  resultsPanelContent.add(summaryLink);
  
  // 2. BUILDINGS DAMAGE
  if (ENABLE_DAMAGE_DETECTION && typeof fp !== 'undefined') {
    var buildingsUrl = fp.limit(5000).getDownloadURL({
      format: 'GeoJSON',
      filename: prefix + '_Buildings_Damage'
    });
    
    var buildingsLink = ui.Label({
      value: '🏠 ' + prefix + '_Buildings_Damage.geojson',
      style: {color: 'blue', fontSize: '12px', margin: '4px 0 4px 8px', fontWeight: 'bold'},
      targetUrl: buildingsUrl
    });
    resultsPanelContent.add(buildingsLink);
    
    fp.limit(5000).size().evaluate(function(count) {
      if (count >= 5000) {
        addResult('     ⚠️ Limited to 5000 features', {color: 'orange', fontSize: '9px'});
      } else {
        addResult('     ✓ ' + count + ' buildings', {color: '#666', fontSize: '9px'});
      }
    });
  }
  
  // 3. ROADS DAMAGE
  if (ENABLE_DAMAGE_DETECTION && typeof roadsStats !== 'undefined') {
    var roadsUrl = roadsStats.limit(5000).getDownloadURL({
      format: 'GeoJSON',
      filename: prefix + '_Roads_Damage'
    });
    
    var roadsLink = ui.Label({
      value: '🛣️ ' + prefix + '_Roads_Damage.geojson',
      style: {color: 'blue', fontSize: '12px', margin: '4px 0 4px 8px', fontWeight: 'bold'},
      targetUrl: roadsUrl
    });
    resultsPanelContent.add(roadsLink);
    
    roadsStats.limit(5000).size().evaluate(function(count) {
      if (count >= 5000) {
        addResult('     ⚠️ Limited to 5000 segments', {color: 'orange', fontSize: '9px'});
      } else {
        addResult('     ✓ ' + count + ' road segments', {color: '#666', fontSize: '9px'});
      }
    });
  }
  
  // 4. FLOODED BUILDINGS
  if (ENABLE_FLOOD_DETECTION && typeof buildingsInFlood !== 'undefined') {
    var floodBuildingsUrl = buildingsInFlood.limit(5000).getDownloadURL({
      format: 'GeoJSON',
      filename: prefix + '_Flooded_Buildings'
    });
    
    var floodBuildingsLink = ui.Label({
      value: '🌊 ' + prefix + '_Flooded_Buildings.geojson',
      style: {color: 'blue', fontSize: '12px', margin: '4px 0 4px 8px', fontWeight: 'bold'},
      targetUrl: floodBuildingsUrl
    });
    resultsPanelContent.add(floodBuildingsLink);
  }
  
  // 5. LANDSLIDE BUILDINGS
  if (ENABLE_LANDSLIDE_DETECTION && typeof buildingsInLandslide !== 'undefined') {
    var landslideBuildingsUrl = buildingsInLandslide.limit(5000).getDownloadURL({
      format: 'GeoJSON',
      filename: prefix + '_Landslide_Buildings'
    });
    
    var landslideBuildingsLink = ui.Label({
      value: '🏔️ ' + prefix + '_Landslide_Buildings.geojson',
      style: {color: 'blue', fontSize: '12px', margin: '4px 0 4px 8px', fontWeight: 'bold'},
      targetUrl: landslideBuildingsUrl
    });
    resultsPanelContent.add(landslideBuildingsLink);
  }
  
  addResult('');
  addResult('💡 Files open in QGIS, ArcGIS, or convert to Shapefile', {
    fontSize: '10px',
    color: '#666'
  });
}

// ============================================================
// GOOGLE DRIVE EXPORT FUNCTION
// ============================================================
function exportResults() {
  if (!CURRENT_AOI) {
    statusLabel.setValue('⚠️ No analysis to export');
    return;
  }
  
  var today = ee.Date(Date.now()).format('YYYY-MM-dd').getInfo();
  var folderName = 'RapidDamage_' + (ZONE_NAME || 'Analysis') + '_' + today;
  
  addSeparator();
  addResult('📦 STARTING GOOGLE DRIVE EXPORTS...', {fontWeight: 'bold', color: '#2196F3'});
  addResult('Folder: ' + folderName);
  addResult('⚠️ Requires Google Account + Click RUN in Tasks tab', {color: 'orange'});
  
  // Export text summary
  var summaryLines = [];
  summaryLines.push('RAPID DAMAGE DETECTION - ANALYSIS SUMMARY');
  summaryLines.push('=========================================');
  summaryLines.push('Zone: ' + ZONE_NAME);
  summaryLines.push('Date: ' + today);
  summaryLines.push('Pre-date: ' + PRE_DATE);
  summaryLines.push('Event date: ' + EVENT_DATE);
  summaryLines.push('');
  
  var widgets = resultsPanelContent.widgets();
  for (var i = 0; i < widgets.length(); i++) {
    var w = widgets.get(i);
    if (w.widgets) continue;
    var label = w.getValue ? w.getValue() : '';
    if (label) summaryLines.push(label);
  }
  
  var summaryText = summaryLines.join('\n');
  
  Export.table.toDrive({
    collection: ee.FeatureCollection([ee.Feature(null, {'summary': summaryText})]),
    description: 'Analysis_Summary',
    folder: folderName,
    fileFormat: 'CSV'
  });
  
  // Buildings damage
  if (ENABLE_DAMAGE_DETECTION && typeof fp !== 'undefined') {
    Export.table.toDrive({
      collection: fp,
      description: 'Buildings_Damage',
      folder: folderName,
      fileFormat: 'SHP'
    });
    
    // T-statistic raster
    if (typeof image !== 'undefined') {
      Export.image.toDrive({
        image: image.select('T_statistic'),
        description: 'T_Statistic_Raster',
        folder: folderName,
        scale: 10,
        region: CURRENT_AOI,
        maxPixels: 1e13,
        crs: 'EPSG:4326'
      });
    }
  }
  
  // Roads damage
  if (ENABLE_DAMAGE_DETECTION && typeof roadsStats !== 'undefined') {
    Export.table.toDrive({
      collection: roadsStats,
      description: 'Roads_Damage',
      folder: folderName,
      fileFormat: 'SHP'
    });
  }
  
  // Flood extent
  if (ENABLE_FLOOD_DETECTION && typeof floods !== 'undefined') {
    Export.image.toDrive({
      image: floods,
      description: 'Flood_Extent',
      folder: folderName,
      scale: 10,
      region: CURRENT_AOI,
      maxPixels: 1e13,
      crs: 'EPSG:4326'
    });
  }
  
  // Landslide susceptibility
  if (ENABLE_LANDSLIDE_DETECTION && typeof landslides !== 'undefined') {
    Export.image.toDrive({
      image: landslides,
      description: 'Landslide_Susceptibility',
      folder: folderName,
      scale: 30,
      region: CURRENT_AOI,
      maxPixels: 1e13,
      crs: 'EPSG:4326'
    });
    
    if (typeof LANDSLIDE_RUNOUT_ZONES !== 'undefined') {
      Export.image.toDrive({
        image: LANDSLIDE_RUNOUT_ZONES,
        description: 'Landslide_Runout_Zones',
        folder: folderName,
        scale: 30,
        region: CURRENT_AOI,
        maxPixels: 1e13,
        crs: 'EPSG:4326'
      });
    }
  }
  
  addResult('✅ Tasks queued! Click Tasks tab (top-right) → RUN each export');
  addSeparator();
  
  addSeparator();
  addSeparator();
  addResult('☁️ GOOGLE DRIVE EXPORT (Complete dataset + rasters)', {
    fontWeight: 'bold', 
    color: '#2196F3',
    fontSize: '13px'
  });
  addResult('Requires Google account', {fontSize: '10px', color: '#666'});
  addResult('');
  
  // Liste ce qui a été exporté
  addResult('📦 Queued for export:', {fontWeight: 'bold', fontSize: '11px'});
  addResult('  • Summary (CSV)', {fontSize: '10px'});
  
  if (ENABLE_DAMAGE_DETECTION && typeof fp !== 'undefined') {
    addResult('  • Buildings damage (Shapefile)', {fontSize: '10px'});
    addResult('  • Roads damage (Shapefile)', {fontSize: '10px'});
    if (typeof image !== 'undefined') {
      addResult('  • T-Statistic raster (GeoTIFF)', {fontSize: '10px', fontWeight: 'bold', color: '#FF9800'});
    }
  }
  
  if (ENABLE_FLOOD_DETECTION && typeof floods !== 'undefined') {
    addResult('  • Flood extent raster (GeoTIFF)', {fontSize: '10px', fontWeight: 'bold', color: '#FF9800'});
  }
  
  if (ENABLE_LANDSLIDE_DETECTION && typeof landslides !== 'undefined') {
    addResult('  • Landslide susceptibility (GeoTIFF)', {fontSize: '10px', fontWeight: 'bold', color: '#FF9800'});
    if (typeof LANDSLIDE_RUNOUT_ZONES !== 'undefined') {
      addResult('  • Landslide runout zones (GeoTIFF)', {fontSize: '10px', fontWeight: 'bold', color: '#FF9800'});
    }
  }
  
  addResult('');
  addResult('⚠️ ACTION REQUIRED:', {fontWeight: 'bold', color: '#FF9800', fontSize: '12px'});
  addResult('');
  
  var tasksInstruction1 = ui.Label({
    value: '👉 1. Click the "Tasks" tab (top-right orange icon)',
    style: {
      fontSize: '11px',
      color: '#000000',
      margin: '2px 0 2px 8px',
      fontWeight: 'bold'
    }
  });
  resultsPanelContent.add(tasksInstruction1);
  
  addResult('👉 2. Click "RUN" on each export task', {
    fontSize: '11px',
    margin: '2px 0 2px 8px',
    fontWeight: 'bold'
  });
  
  addResult('👉 3. Wait for completion (check Google Drive)', {
    fontSize: '11px',
    margin: '2px 0 2px 8px',
    fontWeight: 'bold'
  });
  
  addResult('');
  addResult('📁 Files will be saved to: Google Drive/' + folderName, {
    fontSize: '10px',
    color: '#666'
  });
  addSeparator();
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================
function expandDateWindowProgressively(s1Collection, targetStart, targetEnd, minImages, maxDays, label) {
  var count = s1Collection.filterDate(targetStart, targetEnd)
    .aggregate_array('orbitNumber_start').distinct().size().getInfo();
  
  if (count > 0) {
    return {start: targetStart, end: targetEnd, expanded: 0, count: count};
  }
  
  for (var afterDays = 1; afterDays <= maxDays; afterDays++) {
    var testEnd = ee.Date(targetEnd).advance(afterDays, 'day');
    var count2 = s1Collection.filterDate(targetStart, testEnd)
      .aggregate_array('orbitNumber_start').distinct().size();
    var countValue = count2.getInfo();
    if (countValue >= minImages) {
      return {start: targetStart, end: testEnd, expanded: afterDays, count: countValue};
    }
  }
  return {
    start: targetStart, 
    end: ee.Date(targetEnd).advance(maxDays, 'day'),
    expanded: 999,
    count: 0
  };
}

function segmentRoads(roads, geometry, segmentSize) {
  var bounds = geometry.bounds();
  var coords = ee.List(bounds.coordinates().get(0));
  var xMin = ee.Number(ee.List(coords.get(0)).get(0));
  var yMin = ee.Number(ee.List(coords.get(0)).get(1));
  var xMax = ee.Number(ee.List(coords.get(2)).get(0));
  var yMax = ee.Number(ee.List(coords.get(2)).get(1));
  var cellSize = ee.Number(segmentSize).divide(111320);
  var xSteps = xMax.subtract(xMin).divide(cellSize).ceil().int();
  var ySteps = yMax.subtract(yMin).divide(cellSize).ceil().int();
  
  var makeGrid = function(xStep) {
    var x = ee.Number(xStep);
    return ee.List.sequence(0, ySteps.subtract(1)).map(function(yStep) {
      var y = ee.Number(yStep);
      var x1 = xMin.add(x.multiply(cellSize));
      var y1 = yMin.add(y.multiply(cellSize));
      var x2 = x1.add(cellSize);
      var y2 = y1.add(cellSize);
      return ee.Feature(ee.Geometry.Rectangle([x1, y1, x2, y2]));
    });
  };
  
  var grid = ee.FeatureCollection(
    ee.List.sequence(0, xSteps.subtract(1)).map(makeGrid).flatten()
  );
  var roadUnion = roads.geometry().dissolve(1);
  var segments = grid.map(function(cell) {
    var intersection = roadUnion.intersection(cell.geometry(), 1);
    return ee.Feature(intersection);
  }).filter(ee.Filter.notNull(['.geo']));
  return segments;
}

function getDEM(geometry) {
  var dem;
  
  if (DEM_SOURCE === 'NASADEM') {
    dem = ee.Image('NASA/NASADEM_HGT/001').select('elevation');
  } else if (DEM_SOURCE === 'SRTM') {
    dem = ee.Image('USGS/SRTMGL1_003').select('elevation');
  } else if (DEM_SOURCE === 'ALOS') {
    dem = ee.ImageCollection('JAXA/ALOS/AW3D30/V3_2')
      .select('DSM').mosaic().rename('elevation');
  } else if (DEM_SOURCE === 'ASTER') {
    dem = ee.Image('NASA/ASTER_GED/AG100_003')
      .select('elevation').focal_mean(1, 'circle', 'meters');
  } else if (DEM_SOURCE === 'Custom') {
    if (CUSTOM_DEM_ASSET && CUSTOM_DEM_ASSET !== '') {
      dem = ee.Image(CUSTOM_DEM_ASSET);
      var bandNames = dem.bandNames();
      dem = ee.Algorithms.If(
        bandNames.contains('elevation'),
        dem.select('elevation'),
        dem.select(0).rename('elevation')
      );
      dem = ee.Image(dem);
    } else {
      addResult('⚠️ Custom DEM selected but no asset path provided. Using NASADEM.', {color: 'orange'});
      dem = ee.Image('NASA/NASADEM_HGT/001').select('elevation');
    }
  } else {
    addResult('⚠️ Unknown DEM source. Using NASADEM.', {color: 'orange'});
    dem = ee.Image('NASA/NASADEM_HGT/001').select('elevation');
  }
  
  return dem.clip(geometry);
}

function leeFilter(image) {
  var bandNames = image.bandNames().remove('angle');
  var hasBands = bandNames.size().gt(0);
  return ee.Algorithms.If(hasBands, function() {
    var eta = ee.Image.constant(1.0 / Math.sqrt(5));
    var one = ee.Image.constant(1);
    var stats = image.select(bandNames).reduceNeighborhood({
      reducer: ee.Reducer.mean().combine({reducer2: ee.Reducer.variance(), sharedInputs: true}),
      kernel: ee.Kernel.square(1, 'pixels'), optimization: 'window'
    });
    var zBar = stats.select(bandNames.map(function(b){return ee.String(b).cat('_mean');}));
    var varZ = stats.select(bandNames.map(function(b){return ee.String(b).cat('_variance');}));
    var varX = varZ.subtract(zBar.pow(2).multiply(eta.pow(2))).divide(one.add(eta.pow(2)));
    var newB = varX.divide(varZ.where(varX.divide(varZ).lt(0), 0));
    return image.addBands(
      one.subtract(newB).multiply(zBar.abs()).add(newB.multiply(image.select(bandNames))).rename(bandNames),
      null, true
    );
  }(), image);
}

function ttest(s1Col) {
  var edEE = ee.Date(EVENT_DATE);
  var pdEE = ee.Date(PRE_DATE);
  var pre = s1Col.filterDate(pdEE.advance(-PRE_INTERVAL, 'day'), pdEE);
  var post = s1Col.filterDate(edEE, edEE.advance(POST_INTERVAL, 'day'));
  var preCount = pre.size();
  var postCount = post.size();
  var hasData = preCount.gt(0).and(postCount.gt(0));
  
  return ee.Image(ee.Algorithms.If(hasData, function() {
    var preMean = pre.mean();
    var postMean = post.mean();
    var hasBands = preMean.bandNames().size().gt(0).and(postMean.bandNames().size().gt(0));
    
    return ee.Algorithms.If(hasBands, function() {
      var preN = ee.Number(pre.aggregate_array('orbitNumber_start').distinct().size());
      var postN = ee.Number(post.aggregate_array('orbitNumber_start').distinct().size());
      var pooledSd = pre.reduce(ee.Reducer.stdDev()).pow(2).multiply(preN.subtract(1))
        .add(post.reduce(ee.Reducer.stdDev()).pow(2).multiply(postN.subtract(1)))
        .divide(preN.add(postN).subtract(2)).sqrt();
      var denom = pooledSd.multiply(
        ee.Image.constant(1).divide(preN).add(ee.Image.constant(1).divide(postN)).sqrt()
      );
      return postMean.subtract(preMean).divide(denom).abs();
    }(), ee.Image.constant([0, 0]).rename(['VV', 'VH']));
  }(), ee.Image.constant([0, 0]).rename(['VV', 'VH'])));
}

function calcZscore(s1Col, baseStart, baseEnd, mode, direction) {
  var filtered = s1Col
    .filter(ee.Filter.eq('orbitProperties_pass', direction))
    .filter(ee.Filter.eq('instrumentMode', mode));
  
  var baseline = filtered.filterDate(baseStart, baseEnd);
  var count = baseline.size();
  var hasData = count.gt(0);
  
  return ee.ImageCollection(ee.Algorithms.If(hasData, function() {
    var basemean = baseline.mean();
    var basesd = baseline.reduce(ee.Reducer.stdDev());
    var hasBands = basemean.bandNames().size().gt(0);
    
    return ee.Algorithms.If(hasBands, function() {
      return filtered.map(function(img) {
        return img.subtract(basemean).divide(basesd)
          .set('system:time_start', img.get('system:time_start'));
      });
    }(), ee.List([]));
  }(), ee.List([])));
}

function mapFloods(z, zvvThd, zvhThd, powThd, pinThd, geometry) {
  var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first().clip(geometry);
  var worldcoverWater = worldcover.eq(80);
  
  var jrc = ee.ImageCollection("JRC/GSW1_4/MonthlyHistory").filterBounds(geometry);
  var jrcvalid = jrc.map(function(x) {return x.gt(0);}).sum();
  var jrcwat = jrc.map(function(x) {return x.eq(2);}).sum().divide(jrcvalid).multiply(100);
  var jrcmask = jrcvalid.gt(0);
  
  var ow = worldcoverWater;
  var inun = jrcwat.gte(ee.Image(pinThd)).and(jrcwat.lt(ee.Image(powThd)));
  
  var bandNames = z.bandNames();
  var hasVV = bandNames.contains('VV');
  var hasVH = bandNames.contains('VH');
  
  var vvflag = ee.Image(ee.Algorithms.If(hasVV, 
    z.select('VV').lte(ee.Image(zvvThd)), 
    ee.Image.constant(0)));
  var vhflag = ee.Image(ee.Algorithms.If(hasVH, 
    z.select('VH').lte(ee.Image(zvhThd)), 
    ee.Image.constant(0)));
  
  var floodOnly = ee.Image(0).add(vvflag).add(vhflag.multiply(2)).add(inun.multiply(10))
    .rename('flood_class').updateMask(jrcmask.and(ow.not())).clip(geometry);
  
  var permanentWater = ee.Image(20).rename('permanent_water')
    .updateMask(ow).clip(geometry);
  
  return {flood: floodOnly, water: permanentWater};
}

function detectLandslides(geometry, maxChange_raw) {
  var elevation = getDEM(geometry);
  var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first().clip(geometry);
  var waterMask = worldcover.neq(80);
  
  var precipStart = ee.Date(EVENT_DATE).advance(-30, 'day');
  var precipEnd = ee.Date(EVENT_DATE);
  var precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .select('precipitation')
    .filterDate(precipStart, precipEnd)
    .filterBounds(geometry)
    .sum().clip(geometry);
  var precipScore = precip.divide(300).clamp(0, 1).multiply(0.143);
  
  var slope = ee.Terrain.slope(elevation);
  var slopeScore = slope.divide(30).clamp(0, 1).multiply(0.128);
  
  var clay = ee.Image('projects/soilgrids-isric/clay_mean')
    .select('clay_0-5cm_mean').clip(geometry);
  var soilScore = clay.divide(100).multiply(0.123);
  
  var aspect = ee.Terrain.aspect(elevation);
  var northFacing = aspect.lte(45).or(aspect.gte(315));
  var aspectScore = northFacing.multiply(1.0).add(northFacing.not().multiply(0.5)).multiply(0.112);
  
  var smooth_curv = ee.Kernel.gaussian({radius: 60, sigma: 30, units: 'meters', normalize: true});
  var elevation_smooth = elevation.convolve(smooth_curv).resample("bilinear");
  var xyDemGrad = elevation_smooth.gradient().resample("bilinear");
  var xGradient = xyDemGrad.select('x').gradient().resample("bilinear");
  var yGradient = xyDemGrad.select('y').gradient().resample("bilinear");
  var curvature = xGradient.select('x').add(yGradient.select('y'));
  var curvatureScore = curvature.abs().divide(0.2).clamp(0, 1).multiply(0.1);
  
  var susceptibilityScore = precipScore
    .add(slopeScore)
    .add(soilScore)
    .add(aspectScore)
    .add(curvatureScore)
    .updateMask(waterMask);
  
  var mask_slope = slope.gte(MIN_SLOPE);
  var mask_curvature = curvature.gte(MIN_CURVATURE);
  var T_stat_landslide = maxChange_raw
    .updateMask(mask_slope)
    .updateMask(mask_curvature)
    .updateMask(waterMask);
  
  var landslide_levels = ee.Image(0)
    .where(susceptibilityScore.gte(0.3).and(T_stat_landslide.gte(T_THRESHOLD)).and(T_stat_landslide.lt(T_THRESHOLD + 1)), 1)
    .where(susceptibilityScore.gte(0.3).and(T_stat_landslide.gte(T_THRESHOLD + 1)).and(T_stat_landslide.lt(T_THRESHOLD + 2)), 2)
    .where(susceptibilityScore.gte(0.3).and(T_stat_landslide.gte(T_THRESHOLD + 2)), 3)
    .rename('landslide_level');
  
  var finalLandslides = landslide_levels.selfMask();
  
  var kernel = ee.Kernel.circle({radius: 100, units: 'meters'});
  var runoutZone = finalLandslides.gt(0).focal_max({kernel: kernel})
    .subtract(finalLandslides.gt(0)).selfMask().rename('runout_zone');
  
  LANDSLIDE_RUNOUT_ZONES = runoutZone;
  
  return finalLandslides;
}

function getWeatherStats(geometry, eventDate) {
  var startDate, endDate, numDays;
  
  if (ENABLE_TIME_SERIES) {
    startDate = ee.Date(TIME_SERIES_START);
    endDate = ee.Date(TIME_SERIES_END);
    numDays = endDate.difference(startDate, 'day').round().getInfo() + 1;
    
    var startStr = TIME_SERIES_START;
    var endStr = TIME_SERIES_END;
    addResult('🌦️ WEATHER CONDITIONS (' + startStr + ' to ' + endStr + ')');
  } else {
    startDate = ee.Date(PRE_DATE);
    endDate = ee.Date(EVENT_DATE).advance(3, 'day');
    numDays = endDate.difference(startDate, 'day').round().getInfo() + 1;
    
    var startStr = startDate.format('YYYY-MM-dd').getInfo();
    var endStr = endDate.format('YYYY-MM-dd').getInfo();
    addResult('🌦️ WEATHER CONDITIONS (' + startStr + ' to ' + endStr + ')');
  }
  
  var precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .select('precipitation')
    .filterDate(startDate, endDate.advance(1, 'day'))
    .filterBounds(geometry);
  
  var gldas = ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H')
    .select(['Wind_f_inst', 'Psurf_f_inst'])
    .filterDate(startDate, endDate.advance(1, 'day'))
    .filterBounds(geometry);
  
  var windSpeed = gldas.map(function(img) {
    var wind = img.select('Wind_f_inst').multiply(3.6);
    return img.addBands(wind.rename('wind_speed_kmh'));
  });
  
  var daysList = ee.List.sequence(0, numDays - 1);
  
  var dailyData = daysList.map(function(dayOffset) {
    var day = startDate.advance(ee.Number(dayOffset), 'day');
    var nextDay = day.advance(1, 'day');
    
    var dailyPrecip = precip.filterDate(day, nextDay).first();
    var precipValue = dailyPrecip.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geometry,
      scale: 5566,
      maxPixels: 1e13,
      bestEffort: true
    });
    
    var dailyWind = windSpeed.filterDate(day, nextDay);
    var windMean = dailyWind.select('wind_speed_kmh').mean().reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geometry,
      scale: 27830,
      maxPixels: 1e13,
      bestEffort: true
    });
    var windMax = dailyWind.select('wind_speed_kmh').max().reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geometry,
      scale: 27830,
      maxPixels: 1e13,
      bestEffort: true
    });
    
    var dailyPressure = gldas.filterDate(day, nextDay);
    var pressureMean = dailyPressure.select('Psurf_f_inst').mean().reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geometry,
      scale: 27830,
      maxPixels: 1e13,
      bestEffort: true
    });
    var pressureMin = dailyPressure.select('Psurf_f_inst').min().reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: geometry,
      scale: 27830,
      maxPixels: 1e13,
      bestEffort: true
    });
    
    return ee.Feature(null, {
      'date': day.format('MM/dd'),
      'precipitation': precipValue.get('precipitation'),
      'wind_mean': windMean.get('wind_speed_kmh'),
      'wind_max': windMax.get('wind_speed_kmh'),
      'pressure_mean': ee.Number(pressureMean.get('Psurf_f_inst')).divide(100),
      'pressure_min': ee.Number(pressureMin.get('Psurf_f_inst')).divide(100)
    });
  });
  
  var dailyFC = ee.FeatureCollection(dailyData);
  
  dailyFC.evaluate(function(fc) {
    if (!fc || !fc.features) {
      addResult('⚠️ Weather data unavailable', {color: 'orange'});
      return;
    }
    
    var eventDateStr = ee.Date(eventDate).format('YYYY-MM-dd').getInfo();
    
    var precipData = [['Date', 'Precipitation (mm)', {role: 'style'}]];
    var windPressureData = [['Date', 'Wind Mean (km/h)', 'Wind Max (km/h)', 'Pressure Mean (hPa)', 'Pressure Min (hPa)']];
    
    var totalPrecip = 0;
    var maxPrecip = 0;
    var maxPrecipDate = '';
    var maxWind = 0;
    var maxWindDate = '';
    var minPressure = 9999;
    var minPressureDate = '';
    
    fc.features.forEach(function(feature) {
      var props = feature.properties;
      var date = props.date || '';
      
      var p = props.precipitation || 0;
      totalPrecip += p;
      if (p > maxPrecip) {
        maxPrecip = p;
        maxPrecipDate = date;
      }
      var isEventDay = date === eventDateStr;
      var barColor = isEventDay ? '#FF6347' : '#1E90FF';
      precipData.push([date, p, barColor]);
      
      var windMean = props.wind_mean || 0;
      var windMax = props.wind_max || 0;
      var pressureMean = props.pressure_mean || 0;
      var pressureMin = props.pressure_min || 0;
      
      if (windMax > maxWind) {
        maxWind = windMax;
        maxWindDate = date;
      }
      if (pressureMin < minPressure && pressureMin > 0) {
        minPressure = pressureMin;
        minPressureDate = date;
      }
      
      windPressureData.push([date, windMean, windMax, pressureMean, pressureMin]);
    });
    
    var precipChartTitle = ENABLE_TIME_SERIES ? 
      'Daily Precipitation (' + TIME_SERIES_START + ' to ' + TIME_SERIES_END + ')' :
      'Daily Precipitation (' + startDate.format('YYYY-MM-dd').getInfo() + ' to ' + endDate.format('YYYY-MM-dd').getInfo() + ')';
    
    var precipChart = ui.Chart(precipData, 'ColumnChart', {
      title: precipChartTitle,
      vAxis: {title: 'Precipitation (mm)'},
      hAxis: {title: 'Date', slantedText: true, slantedTextAngle: 30},
      legend: {position: 'none'},
      height: 300,
      width: 360,
      bar: {groupWidth: '75%'}
    });
    resultsPanelContent.add(precipChart);
    
    var windChartTitle = ENABLE_TIME_SERIES ?
      'Wind & Pressure (' + TIME_SERIES_START + ' to ' + TIME_SERIES_END + ')' :
      'Wind & Pressure (' + startDate.format('YYYY-MM-dd').getInfo() + ' to ' + endDate.format('YYYY-MM-dd').getInfo() + ')';
    
    var windPressureChart = ui.Chart(windPressureData, 'LineChart', {
      title: windChartTitle,
      series: {
        0: {targetAxisIndex: 0, color: '#90EE90', lineWidth: 2},
        1: {targetAxisIndex: 0, color: '#228B22', lineWidth: 3, lineDashStyle: [2, 2]},
        2: {targetAxisIndex: 1, color: '#FFD700', lineWidth: 2},
        3: {targetAxisIndex: 1, color: '#FF6347', lineWidth: 3, lineDashStyle: [2, 2]}
      },
      vAxes: {
        0: {title: 'Wind Speed (km/h)', textStyle: {color: '#228B22'}},
        1: {title: 'Pressure (hPa)', textStyle: {color: '#FFD700'}}
      },
      hAxis: {title: 'Date', slantedText: true, slantedTextAngle: 30},
      interpolateNulls: true,
      pointSize: 5,
      height: 350,
      width: 360
    });
    resultsPanelContent.add(windPressureChart);
    
    addResult('Cumulative rainfall: ' + totalPrecip.toFixed(1) + ' mm');
    addResult('Max daily rainfall: ' + maxPrecip.toFixed(1) + ' mm (' + maxPrecipDate + ')');
    addResult('Max wind gust: ' + maxWind.toFixed(1) + ' km/h (' + maxWindDate + ')');
    addResult('Min pressure: ' + minPressure.toFixed(1) + ' hPa (' + minPressureDate + ')');
  });
}

// ============================================================
// MAIN ANALYSIS FUNCTION - DÉBUT
// ============================================================
function runAnalysis(aoi, footprints, roads) {
  var geometry = aoi.geometry();
  Map.centerObject(geometry, 12);
  
  var floodPostDate = '';
  var timeSeriesFloodLayers = [];
  
  var steps = [];
  if (ENABLE_DAMAGE_DETECTION) steps.push('Damage');
  if (ENABLE_FLOOD_DETECTION) steps.push('Flood');
  if (ENABLE_LANDSLIDE_DETECTION) steps.push('Landslide');
  if (ENABLE_WEATHER_DATA) steps.push('Weather');
  var totalSteps = steps.length;
  var currentStep = 0;
  
  function updateProgress(message) {
    currentStep++;
    var bar = '';
    var filled = Math.floor((currentStep / totalSteps) * 20);
    for (var i = 0; i < 20; i++) {
      bar += i < filled ? '█' : '░';
    }
    var percent = Math.floor((currentStep / totalSteps) * 100);
    progressLabel.setValue(bar + ' ' + percent + '% - ' + message);
  }
  
  addSeparator();
  var aoiAreaKm2 = geometry.area(1).divide(1000000);
  addResult('🎯 AOI area: ' + aoiAreaKm2.getInfo().toFixed(2) + ' km²');
  
  var worldpop = ee.ImageCollection('WorldPop/GP/100m/pop')
    .filterBounds(geometry)
    .sort('system:time_start', false)
    .first();
  
  var popStats = worldpop.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometry,
    scale: 100,
    maxPixels: 1e13,
    bestEffort: true
  });
  
  var population = ee.Number(popStats.get('population')).round().getInfo();
  var popYear = ee.Date(worldpop.get('system:time_start')).get('year').getInfo();
  
  addResult('👥 Population (WorldPop ' + popYear + '): ' + population.toLocaleString());
  
  try {
    var ports = ee.FeatureCollection('projects/rapiddamagedetection/assets/upply-seaports');
    var portsCount = ports.filterBounds(geometry).size().getInfo();
    addResult('⚓ Ports: ' + portsCount);
  } catch(e) {
    addResult('⚓ Ports: N/A');
  }
  
  try {
    var airports = ee.FeatureCollection('projects/rapiddamagedetection/assets/ourairports');
    var airportsInAOI = airports.filterBounds(geometry);
    
    var heliports = airportsInAOI.filter(ee.Filter.eq('type', 'heliport')).size().getInfo();
    var smallAirports = airportsInAOI.filter(ee.Filter.eq('type', 'small_airport')).size().getInfo();
    var mediumAirports = airportsInAOI.filter(ee.Filter.eq('type', 'medium_airport')).size().getInfo();
    var largeAirports = airportsInAOI.filter(ee.Filter.eq('type', 'large_airport')).size().getInfo();
    var totalAirports = heliports + smallAirports + mediumAirports + largeAirports;
    
    addResult('✈️ Airports: ' + totalAirports);
    if (largeAirports > 0) addResult('  ├─ Large: ' + largeAirports);
    if (mediumAirports > 0) addResult('  ├─ Medium: ' + mediumAirports);
    if (smallAirports > 0) addResult('  ├─ Small: ' + smallAirports);
    if (heliports > 0) addResult('  └─ Heliports: ' + heliports);
  } catch(e) {
    addResult('✈️ Airports: N/A');
  }
  
  try {
    var healthNodes = ee.FeatureCollection('projects/sat-io/open-datasets/health-site-node');
    var healthWays = ee.FeatureCollection('projects/sat-io/open-datasets/health-site-way');
    var healthCount = healthNodes.filterBounds(geometry).size().getInfo() + 
                      healthWays.filterBounds(geometry).size().getInfo();
    addResult('🏥 Health facilities: ' + healthCount);
  } catch(e) {
    addResult('🏥 Health facilities: N/A');
  }
  addSeparator();
  
  if (ENABLE_WEATHER_DATA) {
    updateProgress('Loading weather data...');
    getWeatherStats(geometry, EVENT_DATE);
  }
  
  addSeparator();
  
  var diagDamagePreCount = 0;
  var diagDamagePostCount = 0;
  var diagDamageExpansion = '';
  var diagFloodExpansion = '';
  
  var floodAreaKm2, maxChange_raw;
  footprintsAll = footprints;
  roadsAll = roads;
  
  if (ENABLE_DAMAGE_DETECTION || ENABLE_LANDSLIDE_DETECTION) {
    if (ENABLE_DAMAGE_DETECTION) updateProgress('Analyzing building damage...');
    else updateProgress('Preparing landslide analysis...');
    
    var s1All = ee.ImageCollection('COPERNICUS/S1_GRD_FLOAT')
      .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
      .filter(ee.Filter.eq('instrumentMode', 'IW')).filterBounds(geometry);
    
    diagDamagePreCount = s1All.filterDate(
      ee.Date(PRE_DATE).advance(-PRE_INTERVAL, 'day'), 
      ee.Date(PRE_DATE)
    ).aggregate_array('orbitNumber_start').distinct().size().getInfo();
    
    var postWindow = expandDateWindowProgressively(
      s1All,
      ee.Date(EVENT_DATE),
      ee.Date(EVENT_DATE).advance(POST_INTERVAL, 'day'),
      1, 6, 'Damage POST'
    );
    
    diagDamagePostCount = postWindow.count || 0;
    
    if (postWindow.expanded > 0 && postWindow.expanded < 999) {
      diagDamageExpansion = ' (+' + postWindow.expanded + ' days, ' + diagDamagePostCount + ' images)';
    } else if (postWindow.expanded === 0) {
      diagDamageExpansion = ' (' + diagDamagePostCount + ' images found)';
    } else {
      diagDamageExpansion = ' (insufficient data)';
    }
    
    var orbits = s1All.filterDate(postWindow.start, postWindow.end)
      .aggregate_array('relativeOrbitNumber_start').distinct();
    
    var orbitsSize = orbits.size().getInfo();
    
    if (orbitsSize === 0) {
      addSeparator();
      addResult('❌ ERROR: No Sentinel-1 images found in POST window', {color: 'red', fontWeight: 'bold'});
      addResult('Event date: ' + EVENT_DATE);
      addResult('POST interval: ' + POST_INTERVAL + ' days');
      addSeparator();
      addResult('💡 SOLUTION: Increase "Post" interval to 7-14 days', {color: 'orange'});
      addResult('   (Sentinel-1 revisit time is ~6 days)');
      addSeparator();
      
      statusLabel.setValue('❌ No POST images - increase Post interval');
      progressLabel.setValue('');
      return;
    }
    
    var ttestImages = ee.ImageCollection(orbits.map(function(orbit) {
        var s1 = ee.ImageCollection('COPERNICUS/S1_GRD_FLOAT')
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
          .filter(ee.Filter.eq('instrumentMode', 'IW'))
          .filter(ee.Filter.eq('relativeOrbitNumber_start', orbit)).filterBounds(geometry)
          .map(leeFilter).map(function(img){ return img.log(); });
        
        var count = s1.size();
        var s1WithBands = ee.ImageCollection(ee.Algorithms.If(count.gt(0), function() {
          var firstImg = s1.first();
          var bandNames = firstImg.bandNames();
          var hasVV = bandNames.contains('VV');
          var hasVH = bandNames.contains('VH');
          var hasBothBands = ee.Algorithms.If(
            hasVV,
            hasVH,
            ee.Number(0)
          );
          return ee.Algorithms.If(hasBothBands, 
            s1.select(['VV', 'VH']),
            ee.List([]));
        }(), ee.List([])));
        
        return ttest(s1WithBands);
      }));
      
      var tMax = ttestImages.max();
      var hasBands = tMax.bandNames().size().gt(0);
      
      maxChange_raw = ee.Image(ee.Algorithms.If(hasBands, function() {
        var bandNames = tMax.bandNames();
        var hasVV = bandNames.contains('VV');
        var hasVH = bandNames.contains('VH');
        var hasBothBands = ee.Algorithms.If(
          hasVV,
          hasVH,
          ee.Number(0)
        );
        
        return ee.Algorithms.If(hasBothBands, function() {
          return tMax.select('VV').max(tMax.select('VH')).rename('max_change')
            .focalMedian(10, 'gaussian', 'meters').clip(geometry);
        }(), ee.Image.constant(0).rename('max_change').clip(geometry));
      }(), ee.Image.constant(0).rename('max_change').clip(geometry)));
    
    if (ENABLE_DAMAGE_DETECTION) {
      var T_stat_urban = maxChange_raw
        .add(maxChange_raw.convolve(ee.Kernel.circle(50, 'meters', true)))
        .add(maxChange_raw.convolve(ee.Kernel.circle(100, 'meters', true)))
        .add(maxChange_raw.convolve(ee.Kernel.circle(150, 'meters', true)))
        .divide(4).rename('T_statistic');
      image = T_stat_urban.addBands(maxChange_raw.gt(T_THRESHOLD).rename('damage')).toFloat().clip(geometry);
      var T_stat_roads = maxChange_raw
        .add(maxChange_raw.convolve(ee.Kernel.circle(50, 'meters', true)))
        .add(maxChange_raw.convolve(ee.Kernel.circle(100, 'meters', true)))
        .add(maxChange_raw.convolve(ee.Kernel.circle(150, 'meters', true)))
        .divide(4).rename('T_statistic');
      
      fp = image.select('T_statistic').reduceRegions({
        collection: footprints.filterBounds(geometry), reducer: ee.Reducer.mean(), scale: 10, tileScale: 16
      }).map(function(f) {
        var T = ee.Number(ee.Algorithms.If(ee.Algorithms.IsEqual(f.get('mean'), null), 0, f.get('mean')));
        var confidence = ee.Algorithms.If(T.gt(5), 'Very High',
          ee.Algorithms.If(T.gt(4), 'High', ee.Algorithms.If(T.gt(3), 'Moderate', 'Low')));
        return f.set({'T_statistic': T, 'damage': T.gt(T_THRESHOLD).int(), 'confidence': confidence});
      });
      
      var roadsFiltered = roads.filterBounds(geometry).map(function(f){ return f.intersection(geometry, 1); });
      var roadsSegmented = segmentRoads(roadsFiltered, geometry, ROAD_SEGMENT_M);
      
      roadsStats = T_stat_roads.reduceRegions({
        collection: roadsSegmented.map(function(f){ return f.buffer(BUFFER_ROADS_M); }),
        reducer: ee.Reducer.max(), scale: 10, tileScale: 16
      }).map(function(f) {
        var T = ee.Number(ee.Algorithms.If(ee.Algorithms.IsEqual(f.get('max'), null), 0, f.get('max')));
        return f.set({'T_statistic': T, 'damage': T.gt(T_THRESHOLD).int()});
      });
    }
  }
  
  if (ENABLE_FLOOD_DETECTION) {
    updateProgress('Detecting flood extent...');
    
    var baseStart, baseEnd;
    
    if (ENABLE_TIME_SERIES) {
      baseEnd = ee.Date(TIME_SERIES_START).advance(-1, 'day');
      baseStart = baseEnd.advance(-PRE_INTERVAL, 'day');
      addResult('📊 BASELINE (time series mode): ' + baseStart.format('YYYY-MM-dd').getInfo() + ' to ' + baseEnd.format('YYYY-MM-dd').getInfo());
    } else {
      baseStart = ee.Date(PRE_DATE).advance(-PRE_INTERVAL, 'day');
      baseEnd = ee.Date(PRE_DATE);
    }
    
    var s1Flood = ee.ImageCollection('COPERNICUS/S1_GRD')
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
      .filter(ee.Filter.eq("instrumentMode", "IW")).filterBounds(geometry);
    
    if (ENABLE_TIME_SERIES) {
      addSeparator();
      addResult('📅 TIME SERIES FLOOD ANALYSIS', {fontWeight: 'bold'});
      addResult('Period: ' + TIME_SERIES_START + ' to ' + TIME_SERIES_END);
      
      var tsStart = ee.Date(TIME_SERIES_START);
      var tsEnd = ee.Date(TIME_SERIES_END);
      
      var s1DatesFlood = s1Flood.filterDate(tsStart, tsEnd)
        .select('VV')
        .map(function(img) {
          return ee.Feature(null, {
            'date': img.date().format('YYYY-MM-dd'),
            'timestamp': img.date().millis()
          });
        })
        .distinct('date')
        .aggregate_array('date');
      
      var datesListFlood = s1DatesFlood.getInfo();
      addResult('Found ' + datesListFlood.length + ' Sentinel-1 dates for flood analysis');
      
      var s1FloodAll = s1Flood.filterDate(baseStart.advance(-PRE_INTERVAL, 'day'), tsEnd.advance(1, 'day'));
      var z_asc = calcZscore(s1FloodAll, baseStart, baseEnd, 'IW', 'ASCENDING');
      var z_dsc = calcZscore(s1FloodAll, baseStart, baseEnd, 'IW', 'DESCENDING');
      var zAll = ee.ImageCollection(z_asc.merge(z_dsc)).sort('system:time_start');
      
      var elevation = getDEM(geometry);
      var slope = ee.Terrain.slope(elevation);
      var worldcoverPostProcess = ee.ImageCollection('ESA/WorldCover/v200').first().clip(geometry);
      var permanentWaterMask = worldcoverPostProcess.neq(80);
      
      var floodLayers = [];
      for (var d = 0; d < datesListFlood.length; d++) {
        var dateStr = datesListFlood[d];
        var currentDate = ee.Date(dateStr);
        var nextDate = currentDate.advance(1, 'day');
        
        var zTarget = zAll.filterDate(currentDate, nextDate);
        var zCount = zTarget.size().getInfo();
        
        if (zCount > 0) {
          var z = zTarget.mosaic().clip(geometry);
          var floodResult = mapFloods(z, ZVV_THRESHOLD, ZVH_THRESHOLD, POW_THRESHOLD, PIN_THRESHOLD, geometry);
          var floodLayer = floodResult.flood;
          
          var s1ForDate = s1Flood.filterDate(currentDate, nextDate).first();
          var orbitPass = s1ForDate.get('orbitProperties_pass').getInfo();
          
          floodLayer = floodLayer.updateMask(slope.lt(MAX_SLOPE));
          var connectedPixels = floodLayer.connectedPixelCount();
          floodLayer = floodLayer.updateMask(connectedPixels.gte(MIN_CONNECTIVITY));
          floodLayer = floodLayer.focal_median(SMOOTHING_RADIUS, 'circle', 'meters');
          floodLayer = floodLayer.updateMask(permanentWaterMask);
          
          floodLayers.push({date: dateStr, layer: floodLayer, orbit: orbitPass});
        }
      }
      
      for (var i = 0; i < floodLayers.length; i++) {
        var orbitLetter = floodLayers[i].orbit === 'ASCENDING' ? '(A)' : '(D)';
        var layerName = '🌊 Flood | ' + floodLayers[i].date + ' ' + orbitLetter;
        timeSeriesFloodLayers.push({
          layer: floodLayers[i].layer,
          name: layerName,
          visible: i === floodLayers.length - 1
        });
      }
      
      if (floodLayers.length > 1) {
        var floodAreasData = [['Date', 'Ascending images', 'Descending images']];
        
        for (var i = 0; i < floodLayers.length; i++) {
          var currentDateStr = floodLayers[i].date;
          var currentDate = ee.Date(currentDateStr);
          var nextDate = currentDate.advance(1, 'day');
          
          var s1ForDate = s1Flood.filterDate(currentDate, nextDate).first();
          var orbitPass = s1ForDate.get('orbitProperties_pass').getInfo();
          
          var floodMaskDate = floodLayers[i].layer.gt(0);
          var floodAreaDate = floodMaskDate.multiply(ee.Image.pixelArea()).reduceRegion({
            reducer: ee.Reducer.sum(), 
            geometry: geometry, 
            scale: 10, 
            maxPixels: 1e13
          });
          var areaKm2 = ee.Number(floodAreaDate.get('flood_class')).divide(1e6).getInfo();
          
          if (orbitPass === 'ASCENDING') {
            floodAreasData.push([currentDateStr, parseFloat(areaKm2.toFixed(3)), null]);
          } else {
            floodAreasData.push([currentDateStr, null, parseFloat(areaKm2.toFixed(3))]);
          }
        }
        
        var floodAreaChart = ui.Chart(floodAreasData, 'ColumnChart', {
          title: 'Flood Extent Evolution (' + TIME_SERIES_START + ' to ' + TIME_SERIES_END + ')',
          hAxis: {title: 'Date', slantedText: true, slantedTextAngle: 30},
          vAxis: {title: 'Flooded Area (km²)'},
          series: {
            0: {color: '#87CEEB'},
            1: {color: '#0066FF'}
          },
          legend: {position: 'right'},
          height: 300,
          width: 360,
          bar: {groupWidth: '75%'}
        });
        resultsPanelContent.add(floodAreaChart);
        
        var firstFloodArea = floodAreasData[1] ? parseFloat(floodAreasData[1][1] || floodAreasData[1][2] || 0) : 0;
        var firstDate = floodAreasData[1] ? floodAreasData[1][0] : '';
        
        if (firstFloodArea > 0.5) {
          addSeparator();
          addResult('⚠️ WARNING: Baseline appears wet!', {color: 'orange', fontWeight: 'bold'});
          addResult('First date (' + firstDate + ') shows ' + firstFloodArea.toFixed(2) + ' km² already flooded');
          addResult('💡 SUGGESTION: Move PRE_DATE earlier to ensure dry baseline');
          var suggestedDate = ee.Date(TIME_SERIES_START).advance(-30, 'day').format('YYYY-MM-dd').getInfo();
          addResult('   Recommended PRE_DATE: ' + suggestedDate);
          addSeparator();
        }
      }
      
      if (floodLayers.length > 0) {
        var eventDateMs = ee.Date(EVENT_DATE).millis().getInfo();
        var selectedIdx = -1;
        
        for (var fi = 0; fi < floodLayers.length; fi++) {
          var dateMs = ee.Date(floodLayers[fi].date).millis().getInfo();
          if (dateMs >= eventDateMs) {
            selectedIdx = fi;
            break;
          }
        }
        
        if (selectedIdx === -1) {
          selectedIdx = floodLayers.length - 1;
          addResult('⚠️ No image found after EVENT_DATE, using last available: ' + floodLayers[selectedIdx].date, {color: 'orange'});
        }
        
        floods = floodLayers[selectedIdx].layer;
        floodPostDate = floodLayers[selectedIdx].date;
        var floodResultSelected = mapFloods(
          zAll.filterDate(ee.Date(floodPostDate), ee.Date(floodPostDate).advance(1, 'day')).mosaic(), 
          ZVV_THRESHOLD, ZVH_THRESHOLD, POW_THRESHOLD, PIN_THRESHOLD, geometry
        );
        permanentWater = floodResultSelected.water;
        diagFloodExpansion = ' (' + floodLayers.length + ' dates analyzed, using ' + floodPostDate + ' for stats)';
      } else {
        floods = ee.Image.constant(0).rename('flood_class').clip(geometry);
        permanentWater = ee.Image.constant(0).rename('permanent_water').clip(geometry);
        diagFloodExpansion = ' (no data in time series)';
        floodPostDate = 'No data';
      }
      
    } else {
      var eventWindow = expandDateWindowProgressively(
        s1Flood,
        ee.Date(EVENT_DATE),
        ee.Date(EVENT_DATE).advance(POST_INTERVAL, 'day'),
        1, 3, 'Flood EVENT'
      );
      
      if (eventWindow.expanded !== 0) {
        diagFloodExpansion = ' (adjusted +' + eventWindow.expanded + ' days, ' + (eventWindow.count || 0) + ' images)';
      } else {
        diagFloodExpansion = ' (' + (eventWindow.count || 0) + ' images found)';
      }
      
      var s1FloodAll = s1Flood.filterDate(
        baseStart.advance(-PRE_INTERVAL, 'day'), 
        eventWindow.end.advance(1, 'day')
      );
      
      var z_asc = calcZscore(s1FloodAll, baseStart, baseEnd, 'IW', 'ASCENDING');
      var z_dsc = calcZscore(s1FloodAll, baseStart, baseEnd, 'IW', 'DESCENDING');
      var zAll = ee.ImageCollection(z_asc.merge(z_dsc)).sort('system:time_start');
      var zTarget = zAll.filterDate(eventWindow.start, eventWindow.end);
      
      var firstPostImage = zTarget.first();
      floodPostDate = ee.Date(firstPostImage.get('system:time_start')).format('YYYY-MM-dd').getInfo();
      
      var z = zTarget.mosaic().clip(geometry);
      var floodResult = mapFloods(z, ZVV_THRESHOLD, ZVH_THRESHOLD, POW_THRESHOLD, PIN_THRESHOLD, geometry);
      floods = floodResult.flood;
      permanentWater = floodResult.water;
      
      var elevation = getDEM(geometry);
      var slope = ee.Terrain.slope(elevation);
      floods = floods.updateMask(slope.lt(MAX_SLOPE));
      
      var connectedPixels = floods.connectedPixelCount();
      floods = floods.updateMask(connectedPixels.gte(MIN_CONNECTIVITY));
      
      floods = floods.focal_median(SMOOTHING_RADIUS, 'circle', 'meters');
      
      var worldcoverPostProcess = ee.ImageCollection('ESA/WorldCover/v200').first().clip(geometry);
      var permanentWaterMask = worldcoverPostProcess.neq(80);
      floods = floods.updateMask(permanentWaterMask);
    }
    
    var floodMask = floods.gt(0);
    var floodArea = floodMask.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(), geometry: geometry, scale: 10, maxPixels: 1e13
    });
    floodAreaKm2 = ee.Number(floodArea.get('flood_class')).divide(1e6);
  }
  
  if (ENABLE_LANDSLIDE_DETECTION) {
    updateProgress('Analyzing landslide susceptibility...');
    landslides = detectLandslides(geometry, maxChange_raw);
  }
  
  if (ENABLE_DAMAGE_DETECTION && typeof fp !== 'undefined') {
    addSeparator();
    addResult('📊 DAMAGE STATISTICS', {fontWeight: 'bold', fontSize: '13px'});
    addSeparator();
    addResult('🏠 BUILDINGS', {fontWeight: 'bold'});
    
    try {
      var buildingsIntact = fp.filter(ee.Filter.eq('damage', 0)).size().getInfo();
      var buildingsDamaged = fp.filter(ee.Filter.eq('damage', 1)).size().getInfo();
      var buildingsTotal = buildingsIntact + buildingsDamaged;
      
      addResult('Buildings damaged: ' + buildingsDamaged);
      addResult('Buildings intact: ' + buildingsIntact);
      addResult('Total buildings in AOI: ' + buildingsTotal);
      if (buildingsTotal > 0) {
        var buildingDamagePercent = ((buildingsDamaged / buildingsTotal) * 100).toFixed(1);
        addResult('  → ' + buildingDamagePercent + '% of buildings damaged');
      }
      addResult('');
      addResult('Damage severity (T-threshold=' + T_THRESHOLD + '):');
      
      var veryHighThreshold = T_THRESHOLD + 2;
      var highMin = T_THRESHOLD + 1;
      
      var buildingsVeryHigh = fp.filter(ee.Filter.gte('T_statistic', veryHighThreshold)).size().getInfo();
      var buildingsHigh = fp.filter(ee.Filter.and(
        ee.Filter.gte('T_statistic', highMin),
        ee.Filter.lt('T_statistic', veryHighThreshold)
      )).size().getInfo();
      var buildingsModerate = fp.filter(ee.Filter.and(
        ee.Filter.gte('T_statistic', T_THRESHOLD),
        ee.Filter.lt('T_statistic', highMin)
      )).size().getInfo();
      
      addResult('  ├─ Very High (T≥' + veryHighThreshold + '): ' + buildingsVeryHigh);
      addResult('  ├─ High (T=' + highMin + '-' + (veryHighThreshold - 0.1).toFixed(1) + '): ' + buildingsHigh);
      addResult('  └─ Moderate (T=' + T_THRESHOLD + '-' + (highMin - 0.1).toFixed(1) + '): ' + buildingsModerate);
    } catch(e) {
      addResult('⚠️ Buildings statistics: Network timeout (too many buildings)', {color: 'orange'});
      addResult('   Stats not available but buildings layers are displayed');
    }
    
    addSeparator();
    addResult('🛣️ ROADS', {fontWeight: 'bold'});
    
    if (typeof roadsStats !== 'undefined') {
      try {
        var roadsIntact = roadsStats.filter(ee.Filter.eq('damage', 0));
        var roadsDamaged = roadsStats.filter(ee.Filter.eq('damage', 1));
        var roadsIntactCount = roadsIntact.size().getInfo();
        var roadsDamagedCount = roadsDamaged.size().getInfo();
        var roadsTotal = roadsIntactCount + roadsDamagedCount;
        
        addResult('Road segments damaged: ' + roadsDamagedCount);
        addResult('Road segments intact: ' + roadsIntactCount);
        addResult('Total road segments in AOI: ' + roadsTotal);
        
        var lengthIntact = (roadsIntactCount * ROAD_SEGMENT_M / 1000).toFixed(1);
        var lengthDamaged = (roadsDamagedCount * ROAD_SEGMENT_M / 1000).toFixed(1);
        var lengthTotal = (roadsTotal * ROAD_SEGMENT_M / 1000).toFixed(1);
        addResult('  → ~' + lengthDamaged + ' km of roads damaged (out of ~' + lengthTotal + ' km total)');
        
        var damageData = [
          ['Category', 'Count', {role: 'style'}],
          ['Buildings Intact', buildingsIntact, '#00CC44'],
          ['Buildings Damaged', buildingsDamaged, '#FF6600'],
          ['  Very High', buildingsVeryHigh, '#CC0000'],
          ['  High', buildingsHigh, '#FF4444'],
          ['  Moderate', buildingsModerate, '#FF8844'],
          ['Roads Intact (×100m)', roadsIntactCount, '#00CC44'],
          ['Roads Damaged (×100m)', roadsDamagedCount, '#FF2222']
        ];
        
        var damageChart = ui.Chart(damageData, 'ColumnChart', {
          title: 'Damage Detection Summary',
          hAxis: {title: 'Category'},
          vAxis: {title: 'Count'},
          legend: {position: 'none'},
          height: 300,
          width: 360
        });
        resultsPanelContent.add(damageChart);
      } catch(e) {
        addResult('⚠️ Roads statistics: Network timeout (too many roads)', {color: 'orange'});
        addResult('   Stats not available but roads layers are displayed');
      }
    }
  }
  
  if (ENABLE_FLOOD_DETECTION && typeof floods !== 'undefined') {
      addSeparator();
      addResult('🌊 FLOOD STATISTICS', {fontWeight: 'bold', fontSize: '13px'});
      addResult('Flooded area (km²): ' + floodAreaKm2.getInfo().toFixed(3));
      addSeparator();
      addResult('🌊 FLOODED LAND COVER (' + floodPostDate + ')', {fontWeight: 'bold'});
      
      var floodMask = floods.gt(0);
      var worldcover = ee.ImageCollection('ESA/WorldCover/v200').first().clip(geometry);
      var classNames = {
        10: 'Tree cover', 20: 'Shrubland', 30: 'Grassland', 40: 'Cropland',
        50: 'Built-up', 60: 'Bare / sparse vegetation', 70: 'Snow and ice',
        80: 'Permanent water bodies', 90: 'Herbaceous wetland', 95: 'Mangroves', 100: 'Moss and lichen'
      };
      
      var totalFloodedArea = floodMask.multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(), 
        geometry: geometry, 
        scale: 10, 
        maxPixels: 1e13, 
        bestEffort: true
      }).get('flood_class');
      
      var totalFloodedAreaValue = ee.Number(totalFloodedArea).getInfo();
      
      var landCoverResults = {};
      [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100].forEach(function(classValue) {
        var classMask = worldcover.eq(classValue);
        var floodedClassMask = classMask.and(floodMask);
        var floodedClassArea = floodedClassMask.multiply(ee.Image.pixelArea());
        
        var areaSum = floodedClassArea.reduceRegion({
          reducer: ee.Reducer.sum(), 
          geometry: geometry, 
          scale: 10, 
          maxPixels: 1e13, 
          bestEffort: true
        }).get('Map');
        
        var areaSumValue = ee.Number(areaSum).getInfo();
        if (areaSumValue > 0) {
          var areaKm2 = areaSumValue / 1000000;
          var areaM2 = areaSumValue;
          var percentage = (areaSumValue / totalFloodedAreaValue) * 100;
          landCoverResults[classValue] = {area: areaKm2, percent: percentage};
          
          var displayArea = areaKm2 >= 0.01 ? 
            areaKm2.toFixed(3) + ' km²' : 
            areaM2.toFixed(0) + ' m²';
          
          addResult('  ' + classNames[classValue] + ': ' + displayArea + ' (' + percentage.toFixed(1) + '%)');
        }
      });
      
      var totalPercent = 0;
      Object.keys(landCoverResults).forEach(function(classValue) {
        totalPercent += landCoverResults[classValue].percent;
      });
      addResult('  ──────────────────────────────');
      addResult('  TOTAL: ' + (totalFloodedAreaValue / 1000000).toFixed(3) + ' km² (' + totalPercent.toFixed(1) + '%)');
      
      var chartData = [['Land Cover', 'Area (km²)', {role: 'style'}]];
      var colorMap = {
        'Tree cover': '#228B22',
        'Shrubland': '#90EE90',
        'Grassland': '#ADFF2F',
        'Cropland': '#FFD700',
        'Built-up': '#DC143C',
        'Bare / sparse vegetation': '#D2B48C',
        'Permanent water bodies': '#1E90FF'
      };
      
      Object.keys(landCoverResults).forEach(function(classValue) {
        var className = classNames[classValue];
        var color = colorMap[className] || '#888888';
        chartData.push([className, parseFloat(landCoverResults[classValue].area.toFixed(3)), color]);
      });
      
      if (chartData.length > 1) {
        var floodChart = ui.Chart(chartData, 'ColumnChart', {
          title: 'Flooded Land Cover (' + floodPostDate + ')',
          hAxis: {title: 'Land Cover Type', slantedText: true, slantedTextAngle: 45},
          vAxis: {title: 'Area (km²)'},
          legend: {position: 'none'},
          height: 300,
          width: 360
        });
        resultsPanelContent.add(floodChart);
      }
      
      addSeparator();
      addResult('🌊 BUILDINGS & ROADS IN FLOODED AREAS', {fontWeight: 'bold'});
      
      var buildingsForFlood = footprintsAll || footprints;
      var buildingsInAOI = buildingsForFlood.filterBounds(geometry);
      
      var floodVectors = floods.gt(0).selfMask()
        .reduceToVectors({
          geometry: geometry,
          scale: 10,
          maxPixels: 1e13,
          bestEffort: true,
          geometryType: 'polygon'
        });
      
      var buildingsFlooded = buildingsInAOI.filterBounds(floodVectors.geometry());
      
      var buildingsFloodedCount = buildingsFlooded.size().getInfo();
      var buildingsTotalCount = buildingsInAOI.size().getInfo();
      var buildingsNotFlooded = buildingsTotalCount - buildingsFloodedCount;
      
      addResult('Buildings in flooded areas: ' + buildingsFloodedCount);
      addResult('Buildings not flooded: ' + buildingsNotFlooded);
      addResult('Total buildings in AOI: ' + buildingsTotalCount);
      if (buildingsTotalCount > 0) {
        var buildingFloodPercent = ((buildingsFloodedCount / buildingsTotalCount) * 100).toFixed(1);
        addResult('  → ' + buildingFloodPercent + '% of buildings affected');
      }
      
      var roadsForFlood = roadsAll || roads;
      var roadsFiltered = roadsForFlood.filterBounds(geometry).map(function(f){ return f.intersection(geometry, 1); });
      var roadsSegmented = segmentRoads(roadsFiltered, geometry, ROAD_SEGMENT_M);
      
      var roadsFlooded = roadsSegmented.filterBounds(floodVectors.geometry());
      
      var roadsFloodedCount = roadsFlooded.size().getInfo();
      var roadsTotalCount = roadsSegmented.size().getInfo();
      var roadsNotFlooded = roadsTotalCount - roadsFloodedCount;
      
      addResult('Road segments in flooded areas: ' + roadsFloodedCount);
      addResult('Road segments not flooded: ' + roadsNotFlooded);
      addResult('Total road segments in AOI: ' + roadsTotalCount);
      
      var floodedRoadLength = (roadsFloodedCount * ROAD_SEGMENT_M / 1000).toFixed(1);
      var totalRoadLength = (roadsTotalCount * ROAD_SEGMENT_M / 1000).toFixed(1);
      addResult('  → ~' + floodedRoadLength + ' km of roads flooded (out of ~' + totalRoadLength + ' km total)');
      
      buildingsInFlood = buildingsFlooded;
      roadsInFlood = roadsFlooded;
  }
  
  if (ENABLE_LANDSLIDE_DETECTION && typeof landslides !== 'undefined') {
    addSeparator();
    addResult('🏔️ LANDSLIDE STATISTICS', {fontWeight: 'bold', fontSize: '13px'});
    var landslidesImg = ee.Image(landslides);
    var hasData = landslidesImg.bandNames().size().gt(0);
    
    if (hasData.getInfo()) {
      var landslideArea = landslidesImg.multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(), geometry: geometry, scale: 30, maxPixels: 1e13
      });
      var totalArea = ee.Number(landslideArea.values().get(0)).divide(1e6).getInfo();
      
      var moderate = landslidesImg.eq(1).multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(), geometry: geometry, scale: 30, maxPixels: 1e13
      });
      var high = landslidesImg.eq(2).multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(), geometry: geometry, scale: 30, maxPixels: 1e13
      });
      var veryHigh = landslidesImg.eq(3).multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(), geometry: geometry, scale: 30, maxPixels: 1e13
      });
      
      var modArea = ee.Number(moderate.values().get(0)).divide(1e6).getInfo();
      var highArea = ee.Number(high.values().get(0)).divide(1e6).getInfo();
      var vhArea = ee.Number(veryHigh.values().get(0)).divide(1e6).getInfo();
      
      addResult('Total landslide susceptibility area: ' + totalArea.toFixed(3) + ' km²');
      addResult('  ├─ Moderate probability (T=3-4): ' + modArea.toFixed(3) + ' km²');
      addResult('  ├─ High probability (T=4-5): ' + highArea.toFixed(3) + ' km²');
      addResult('  └─ Very high probability (T>5): ' + vhArea.toFixed(3) + ' km²');
      addResult('');
      addResult('Exposure zones (100m downslope):');
      if (typeof LANDSLIDE_RUNOUT_ZONES !== 'undefined') {
        var runoutArea = LANDSLIDE_RUNOUT_ZONES.multiply(ee.Image.pixelArea()).reduceRegion({
          reducer: ee.Reducer.sum(), geometry: geometry, scale: 30, maxPixels: 1e13
        });
        var runoutKm2 = ee.Number(runoutArea.values().get(0)).divide(1e6).getInfo();
        addResult('  Area: ' + runoutKm2.toFixed(3) + ' km²');
      }

      var landslideChartData = [
        ['Probability', 'Area (km²)', {role: 'style'}],
        ['Moderate (T=3-4)', parseFloat(modArea.toFixed(3)), '#D2B48C'],
        ['High (T=4-5)', parseFloat(highArea.toFixed(3)), '#A0522D'],
        ['Very High (T>5)', parseFloat(vhArea.toFixed(3)), '#8B4513']
      ];
      
      var landslideChart = ui.Chart(landslideChartData, 'ColumnChart', {
        title: 'Landslide Susceptibility by Probability Level',
        hAxis: {title: 'Probability Level'},
        vAxis: {title: 'Area (km²)'},
        legend: {position: 'none'},
        height: 300,
        width: 360
      });
      resultsPanelContent.add(landslideChart);
      
      if (typeof footprintsAll !== 'undefined' && typeof roadsAll !== 'undefined') {
        addResult('');
        addResult('🏔️ BUILDINGS & ROADS IN LANDSLIDE ZONES', {fontWeight: 'bold'});
        
        var landslideVectors = landslides.gt(0).selfMask()
          .reduceToVectors({
            geometry: geometry,
            scale: 30,
            maxPixels: 1e13,
            bestEffort: true,
            geometryType: 'polygon'
          });
        
        var buildingsForLandslide = footprintsAll || footprints;
        var buildingsInAOI = buildingsForLandslide.filterBounds(geometry);
        buildingsInLandslide = buildingsInAOI.filterBounds(landslideVectors.geometry());
        
        var buildingsLandslideCount = buildingsInLandslide.size().getInfo();
        var buildingsTotalCount = buildingsInAOI.size().getInfo();
        var buildingsNotInLandslide = buildingsTotalCount - buildingsLandslideCount;
        
        addResult('Buildings in landslide zones: ' + buildingsLandslideCount);
        addResult('Buildings not in landslide zones: ' + buildingsNotInLandslide);
        addResult('Total buildings in AOI: ' + buildingsTotalCount);
        if (buildingsTotalCount > 0) {
          var buildingLandslidePercent = ((buildingsLandslideCount / buildingsTotalCount) * 100).toFixed(1);
          addResult('  → ' + buildingLandslidePercent + '% of buildings in landslide zones');
        }
        
        var roadsForLandslide = roadsAll || roads;
        var roadsFiltered = roadsForLandslide.filterBounds(geometry).map(function(f){ return f.intersection(geometry, 1); });
        var roadsSegmented = segmentRoads(roadsFiltered, geometry, ROAD_SEGMENT_M);
        roadsInLandslide = roadsSegmented.filterBounds(landslideVectors.geometry());
        
        var roadsLandslideCount = roadsInLandslide.size().getInfo();
        var roadsTotalCount = roadsSegmented.size().getInfo();
        var roadsNotInLandslide = roadsTotalCount - roadsLandslideCount;
        
        addResult('Road segments in landslide zones: ' + roadsLandslideCount);
        addResult('Road segments not in landslide zones: ' + roadsNotInLandslide);
        addResult('Total road segments in AOI: ' + roadsTotalCount);
        
        var landslidedRoadLength = (roadsLandslideCount * ROAD_SEGMENT_M / 1000).toFixed(1);
        var totalRoadLength = (roadsTotalCount * ROAD_SEGMENT_M / 1000).toFixed(1);
        addResult('  → ~' + landslidedRoadLength + ' km of roads in landslide zones (out of ~' + totalRoadLength + ' km total)');
      }
    } else {
      addResult('No landslide susceptibility detected');
    }
  }
  
  addSeparator();
  addResult('🔍 ANALYSIS DIAGNOSTICS', {fontWeight: 'bold'});
  
  if (ENABLE_DAMAGE_DETECTION || ENABLE_FLOOD_DETECTION || ENABLE_LANDSLIDE_DETECTION) {
    addResult('Sentinel-1 imagery:');
    addResult('  PRE images: ' + diagDamagePreCount);
    addResult('  POST images:' + diagDamageExpansion);
    
    if (ENABLE_FLOOD_DETECTION && diagFloodExpansion !== diagDamageExpansion) {
      addResult('  Flood event window:' + diagFloodExpansion);
    }
  }
  
  addSeparator();
  progressLabel.setValue('████████████████████ 100% - Complete!');
  
  Map.setOptions('SATELLITE');
  
  var layersToRemove = [];
  for (var i = 0; i < Map.layers().length(); i++) {
    var layer = Map.layers().get(i);
    var layerName = layer.getName();
    if (layerName !== 'AOI boundary') {
      layersToRemove.push(layer);
    }
  }
  for (var j = 0; j < layersToRemove.length; j++) {
    Map.remove(layersToRemove[j]);
  }
  
  Map.addLayer(ee.FeatureCollection([ee.Feature(geometry)]).style({
    color: 'FFA500', fillColor: 'FFFF0033', width: 3
  }), {}, '🔶 AOI boundary');
  
  // ============================================================
  // DAMAGE LAYERS - PROTECTION COMPLÈTE
  // ============================================================
  if (ENABLE_DAMAGE_DETECTION && typeof image !== 'undefined' && typeof fp !== 'undefined') {
    Map.addLayer(image.select('T_statistic').updateMask(image.select('T_statistic').gt(T_THRESHOLD)),
      {min: T_THRESHOLD, max: T_THRESHOLD+2, palette: ['FFFF00','FF6600','FF0000','880088']}, 
      '💥 Damage | T-statistic raster', false, 0.7);
    
    Map.addLayer(fp.filter(ee.Filter.eq('damage', 0)).style({color: '00CC44', fillColor: '00000000', width: 1}), 
      {}, '💥 Damage | Buildings intact', true);
    Map.addLayer(fp.filter(ee.Filter.eq('confidence', 'Very High')).style({color: 'CC0000', fillColor: '00000000', width: 2}), 
      {}, '💥 Damage | Buildings Very High', true);
    Map.addLayer(fp.filter(ee.Filter.eq('confidence', 'High')).style({color: 'FF4444', fillColor: '00000000', width: 2}), 
      {}, '💥 Damage | Buildings High', true);
    Map.addLayer(fp.filter(ee.Filter.eq('confidence', 'Moderate')).style({color: 'FF8844', fillColor: '00000000', width: 1}), 
      {}, '💥 Damage | Buildings Moderate', true);
    
    if (typeof roadsStats !== 'undefined') {
      Map.addLayer(roadsStats.filter(ee.Filter.eq('damage', 0)).style({color: '00CC44', width: 2}), 
        {}, '💥 Damage | Roads intact', true);
      Map.addLayer(roadsStats.filter(ee.Filter.eq('damage', 1)).style({color: 'FF2222', width: 3}), 
        {}, '💥 Damage | Roads damaged', true);
    }
    
    var damaged = fp.filter(ee.Filter.neq('damage', 0));
    
    var damageRaster = damaged.reduceToImage({
      properties: ['damage'],
      reducer: ee.Reducer.count()
    }).reproject({
      crs: 'EPSG:4326',
      scale: 100
    }).clip(geometry);
    
    var damagePoints = damageRaster.sample({
      region: geometry,
      scale: 100,
      geometries: true
    }).filter(ee.Filter.gt('count', 0));
    
    var bubbles = damagePoints.map(function(point) {
      var count = ee.Number(point.get('count'));
      var radius = count.sqrt().multiply(25);
      return point.buffer(radius);
    });
    
    Map.addLayer(bubbles.style({
      color: 'FF0000',
      fillColor: 'FF000044',
      width: 2
    }), {}, '💥 Damage | Density bubbles', false, 0.7);
    
    try {
      var damagePointsWithCount = damagePoints.filter(ee.Filter.gt('count', 0));
      var pointCount = damagePointsWithCount.size().getInfo();
      
      if (pointCount > 0) {
        var totalDamageCount = damagePointsWithCount.aggregate_sum('count');
        
        var weightedCoords = damagePointsWithCount.map(function(point) {
          var count = ee.Number(point.get('count'));
          var coords = point.geometry().coordinates();
          var lon = ee.Number(coords.get(0)).multiply(count);
          var lat = ee.Number(coords.get(1)).multiply(count);
          return ee.Feature(null, {'wlon': lon, 'wlat': lat});
        });
        
        var sumWLon = ee.Number(weightedCoords.aggregate_sum('wlon'));
        var sumWLat = ee.Number(weightedCoords.aggregate_sum('wlat'));
        var baryLon = sumWLon.divide(totalDamageCount);
        var baryLat = sumWLat.divide(totalDamageCount);
        var damageCentroid = ee.Geometry.Point([baryLon, baryLat]);
        
        try {
          var entryPointsList = [];
          
          try {
            var ports = ee.FeatureCollection('projects/rapiddamagedetection/assets/upply-seaports');
            var portsInAOI = ports.filterBounds(geometry);
            var portCount = portsInAOI.size().getInfo();
            if (portCount > 0) {
              var portCentroid = portsInAOI.geometry().centroid();
              entryPointsList.push(portCentroid);
              addResult('⚓ Found ' + portCount + ' port(s) in AOI');
            }
          } catch(e) {}
          
          try {
            var airports = ee.FeatureCollection('projects/rapiddamagedetection/assets/ourairports');
            var airportsInAOI = airports.filterBounds(geometry);
            var airportCount = airportsInAOI.size().getInfo();
            
            if (airportCount > 0) {
              var airportCentroid = airportsInAOI.geometry().centroid();
              entryPointsList.push(airportCentroid);
              addResult('✈️ Found ' + airportCount + ' airport(s) in AOI');
            }
          } catch(e) {}
          
          var hubPoint;
          
          if (entryPointsList.length > 0) {
            var coordsList = [];
            for (var ep = 0; ep < entryPointsList.length; ep++) {
              var coords = entryPointsList[ep].coordinates().getInfo();
              coordsList.push(coords);
            }
            
            var entryGeom = ee.Geometry.MultiPoint(coordsList).centroid();
            var entryCoords = entryGeom.coordinates();
            var entryLon = ee.Number(entryCoords.get(0));
            var entryLat = ee.Number(entryCoords.get(1));
            
            var hubLon = entryLon.multiply(0.7).add(baryLon.multiply(0.3));
            var hubLat = entryLat.multiply(0.7).add(baryLat.multiply(0.3));
            hubPoint = ee.Geometry.Point([hubLon, hubLat]);
            
            addResult('🎯 Logistic hub (weighted by entry points):');
            addResult('   Coordinates: ' + hubPoint.coordinates().getInfo());
          } else {
            hubPoint = damageCentroid;
            addResult('🎯 Logistic hub (damage centroid):');
            addResult('   Coordinates: ' + hubPoint.coordinates().getInfo());
          }
          
          if (typeof roadsStats !== 'undefined') {
            var nearestRoad = roadsStats.map(function(road) {
              return road.set('dist_to_hub', road.distance(hubPoint, 10));
            }).sort('dist_to_hub').first();
            
            var minDist = ee.Number(nearestRoad.get('dist_to_hub')).getInfo();
            
            if (minDist <= 10) {
              hubPoint = nearestRoad.geometry().nearestPoint(hubPoint);
              addResult('   Projected on road (distance: ' + minDist.toFixed(1) + 'm)');
            }
          }
          
          Map.addLayer(ee.FeatureCollection([ee.Feature(hubPoint)]).style({
            color: '9C27B0',
            fillColor: '9C27B0',
            pointSize: 6,
            pointShape: 'circle',
            width: 2
          }), {}, '🎯 Logistic hub', true);
          
        } catch(e) {
          addResult('⚠️ Entry points/hub error: ' + e, {color: 'orange'});
        }
      }
    } catch(e) {
      addResult('⚠️ Could not calculate logistic hub: ' + e, {color: 'orange'});
    }
  }
  
  // ============================================================
  // FLOOD LAYERS - PROTECTION COMPLÈTE
  // ============================================================
  if (ENABLE_FLOOD_DETECTION && typeof floods !== 'undefined' && typeof permanentWater !== 'undefined') {
    var floodPalette = [
      '#00BFFF','#1E90FF','#0000FF',
      '#000000','#000000','#000000','#000000','#000000','#000000',
      '#87CEEB','#4169E1','#4682B4','#000080'
    ];
    
    Map.addLayer(floods.updateMask(floods.gt(0)), 
      {min:1, max:13, palette:floodPalette}, 
      ENABLE_TIME_SERIES ? '🌊 Flood | Extent (analysis)' : '🌊 Flood | Extent', 
      !ENABLE_TIME_SERIES,
      0.7);
    
    if (ENABLE_TIME_SERIES) {
      for (var tsIdx = 0; tsIdx < timeSeriesFloodLayers.length; tsIdx++) {
        var tsLayer = timeSeriesFloodLayers[tsIdx];
        Map.addLayer(tsLayer.layer.updateMask(tsLayer.layer.gt(0)), 
          {min:1, max:13, palette:floodPalette}, 
          tsLayer.name, 
          tsLayer.visible, 
          0.7);
      }
    }
    
    Map.addLayer(permanentWater.updateMask(permanentWater.eq(20)),
      {palette: ['#ADD8E6']}, '🌊 Flood | Permanent water', false, 0.5);
    
    if (typeof buildingsInFlood !== 'undefined' && typeof fp !== 'undefined') {
      var floodedIds = buildingsInFlood.aggregate_array('system:index');
      var allFloodedBuildings = fp.filter(ee.Filter.inList('system:index', floodedIds));
      
      Map.addLayer(allFloodedBuildings.style({
        color: '0066FF',
        fillColor: '0066FF66',
        width: 2
      }), {}, '🌊 Flood | Flooded buildings', true);
    }
    
    if (typeof roadsInFlood !== 'undefined') {
      Map.addLayer(roadsInFlood.map(function(f) { 
          return f.buffer(BUFFER_ROADS_M); 
        }).style({color: '0066FF', fillColor: '00000000', width: 3}), 
        {}, '🌊 Flood | Flooded roads', true);
    }
  }
  
  // ============================================================
  // LANDSLIDE LAYERS - PROTECTION COMPLÈTE
  // ============================================================
  if (ENABLE_LANDSLIDE_DETECTION && typeof landslides !== 'undefined') {
    var landslidesImg = ee.Image(landslides);
    
    Map.addLayer(landslidesImg.selfMask(),
      {min: 1, max: 3, palette: ['#D2B48C', '#A0522D', '#8B4513']}, 
      '🏔️ Landslide | Susceptibility', true, 0.7);
      
    if (typeof LANDSLIDE_RUNOUT_ZONES !== 'undefined') {
      Map.addLayer(LANDSLIDE_RUNOUT_ZONES,
        {palette: ['#D2B48C']},
        '🏔️ Landslide | Exposure zones', false, 0.4);
    }
    
    if (typeof buildingsInLandslide !== 'undefined' && typeof fp !== 'undefined') {
      var landslideIds = buildingsInLandslide.aggregate_array('system:index');
      var allLandslideBuildings = fp.filter(ee.Filter.inList('system:index', landslideIds));
      
      Map.addLayer(allLandslideBuildings.style({
        color: '#8B4513',
        fillColor: '#8B451366',
        width: 2
      }), {}, '🏔️ Landslide | Buildings at risk', true);
    }
    
    if (typeof roadsInLandslide !== 'undefined') {
      Map.addLayer(roadsInLandslide.map(function(f) { 
        return f.buffer(BUFFER_ROADS_M); 
      }).style({
        color: '#8B4513',
        fillColor: '00000000',
        width: 3
      }), {}, '🏔️ Landslide | Roads at risk', true);
    }
  }
  
  // ============================================================
  // INFRASTRUCTURE LAYERS
  // ============================================================
  try {
    var airports = ee.FeatureCollection('projects/rapiddamagedetection/assets/ourairports');
    var airportsInAOI = airports.filterBounds(geometry);
    
    var largeAirports = airportsInAOI.filter(ee.Filter.eq('type', 'large_airport'));
    Map.addLayer(largeAirports.style({
      color: '0033CC',
      fillColor: '0033CC99',
      pointSize: 12,
      pointShape: 'triangle',
      width: 3
    }), {}, '✈️ Infrastructure | Large airports', false);
    
    var mediumAirports = airportsInAOI.filter(ee.Filter.eq('type', 'medium_airport'));
    Map.addLayer(mediumAirports.style({
      color: '0066FF',
      fillColor: '0066FF99',
      pointSize: 9,
      pointShape: 'triangle',
      width: 2
    }), {}, '✈️ Infrastructure | Medium airports', false);
    
    var smallAirports = airportsInAOI.filter(ee.Filter.eq('type', 'small_airport'));
    Map.addLayer(smallAirports.style({
      color: '6699FF',
      fillColor: '6699FF99',
      pointSize: 6,
      pointShape: 'triangle',
      width: 2
    }), {}, '✈️ Infrastructure | Small airports', false);
    
    var heliports = airportsInAOI.filter(ee.Filter.eq('type', 'heliport'));
    Map.addLayer(heliports.style({
      color: '00AAFF',
      fillColor: '00AAFF99',
      pointSize: 5,
      pointShape: 'circle',
      width: 2
    }), {}, '🚁 Infrastructure | Heliports', false);
    
  } catch(e) {
    addResult('⚠️ Airports layer unavailable', {color: 'orange'});
  }
  
  try {
    var ports = ee.FeatureCollection('projects/rapiddamagedetection/assets/upply-seaports');
    var portsInAOI = ports.filterBounds(geometry);
    
    Map.addLayer(portsInAOI.style({
      color: '0099FF',
      fillColor: '0099FF99',
      pointSize: 8,
      pointShape: 'square',
      width: 3
    }), {}, '⚓ Infrastructure | Ports', false);
  } catch(e) {
    addResult('⚠️ Ports layer unavailable', {color: 'orange'});
  }
  
  try {
    var healthNodes = ee.FeatureCollection('projects/sat-io/open-datasets/health-site-node');
    var healthWays = ee.FeatureCollection('projects/sat-io/open-datasets/health-site-way');
    
    var healthNodesInAOI = healthNodes.filterBounds(geometry);
    var healthWaysInAOI = healthWays.filterBounds(geometry);
    
    var allHealth = healthNodesInAOI.merge(healthWaysInAOI);
    
    Map.addLayer(allHealth.style({
      color: 'FF0000',
      fillColor: 'FF000099',
      pointSize: 10,
      pointShape: 'plus',
      width: 5
    }), {}, '🏥 Infrastructure | Health facilities', false);
  } catch(e) {
    addResult('⚠️ Health facilities layer unavailable', {color: 'orange'});
  }
  
  addSeparator();
  addResult('✅ Complete', {fontWeight: 'bold', color: '#4CAF50', fontSize: '14px'});
  addSeparator();
  
  statusLabel.setValue('✅ Done');
  
  // ============================================================
  // EXPORTS CONDITIONNELS - CORRECTION CRITIQUE
  // ============================================================
  addSeparator();
  addResult('📤 PREPARING EXPORTS...', {fontWeight: 'bold', color: '#2196F3', fontSize: '13px'});
  addSeparator();
  
  // Vérifier si on a des données à exporter
  var hasDataToExport = (ENABLE_DAMAGE_DETECTION && typeof fp !== 'undefined') ||
                        (ENABLE_FLOOD_DETECTION && typeof floods !== 'undefined') ||
                        (ENABLE_LANDSLIDE_DETECTION && typeof landslides !== 'undefined');
  
  if (hasDataToExport) {
    // Export client-side (liens directs)
    downloadResultsClientSide();
    
    // Export Google Drive (tasks)
    exportResults();
  } else {
    // Weather only - pas d'exports
    addResult('✅ Analysis complete', {fontWeight: 'bold', color: '#4CAF50'});
    addResult('Weather data displayed above');
    addResult('');
    addResult('💡 Enable Damage/Flood/Landslide for data exports', {
      fontSize: '11px',
      color: '#FF9800'
    });
    addSeparator();
  }
}

// ============================================================
// DATA LOADING FUNCTION
// ============================================================
function loadDataAndRun(aoiGeometry, buildingSource, customBuildingAsset, roadsSource, customRoadsAsset) {
  var aoi = ee.FeatureCollection([ee.Feature(aoiGeometry)]);
  
  function validateAssetPath(path) {
    if (!path || typeof path !== 'string') {
      return null;
    }
    var trimmed = path.trim();
    if (trimmed === '' || trimmed === 'Loading...' || trimmed === 'No assets found' || 
        trimmed === 'No tables found' || trimmed === 'Error loading assets' ||
        trimmed === 'No assets accessible' || trimmed === 'Cannot access assets') {
      return null;
    }
    return trimmed;
  }
  
  var footprints;
  if (buildingSource === 'Google Open Buildings v3') {
    footprints = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons').filterBounds(aoiGeometry);
  } else if (buildingSource === 'Google-Microsoft (VIDA Combined)') {
    var centroidInfoB = aoiGeometry.centroid(100).coordinates().getInfo();
    var lonB = centroidInfoB[0], latB = centroidInfoB[1];
    var regionKey;
    if      (lonB>=-85 && lonB<=-59 && latB>=10 && latB<=25) regionKey='caribbean';
    else if (lonB>=-170 && lonB<=-52 && latB>25)              regionKey='north_am';
    else if (lonB>=-82 && lonB<=-34 && latB<=10)              regionKey='cs_am';
    else if (lonB>=-25 && lonB<=50  && latB>35)               regionKey='europe';
    else if (lonB>25   && lonB<=80  && latB>10 && latB<=55)   regionKey='meca';
    else if (lonB>=-18 && lonB<=52  && latB>=-35 && latB<=38) regionKey='africa';
    else if (lonB>60   && lonB<=150 && latB>=-12 && latB<=30) regionKey='se_asia';
    else if (lonB>110  && latB<0)                              regionKey='oceania';
    else                                                       regionKey='africa';
    var isoByRegion = {
      'caribbean': ['JAM','HTI','DOM','CUB'],
      'north_am':  ['USA','CAN','MEX'],
      'cs_am':     ['BRA','COL','ARG','PER','CHL','ECU','BOL'],
      'europe':    ['FRA','DEU','GBR','ITA','ESP','POL','UKR','ROU','NLD'],
      'meca':      ['TUR','SYR','IRQ','IRN','SAU','JOR','LBN','ISR','YEM'],
      'africa':    ['NGA','ETH','KEN','TZA','UGA','ZAF','GHA','EGY','DZA','MAR'],
      'se_asia':   ['IND','BGD','CHN','IDN','PHL','VNM','THA','MMR','MYS'],
      'oceania':   ['AUS','NZL','PNG']
    };
    var isoList = isoByRegion[regionKey];
    var tiles = [];
    for (var i=0; i<isoList.length; i++) {
      tiles.push(ee.FeatureCollection('projects/sat-io/open-datasets/VIDA_COMBINED/' + isoList[i]));
    }
    footprints = ee.FeatureCollection(tiles).flatten().filterBounds(aoiGeometry);
  } else if (buildingSource === 'Custom asset') {
    var validPath = validateAssetPath(customBuildingAsset);
    if (validPath) {
      footprints = ee.FeatureCollection(validPath).filterBounds(aoiGeometry);
    } else {
      addResult('❌ Error: Invalid building asset path. Please enter a valid path.', {color: 'red'});
      return;
    }
  } else {
    footprints = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons').filterBounds(aoiGeometry);
  }
  
  var roads;
  if (roadsSource === 'Custom asset') {
    var validRoadPath = validateAssetPath(customRoadsAsset);
    if (validRoadPath) {
      roads = ee.FeatureCollection(validRoadPath).filterBounds(aoiGeometry);
    } else {
      addResult('❌ Error: Invalid roads asset path. Please enter a valid path.', {color: 'red'});
      return;
    }
  } else {
    var c = aoiGeometry.centroid(100).coordinates().getInfo();
    var lon = c[0], lat = c[1];
    var roadsAsset;
    if (lon >= -85 && lon <= -59 && lat >= 10 && lat <= 25) {
      roadsAsset = ee.FeatureCollection([
        ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/North-America'),
        ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Central-South-America')
      ]).flatten();
    } else if (lon >= -170 && lon <= -52 && lat > 25) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/North-America');
    } else if (lon >= -82 && lon <= -34 && lat <= 10) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Central-South-America');
    } else if (lon >= -25 && lon <= 50 && lat > 35) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Europe');
    } else if (lon > 25 && lon <= 80 && lat > 10 && lat <= 55) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Middle-East-Central-Asia');
    } else if (lon >= -18 && lon <= 52 && lat >= -35 && lat <= 38) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Africa');
    } else if (lon > 60 && lon <= 150 && lat >= -12 && lat <= 30) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/South-East-Asia');
    } else if (lon > 110 && lat < 0) {
      roadsAsset = ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Oceania');
    } else {
      roadsAsset = ee.FeatureCollection([
        ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Africa'),
        ee.FeatureCollection('projects/sat-io/open-datasets/GRIP4/Middle-East-Central-Asia')
      ]).flatten();
    }
    roads = roadsAsset.filterBounds(aoiGeometry);
  }
  runAnalysis(aoi, footprints, roads);
}

// ============================================================
// UI SETUP (if not using custom assets)
// ============================================================
if (!USE_CUSTOM_ASSETS) {
  Map.setOptions('SATELLITE');
  Map.setCenter(-75, 18, 5);
  var tools = Map.drawingTools();
  tools.setShown(true);
  tools.setDrawModes(['rectangle', 'polygon']);
  tools.layers().reset();
  
  var tbPreDate = ui.Textbox({value: PRE_DATE, style: {width: '90px', fontSize: '11px'}});
  var tbEventDate = ui.Textbox({value: EVENT_DATE, style: {width: '90px', fontSize: '11px'}});
  var selPreInterval = ui.Select({items: ['30','60','90','120','150','180','210','240','270','300','330','365'], value: '180', style: {width: '50px', fontSize: '11px', margin: '0'}});
  var selPostInterval = ui.Select({items: ['1','2','3','4','5','6','7','10','14','21','28'], value: '6', style: {width: '50px', fontSize: '11px', margin: '0'}});
  
  var selBuildings = ui.Select({items: ['Google Open Buildings v3', 'Google-Microsoft (VIDA Combined)', 'Custom asset'], value: 'Google Open Buildings v3', style: {width: '200px', fontSize: '9px'}});
  var tbCustomBuilding = ui.Textbox({placeholder: 'projects/.../buildings', style: {width: '200px', fontSize: '9px'}});
  
  var customBuildingRow = ui.Panel([
    tbCustomBuilding
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '2px 0 2px 0', shown: false});
  
  selBuildings.onChange(function(val) {
    var showCustom = val === 'Custom asset';
    customBuildingRow.style().set('shown', showCustom);
  });
  
  var selRoads = ui.Select({items: ['GRIP4 (auto)', 'Custom asset'], value: 'GRIP4 (auto)', style: {width: '200px', fontSize: '9px'}});
  var tbCustomRoads = ui.Textbox({placeholder: 'projects/.../roads', style: {width: '200px', fontSize: '9px'}});
  
  var customRoadsRow = ui.Panel([
    tbCustomRoads
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '2px 0 2px 0', shown: false});
  
  selRoads.onChange(function(val) {
    var showCustom = val === 'Custom asset';
    customRoadsRow.style().set('shown', showCustom);
  });
  
  var selAOIMethod = ui.Select({
    items: ['Draw on map', 'Enter WKT/GeoJSON', 'Custom asset'],
    value: 'Draw on map', 
    style: {width: '200px', fontSize: '9px'}
  });
  
  var tbGeoJSON = ui.Textbox({
    placeholder: 'WKT or GeoJSON (e.g., from QGIS Get WKT plugin)', 
    style: {width: '200px', height: '40px', fontSize: '8px'}
  });
  
  var tbAOIAsset = ui.Textbox({
    placeholder: 'projects/.../aoi', 
    style: {width: '200px', fontSize: '9px'}
  });
  
  var geojsonRow = ui.Panel({
    widgets: [tbGeoJSON],
    style: {shown: false, margin: '2px 0 2px 0'}
  });
  
  var aoiAssetRow = ui.Panel([
    tbAOIAsset
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '2px 0 2px 0', shown: false});
  
  selAOIMethod.onChange(function(val) {
    var drawMode = val === 'Draw on map';
    var geojsonMode = val === 'Enter WKT/GeoJSON';
    var assetMode = val === 'Custom asset';
    
    geojsonRow.style().set('shown', geojsonMode);
    aoiAssetRow.style().set('shown', assetMode);
    tools.setShown(drawMode);
  });
  
  var cbDamage = ui.Checkbox({label: 'Damage detection', value: ENABLE_DAMAGE_DETECTION, style: {fontSize: '10px', margin: '3px 0'}});
  var cbFlood = ui.Checkbox({label: 'Flood detection', value: ENABLE_FLOOD_DETECTION, style: {fontSize: '10px', margin: '3px 0'}});
  var cbLandslide = ui.Checkbox({label: 'Landslide detection', value: ENABLE_LANDSLIDE_DETECTION, style: {fontSize: '10px', margin: '3px 0'}});
  var cbWeather = ui.Checkbox({label: 'Weather data', value: ENABLE_WEATHER_DATA, style: {fontSize: '10px', margin: '3px 0'}});
  
  var selDEM = ui.Select({
    items: ['NASADEM', 'SRTM', 'ALOS', 'ASTER', 'Custom asset'], 
    value: 'NASADEM', 
    style: {width: '200px', fontSize: '9px', color: '#AAAAAA'},
    disabled: true
  });
  var tbCustomDEM = ui.Textbox({
    placeholder: 'projects/.../dem', 
    style: {width: '200px', fontSize: '9px', color: '#AAAAAA'},
    disabled: true
  });
  var customDEMRow = ui.Panel([
    tbCustomDEM
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '2px 0 2px 0', shown: false});
  
  function updateDEMState() {
    var needDEM = cbFlood.getValue() || cbLandslide.getValue();
    selDEM.setDisabled(!needDEM);
    tbCustomDEM.setDisabled(!needDEM);
    
    var textColor = needDEM ? '#000000' : '#AAAAAA';
    selDEM.style().set('color', textColor);
    tbCustomDEM.style().set('color', textColor);
    labelDEMSource.style().set('color', textColor);
  }
  
  selDEM.onChange(function(val) { 
    var showCustom = val === 'Custom asset';
    customDEMRow.style().set('shown', showCustom);
  });
  
  cbFlood.onChange(function() {
    updateDEMState();
    
    var floodEnabled = cbFlood.getValue();
    cbTimeSeries.setDisabled(!floodEnabled);
    
    var tsColor = floodEnabled ? '#000000' : '#AAAAAA';
    cbTimeSeries.style().set('color', tsColor);
    
    if (!floodEnabled) {
      cbTimeSeries.setValue(false);
    }
  });

  cbLandslide.onChange(updateDEMState);
  
  function updateBuildingsRoadsState() {
    var needBuildingsRoads = cbDamage.getValue() || cbFlood.getValue() || cbLandslide.getValue();
    
    selBuildings.setDisabled(!needBuildingsRoads);
    tbCustomBuilding.setDisabled(!needBuildingsRoads);
    selRoads.setDisabled(!needBuildingsRoads);
    tbCustomRoads.setDisabled(!needBuildingsRoads);
    
    var textColor = needBuildingsRoads ? '#000000' : '#AAAAAA';
    selBuildings.style().set('color', textColor);
    tbCustomBuilding.style().set('color', textColor);
    selRoads.style().set('color', textColor);
    tbCustomRoads.style().set('color', textColor);
  }
  
  cbDamage.onChange(updateBuildingsRoadsState);
  cbFlood.onChange(updateBuildingsRoadsState);
  cbLandslide.onChange(updateBuildingsRoadsState);
  
  var leftCol = ui.Panel({style: {width: '165px', padding: '0', margin: '0 6px 0 0'}});
  var middleCol = ui.Panel({style: {width: '210px', padding: '0', margin: '0 6px 0 0'}});
  var rightCol = ui.Panel({style: {width: '235px', padding: '0'}});
  
  var examplesList = ui.Select({
    items: ['New (blank)', 'Demo: Jamaica Whitehouse (Oct 2025)'],
    value: 'New (blank)',
    placeholder: 'Select example...',
    style: {width: '155px', fontSize: '10px', fontWeight: 'bold', margin: '0 0 4px 0'}
  });
  
  examplesList.onChange(function(selected) {
    if (selected === 'Demo: Jamaica Whitehouse (Oct 2025)') {
      tbZoneName.setValue('Whitehouse_Jamaica_Melissa');
      tbPreDate.setValue('2025-09-01');
      tbEventDate.setValue('2025-10-28');
      selPreInterval.setValue('180');
      selPostInterval.setValue('6');
      
      cbWeather.setValue(true);
      cbDamage.setValue(true);
      cbFlood.setValue(false);
      cbLandslide.setValue(false);
      
      selAOIMethod.setValue('Custom asset');
      tbAOIAsset.setValue('projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/AOI_whitehouse');
      
      selBuildings.setValue('Custom asset');
      tbCustomBuilding.setValue('projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Building_OSM_whitehouse');
      
      selRoads.setValue('Custom asset');
      tbCustomRoads.setValue('projects/rapiddamagedetection/assets/examples/jamaica_whitehouse_Melissa_28oct2025/Road_OSM_whitehouse');
      
      sliderTThreshold.setValue(2.4);
      sliderSlope.setValue(10);
      sliderCurvature.setValue(0.05);
      
      statusLabel.setValue('✅ Demo loaded! Click "Run Analysis" to start.');
    } else {
      tbZoneName.setValue('');
      tbPreDate.setValue('2025-09-01');
      tbEventDate.setValue('2025-10-28');
      selPreInterval.setValue('180');
      selPostInterval.setValue('6');
      cbWeather.setValue(true);
      cbDamage.setValue(false);
      cbFlood.setValue(false);
      cbLandslide.setValue(false);
      selAOIMethod.setValue('Draw on map');
      selBuildings.setValue('Google Open Buildings v3');
      selRoads.setValue('GRIP4 (auto)');
      statusLabel.setValue('');
    }
  });
  
  var tbZoneName = ui.Textbox({
    placeholder: 'Zone name (for exports)',
    value: '',
    style: {width: '155px', fontSize: '9px', margin: '2px 0'}
  });
  
  leftCol.add(ui.Label('Quick Start', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0', color: '#2196F3'}));
  leftCol.add(examplesList);
  leftCol.add(ui.Label('1. Zone Name', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  leftCol.add(tbZoneName);
  leftCol.add(ui.Label('2. Dates', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  leftCol.add(ui.Label('YYYY-MM-DD', {fontSize: '9px', color: 'grey', margin: '0 0 2px 0'}));
  leftCol.add(ui.Panel([ui.Label('Pre:', {fontSize: '10px', color: '#444', width: '28px'}), tbPreDate], ui.Panel.Layout.Flow('horizontal'), {margin: '0 0 -6px 0'}));
  leftCol.add(ui.Panel([ui.Label('Event:', {fontSize: '10px', color: '#444', width: '28px'}), tbEventDate], ui.Panel.Layout.Flow('horizontal'), {margin: '-2px 0 0 0'}));
  
  leftCol.add(ui.Label('3. Intervals (days)', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  var intervalsPanel = ui.Panel({
    layout: ui.Panel.Layout.Flow('horizontal'),
    style: {margin: '0'}
  });
  var preCol = ui.Panel([
    ui.Label('Pre', {fontSize: '9px', color: '#444', textAlign: 'center', stretch: 'horizontal'}),
    selPreInterval
  ], ui.Panel.Layout.Flow('vertical'), {margin: '0 4px 0 0', padding: '0'});
  var postCol = ui.Panel([
    ui.Label('Post', {fontSize: '9px', color: '#444', textAlign: 'center', stretch: 'horizontal'}),
    selPostInterval
  ], ui.Panel.Layout.Flow('vertical'), {margin: '0', padding: '0'});
  intervalsPanel.add(preCol);
  intervalsPanel.add(postCol);
  leftCol.add(intervalsPanel);
  
  leftCol.add(ui.Label('4. Options', {fontSize: '11px', fontWeight: 'bold', margin: '3px 0 1px 0'}));
  leftCol.add(cbWeather);
  leftCol.add(cbDamage);
  leftCol.add(cbLandslide);
  leftCol.add(cbFlood);
  
  var cbTimeSeries = ui.Checkbox({
    label: 'Time series (flood only)', 
    value: ENABLE_TIME_SERIES, 
    style: {fontSize: '10px', margin: '1px 0', color: '#AAAAAA'},
    disabled: true
  });
  
  middleCol.add(ui.Label('5. AOI', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  middleCol.add(selAOIMethod);
  middleCol.add(geojsonRow);
  middleCol.add(aoiAssetRow);
  
  middleCol.add(ui.Label('6. Buildings', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  middleCol.add(selBuildings);
  middleCol.add(customBuildingRow);
  
  middleCol.add(ui.Label('7. Roads', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  middleCol.add(selRoads);
  middleCol.add(customRoadsRow);
  
  var labelDEMSource = ui.Label('8. DEM Source', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0', color: '#AAAAAA'});
  rightCol.add(labelDEMSource);
  rightCol.add(selDEM);
  rightCol.add(customDEMRow);
  
  rightCol.add(ui.Label('9. Settings', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  
  var sliderTThreshold = ui.Slider({
    min: 2, max: 5, value: T_THRESHOLD, step: 0.2,
    style: {width: '135px'},
    disabled: true
  });
  var labelTValue = ui.Label(T_THRESHOLD.toFixed(1), {
    fontSize: '8px', color: '#AAAAAA', width: '28px', textAlign: 'right', fontWeight: 'bold'
  });
  sliderTThreshold.onChange(function(value) {
    labelTValue.setValue(value.toFixed(1));
    T_THRESHOLD = value;
  });
  var rowTThreshold = ui.Panel([
    ui.Label('T-thresh', {fontSize: '10px', color: '#000000', width: '50px'}),
    sliderTThreshold,
    labelTValue
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '0'});
  rightCol.add(rowTThreshold);
  
  var sliderSlope = ui.Slider({
    min: 5, max: 30, value: MIN_SLOPE, step: 1,
    style: {width: '135px'},
    disabled: true
  });
  var labelSlopeValue = ui.Label(MIN_SLOPE + '°', {
    fontSize: '8px', color: '#AAAAAA', width: '28px', textAlign: 'right', fontWeight: 'bold'
  });
  sliderSlope.onChange(function(value) {
    labelSlopeValue.setValue(value + '°');
    MIN_SLOPE = value;
  });
  var rowSlope = ui.Panel([
    ui.Label('Slope', {fontSize: '10px', color: '#000000', width: '50px'}),
    sliderSlope,
    labelSlopeValue
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '0'});
  rightCol.add(rowSlope);
  
  var sliderCurvature = ui.Slider({
    min: 0.01, max: 0.2, value: MIN_CURVATURE, step: 0.01,
    style: {width: '135px'},
    disabled: true
  });
  var labelCurvValue = ui.Label(MIN_CURVATURE.toFixed(2), {
    fontSize: '8px', color: '#AAAAAA', width: '28px', textAlign: 'right', fontWeight: 'bold'
  });
  sliderCurvature.onChange(function(value) {
    labelCurvValue.setValue(value.toFixed(2));
    MIN_CURVATURE = value;
  });
  var rowCurvature = ui.Panel([
    ui.Label('Curvature', {fontSize: '10px', color: '#000000', width: '50px'}),
    sliderCurvature,
    labelCurvValue
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '2px 0'});
  rightCol.add(rowCurvature);
  
  rightCol.add(ui.Label('10. Time Series', {fontSize: '11px', fontWeight: 'bold', margin: '2px 0 1px 0'}));
  rightCol.add(cbTimeSeries);
  
  var tbTimeSeriesStart = ui.Textbox({
    placeholder: 'YYYY-MM-DD',
    value: TIME_SERIES_START,
    style: {width: '90px', fontSize: '9px', color: '#AAAAAA'},
    disabled: true
  });
  
  var tbTimeSeriesEnd = ui.Textbox({
    placeholder: 'YYYY-MM-DD',
    value: TIME_SERIES_END,
    style: {width: '90px', fontSize: '9px', color: '#AAAAAA'},
    disabled: true
  });
  
  var timeSeriesStartRow = ui.Panel([
    ui.Label('From:', {fontSize: '9px', color: '#000000', width: '35px'}),
    tbTimeSeriesStart
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '0 0 -4px 0', shown: false});
  
  var timeSeriesEndRow = ui.Panel([
    ui.Label('To:', {fontSize: '9px', color: '#000000', width: '35px'}),
    tbTimeSeriesEnd
  ], ui.Panel.Layout.Flow('horizontal'), {margin: '0', shown: false});
  
  rightCol.add(timeSeriesStartRow);
  rightCol.add(timeSeriesEndRow);
  
  function updateAdvancedParametersState() {
    var damageOrLandslide = cbDamage.getValue() || cbLandslide.getValue();
    var landslideOnly = cbLandslide.getValue();
    var timeSeriesEnabled = cbTimeSeries.getValue();
    
    sliderTThreshold.setDisabled(!damageOrLandslide);
    var tColor = damageOrLandslide ? '#000000' : '#AAAAAA';
    rowTThreshold.widgets().get(0).style().set('color', tColor);
    labelTValue.style().set('color', tColor);
    
    sliderSlope.setDisabled(!landslideOnly);
    sliderCurvature.setDisabled(!landslideOnly);
    var lColor = landslideOnly ? '#000000' : '#AAAAAA';
    rowSlope.widgets().get(0).style().set('color', lColor);
    labelSlopeValue.style().set('color', lColor);
    rowCurvature.widgets().get(0).style().set('color', lColor);
    labelCurvValue.style().set('color', lColor);
    
    timeSeriesStartRow.style().set('shown', timeSeriesEnabled);
    timeSeriesEndRow.style().set('shown', timeSeriesEnabled);
    tbTimeSeriesStart.setDisabled(!timeSeriesEnabled);
    tbTimeSeriesEnd.setDisabled(!timeSeriesEnabled);
    
    var tsColor = timeSeriesEnabled ? '#000000' : '#AAAAAA';
    tbTimeSeriesStart.style().set('color', tsColor);
    tbTimeSeriesEnd.style().set('color', tsColor);
  }
  
  cbDamage.onChange(updateAdvancedParametersState);
  cbLandslide.onChange(updateAdvancedParametersState);
  cbTimeSeries.onChange(function() {
    updateAdvancedParametersState();
    if (cbTimeSeries.getValue()) {
      if (!tbTimeSeriesStart.getValue()) {
        tbTimeSeriesStart.setValue(tbPreDate.getValue());
      }
      if (!tbTimeSeriesEnd.getValue()) {
        tbTimeSeriesEnd.setValue(tbEventDate.getValue());
      }
    }
  });
  
  var statusLabel = ui.Label('', {fontSize: '10px', color: '#555', margin: '4px 0', stretch: 'horizontal'});
  var progressLabel = ui.Label('', {fontSize: '9px', color: '#00AA00', margin: '0 0 4px 0', stretch: 'horizontal', fontFamily: 'monospace'});
  
  function isValidDate(s) { return /^\d{4}-\d{2}-\d{2}$/.test(s); }
  
  updateDEMState();
  updateBuildingsRoadsState();
  
var helpBtnTopRight = ui.Button({
    label: '?',
    style: {
      padding: '2px 8px',
      backgroundColor: 'white',
      color: 'black',
      fontWeight: 'bold',
      fontSize: '12px',
      margin: '0 0 0 4px',
      border: 'none'
    }
  });
  
  helpBtnTopRight.onClick(function() {
    if (helpPanelOpen !== null) {
      Map.remove(helpPanelOpen);
      helpPanelOpen = null;
      return;
    }
    
    var helpPanel = ui.Panel({
      style: {
        width: '600px',
        position: 'top-center',
        padding: '20px',
        backgroundColor: 'white',
        border: '3px solid #4CAF50',
        maxHeight: '80%'
      }
    });
    
    helpPanelOpen = helpPanel;
    
    var helpContent = ui.Panel({
      style: {
        maxHeight: '500px',
        padding: '0'
      }
    });
    
    helpContent.add(ui.Label('📖 User Guide', {
      fontWeight: 'bold',
      fontSize: '18px',
      margin: '0 0 16px 0',
      color: '#4CAF50'
    }));
    
    helpContent.add(ui.Label('Quick Start', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0', color: '#2196F3'}));
    helpContent.add(ui.Label('Select an example from the dropdown to auto-fill all fields, or choose "New (blank)" to start from scratch.', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('1. Zone Name', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('Enter a name for your analysis (e.g., "Haiti_Beryl_2024"). Used for export folders.', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('2. Dates', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('• Pre: Baseline date before the event\n• Event: Date of the cyclone/disaster', {fontSize: '11px', margin: '0 0 12px 8px', whiteSpace: 'pre'}));
    
    helpContent.add(ui.Label('3. Intervals', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('• Pre: Time window before "Pre" date to search for Sentinel-1 baseline images (default: 180 days)\n• Post: Time window after "Event" date to search for Sentinel-1 post-event images (default: 6 days). Note: Sentinel-1 revisit time is ~6 days.', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('4. Options', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('• Weather: Precipitation, wind, pressure charts\n• Damage: Buildings + roads (SAR change detection)\n• Landslide: Susceptibility mapping\n• Flood: Extent mapping', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('5. Area of Interest', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('Choose:\n• Draw on map: Use drawing tools\n• Enter WKT/GeoJSON: Paste WKT or GeoJSON (use QGIS "Get WKT" plugin)\n• Custom asset: Enter asset path', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('6-7. Buildings, Roads', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('Select datasets or provide custom asset paths (format: projects/YOUR_PROJECT/assets/...).', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('8. DEM Source', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('Choose elevation model for landslide and flood analysis. Enabled only when Landslide or Flood is selected. You can also provide your own custom DEM asset path (format: projects/YOUR_PROJECT/assets/...).', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('9. Settings', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('• T-threshold: Damage sensitivity (higher = less sensitive)\n• Slope: Min slope for landslides (°)\n• Curvature: Min terrain curvature', {fontSize: '11px', margin: '0 0 12px 8px'}));
    
    helpContent.add(ui.Label('10. Time Series', {fontWeight: 'bold', fontSize: '13px', margin: '8px 0 4px 0'}));
    helpContent.add(ui.Label('For flood analysis only. Specify date range to track flood evolution.', {fontSize: '11px', margin: '0 0 16px 8px'}));
    
    helpContent.add(ui.Label('───────────────────', {color: '#ccc', margin: '8px 0'}));
    helpContent.add(ui.Label('💡 Results appear in the right panel. Layers are grouped in the Layers panel. Two export options available: instant download (GeoJSON) or Google Drive (complete dataset).', {fontSize: '11px', color: '#666', fontStyle: 'italic'}));
    
    // Séparateur
    helpContent.add(ui.Label('───────────────────', {color: '#ccc', margin: '12px 0'}));
    
    // Titre
    helpContent.add(ui.Label('📚 Full Documentation', {
      fontWeight: 'bold',
      fontSize: '13px',
      margin: '8px 0 8px 0',
      color: '#2196F3'
    }));
    
    // Lien cliquable English
    var linkEN = ui.Label({
      value: '🇬🇧 English: Click here to open README',
      style: {
        fontSize: '12px',
        color: 'blue',
        margin: '4px 0 4px 8px',
        textDecoration: 'underline'
      },
      targetUrl: 'https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping#readme'
    });
    helpContent.add(linkEN);
    
    // Lien cliquable French
    var linkFR = ui.Label({
      value: '🇫🇷 Français : Cliquez ici pour ouvrir le README',
      style: {
        fontSize: '12px',
        color: 'blue',
        margin: '4px 0 12px 8px',
        textDecoration: 'underline'
      },
      targetUrl: 'https://github.com/renouxfabrice/Rapid-Cyclone-Damage-Mapping/blob/main/README.fr.md'
    });
    helpContent.add(linkFR);
    
    var closeBtn = ui.Button({
      label: 'Close',
      style: {
        stretch: 'horizontal', 
        margin: '8px 0 0 0', 
        backgroundColor: '#f44336', 
        color: '#000000',
        fontWeight: 'bold'
      }
    });
    closeBtn.onClick(function() {
      Map.remove(helpPanel);
      helpPanelOpen = null;
    });
    
    helpPanel.add(helpContent);
    helpPanel.add(closeBtn);
    
    Map.add(helpPanel);
  });
  
  var mainPanelCollapsed = false;
  var mainPanelToggleBtn = ui.Button({
    label: '▼',
    style: {
      padding: '2px 8px',
      backgroundColor: 'white',
      color: 'black',
      fontWeight: 'bold',
      fontSize: '12px',
      border: 'none',
      margin: '0 0 0 8px'
    }
  });
  
  mainPanelToggleBtn.onClick(function() {
    mainPanelCollapsed = !mainPanelCollapsed;
    leftCol.style().set('shown', !mainPanelCollapsed);
    middleCol.style().set('shown', !mainPanelCollapsed);
    rightCol.style().set('shown', !mainPanelCollapsed);
    runBtn.style().set('shown', !mainPanelCollapsed);
    resetBtn.style().set('shown', !mainPanelCollapsed);
    statusLabel.style().set('shown', !mainPanelCollapsed);
    progressLabel.style().set('shown', !mainPanelCollapsed);
    mainPanelToggleBtn.setLabel(mainPanelCollapsed ? '▶' : '▼');
    
    if (mainPanelCollapsed) {
      mainPanel.style().set('width', '320px');
    } else {
      mainPanel.style().set('width', '620px');
    }
  });
  
  var titleRow = ui.Panel({
    layout: ui.Panel.Layout.Flow('horizontal'),
    style: {stretch: 'horizontal'}
  });
  
  var titleLabel = ui.Label('⚡ Rapid Damage Detection', {
    fontWeight: 'bold', 
    fontSize: '14px', 
    margin: '0',
    stretch: 'horizontal'
  });
  
  titleRow.add(titleLabel);
  titleRow.add(mainPanelToggleBtn);
  titleRow.add(helpBtnTopRight);
  
  var mainPanel = ui.Panel({
    widgets: [
      titleRow,
      ui.Panel([leftCol, middleCol, rightCol], ui.Panel.Layout.Flow('horizontal'), {margin: '0'})
    ],
    style: {
      position: 'top-left', 
      padding: '8px 10px', 
      width: '670px', 
      border: '2px solid #FF9800', 
      backgroundColor: 'white',
      maxWidth: '820px' 
    }
  });
  
  var runBtn = ui.Button({
    label: 'Run Analysis', 
    style: {
      stretch: 'horizontal', 
      margin: '4px 0', 
      backgroundColor: '#E0E0E0', 
      color: '#000000',
      fontWeight: 'bold'
    }
  });
  
  runBtn.onClick(function() {
    resultsPanelContent.clear();
    
    var zoneName = tbZoneName.getValue().trim();
    var preDate = tbPreDate.getValue().trim();
    var eventDate = tbEventDate.getValue().trim();
    var preInt = parseInt(selPreInterval.getValue(), 10);
    var postInt = parseInt(selPostInterval.getValue(), 10);
    
    ZONE_NAME = zoneName || 'UnnamedZone';
    
    if (cbTimeSeries.getValue()) {
      var tsStart = tbTimeSeriesStart.getValue().trim();
      var tsEnd = tbTimeSeriesEnd.getValue().trim();
      
      if (!tsStart || !tsEnd) {
        statusLabel.setValue('❌ Time series dates required');
        progressLabel.setValue('Please enter both start and end dates');
        return;
      }
      
      if (!isValidDate(tsStart) || !isValidDate(tsEnd)) {
        statusLabel.setValue('❌ Invalid time series date format');
        progressLabel.setValue('Please use YYYY-MM-DD format');
        return;
      }
      
      if (tsStart >= tsEnd) {
        statusLabel.setValue('❌ Start date must be before end date');
        progressLabel.setValue('');
        return;
      }
      
      ENABLE_TIME_SERIES = true;
      TIME_SERIES_START = tsStart;
      TIME_SERIES_END = tsEnd;
    } else {
      ENABLE_TIME_SERIES = false;
    }
    
    if (!isValidDate(preDate) || !isValidDate(eventDate)) {
      statusLabel.setValue('⚠️ Invalid date format.');
      return;
    }
    if (preDate >= eventDate) {
      statusLabel.setValue('⚠️ Pre-date must be before event.');
      return;
    }
    
    var drawnGeom;
    if (selAOIMethod.getValue() === 'Enter WKT/GeoJSON') {
      var geojsonStr = tbGeoJSON.getValue();
      if (!geojsonStr || String(geojsonStr).trim() === '') {
        statusLabel.setValue('⚠️ Enter WKT/GeoJSON.');
        return;
      }
      try {
        var geojson = JSON.parse(String(geojsonStr).trim());
        drawnGeom = ee.Geometry(geojson);
      } catch (e) {
        statusLabel.setValue('⚠️ Invalid WKT/GeoJSON.');
        return;
      }
    } else if (selAOIMethod.getValue() === 'Custom asset') {
      var aoiAssetPath = tbAOIAsset.getValue().trim();
      if (!aoiAssetPath) {
        statusLabel.setValue('⚠️ Enter AOI asset path.');
        return;
      }
      try {
        drawnGeom = ee.FeatureCollection(aoiAssetPath).geometry();
      } catch(e) {
        statusLabel.setValue('⚠️ Invalid AOI asset.');
        return;
      }
    } else {
      var layers = tools.layers();
      var geomList = [];
      for (var i = 0; i < layers.length(); i++) {
        var geoms = layers.get(i).geometries();
        for (var j = 0; j < geoms.length(); j++) { geomList.push(geoms.get(j)); }
      }
      if (geomList.length === 0) {
        statusLabel.setValue('⚠️ Draw an AOI first.');
        return;
      }
      drawnGeom = ee.Geometry(geomList[0]);
      for (var k = 1; k < geomList.length; k++) {
        drawnGeom = drawnGeom.union(ee.Geometry(geomList[k]), 1);
      }
    }
    
    if (selAOIMethod.getValue() === 'Draw on map') {
      tools.layers().reset();
    }
    
    CURRENT_AOI = drawnGeom;
    Map.centerObject(drawnGeom, 12);
    
    PRE_DATE = preDate;
    EVENT_DATE = eventDate;
    PRE_INTERVAL = preInt;
    POST_INTERVAL = postInt;
    ENABLE_DAMAGE_DETECTION = cbDamage.getValue();
    ENABLE_FLOOD_DETECTION = cbFlood.getValue();
    ENABLE_LANDSLIDE_DETECTION = cbLandslide.getValue();
    ENABLE_WEATHER_DATA = cbWeather.getValue();
    
    DEM_SOURCE = selDEM.getValue();
    CUSTOM_DEM_ASSET = tbCustomDEM.getValue();
    
    statusLabel.setValue('⏳ Running…');
    progressLabel.setValue('░░░░░░░░░░░░░░░░░░░░ 0% - Starting analysis...');
    
    loadDataAndRun(drawnGeom, selBuildings.getValue(), tbCustomBuilding.getValue(), 
                   selRoads.getValue(), tbCustomRoads.getValue());
  });
  
  var resetBtn = ui.Button({
    label: 'Clear All', 
    style: {
      stretch: 'horizontal', 
      margin: '0',
      color: '#000000',
      fontWeight: 'bold',
      backgroundColor: '#E0E0E0'
    }
  });
  
  resetBtn.onClick(function() {
    tools.layers().reset();
    Map.layers().reset();
    CURRENT_AOI = null;
    statusLabel.setValue('');
    progressLabel.setValue('');
    resultsPanelContent.clear();
  });
  
  mainPanel.add(runBtn);
  mainPanel.add(resetBtn);
  mainPanel.add(statusLabel);
  mainPanel.add(progressLabel);
  Map.add(mainPanel);
  Map.add(resultsPanel);
  
  updateDEMState();
} else {
  runAnalysis(ee.FeatureCollection(CUSTOM_AOI), ee.FeatureCollection(CUSTOM_FOOTPRINTS), ee.FeatureCollection(CUSTOM_ROADS));
}
