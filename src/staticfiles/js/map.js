const cartoLayer = L.tileLayer(
  "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  }
);

const map = L.map("map", {
  center: [48.459801, 35.009273],
  zoom: 11,
  layers: [cartoLayer],
  minZoom: 6,
  maxZoom: 15,
  zoomControl: false,
  fullscreenControl: true,
  fullscreenControlOptions: {
    position: "bottomright",
  },
  preferCanvas: true,
});

let fullScreen = false;
let fetchMarkersEnabled = true;
let currentMarkers = {};
let regionsFetched = false
const geojsonLayers = {};


addButtonsLogic(map);
addDeepStateLayer(map);
addRegionsBordersLayer(map);

map.on('popupopen', () => {
    attachContextMenuToPopupImages();
});
document.addEventListener('DOMContentLoaded', ()=>{
  fetchRegions(map)

  fetchMarkers(map)
});

map.on('zoomend', function() {
  const currentZoom = map.getZoom();

  if (currentZoom >= 9) {
    fetchMarkersEnabled = true
    hideGeoJSONLayers(map)
  } else {
    fetchMarkersEnabled = false
    removeAllMarkers(map)
    showGeoJSONLayers(map)
    
  }
});

map.on('moveend', () => {
  if(fetchMarkersEnabled) {
    fetchMarkers(map)
  }
});


function addDeepStateLayer(map) {
    fetch("https://deepstatemap.live/api/history/1687169321/geojson", {
      mode: "cors",
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        const polygons = data.features.filter(
          (feature) => feature.geometry.type !== "Point"
        );
        const geoJsonData = {
          type: "FeatureCollection",
          features: polygons,
        };
        L.geoJSON(geoJsonData, {
          style: function (feature) {
            return {
              color: feature.properties.stroke,
              fillColor: feature.properties.fill,
              weight: feature.properties["stroke-width"],
              fillOpacity: feature.properties["fill-opacity"],
            };
          },
        }).addTo(map);
      })
      .catch(function (error) {
        console.error(error);
      });
}

function addRegionsBordersLayer(map) {
    fetch("/static/json/regions.geojson")
      .then((response) => response.json())
      .then((data) => {
        data.features.forEach((feature) => {
          const myStyle = {
            "opacity": 1,
            "fillOpacity": 0,
            "weight": 1,
        };
          L.geoJSON(feature, {
            style: myStyle
          }).addTo(map);
        });
      })
      .catch((error) => {
        console.error("Error fetching regions:", error);
      });
}

function addButtonsLogic(map) {
    // add zoom buttons
    L.control.zoom({
        position: 'bottomleft'
    }).addTo(map)
    
    // add search btn
    L.Control.geocoder().addTo(map)

    // Logic for changing icons
    map.on("enterFullscreen", () => {
      fullScreen = true;
      const btn = document.querySelector(".leaflet-control-zoom-fullscreen");
      btn.innerHTML = "";
      const icon = document.createElement("i");
      icon.classList.add("fas", "fa-compress");
      btn.appendChild(icon);
    });
    map.on("exitFullscreen", () => {
      fullScreen = false;
      const btn = document.querySelector(".leaflet-control-zoom-fullscreen");
      btn.innerHTML = "";
      const icon = document.createElement("i");
      icon.classList.add("fas", "fa-expand");
      btn.appendChild(icon);
    });

    // Snapshot button logic
    L.easyButton("fa-solid fa-camera", function (btn, map) {
      const mapElement = document.querySelector("#map");
      html2canvas(mapElement, {
        useCORS: true,
        ignoreElements: (element) => {
          return (
            element.classList.contains("leaflet-bar") ||
            element.classList.contains("leaflet-control")
          );
        },
      }).then(function (canvas) {
        const link = document.createElement("a");
        link.download = "map-snapshot.png";
        const imageDataURL = canvas.toDataURL("image/png");

        link.href = imageDataURL;

        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);
      });
    }).addTo(map);
    map.on("popupopen", () => {
      attachContextMenuToPopupImages();
    });
}


function fetchPhoto(page, id) {
    return fetch(`/api/get_marker_photos/${id}/?page=${page}`)
        .then(response => response.json())
        .then(data => {
            const dataObj = data.data_entries[0]
            const photo = `<img src="${dataObj.photo}" alt="Marker Photo" style="width: 100px; height: 150px; border-radius: 20px; user-select: none; margin-bottom: 5px">`;
            const maxPage = data.max_page
            const updateData = {
                photo, maxPage, dataObj
            }
            return updateData;
        })
        .catch(error => {
            const updateData = {photo: null, maxPage: null, dataObj: null}
            return updateData
        })
}

function removeMarkersOutsideBounds(bounds, markers) {
  const minLat = bounds.getSouth();
  const maxLat = bounds.getNorth();
  const minLng = bounds.getWest();
  const maxLng = bounds.getEast();

  for (const markerId in markers) {
    const marker = markers[markerId];
    const markerLat = marker.marker.getLatLng().lat;
    const markerLng = marker.marker.getLatLng().lng;

    if (
      markerLat < minLat ||
      markerLat > maxLat ||
      markerLng < minLng ||
      markerLng > maxLng
    ) {
      delete markers[markerId];
      map.removeLayer(marker.marker);
    }
  }
}

function removeAllMarkers(map) {
  for (const id in currentMarkers) {
    const marker = currentMarkers[id]
    delete currentMarkers[id]
    map.removeLayer(marker.marker)
  }
}



function fetchMarkers(map) {
    const bounds = map.getBounds();

    const minLat = bounds.getSouth();
    const maxLat = bounds.getNorth();
    const minLng = bounds.getWest();
    const maxLng = bounds.getEast();
    removeMarkersOutsideBounds(bounds, currentMarkers);
    const url = `/api/markers/?minLat=${minLat}&maxLat=${maxLat}&minLng=${minLng}&maxLng=${maxLng}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            data.forEach(markerData => {
                if(currentMarkers[markerData.id]) {
                    return;
                }
                if(markerData.category && markerData.category.icon && markerData.category.color) {
                    const latLng = [markerData.lat, markerData.lng];
                    const iconOptions = {
                        icon: markerData.category.icon.replace('fa-', ''),
                        prefix: 'fa',
                        markerColor: markerData.category.color,
                    };
                    const customIcon = L.AwesomeMarkers.icon(iconOptions);
                    const marker = L.marker(latLng, {icon: customIcon});
                    currentMarkers[markerData.id] = {
                        marker: marker, 
                        activityId: markerData.category.id, 
                        popupDataFetched: false, 
                        currentPage: 1,
                        maxPage: 1
                    }
                    marker.on('click', function(event) {
                        updatePopup( markerData.id, 0);
                    });
                    marker.addTo(map)
                }

            })
        })

}

window.updatePopup = (id, offset) => {
    const markerData = currentMarkers[id];
    const marker = markerData.marker
    markerData.currentPage = markerData.currentPage + offset;
    if (markerData.currentPage > markerData.maxPage) {
        markerData.currentPage = 1;
    }
    if (markerData.currentPage <= 0) {
        markerData.currentPage = markerData.maxPages;
    }

    fetchPhoto(markerData.currentPage, id).then((updateData) => {
        if (updateData.photo && updateData.maxPage && updateData.dataObj) {
            markerData.maxPage = updateData.maxPage;
            const received_items = Object.entries(updateData.dataObj.received_items)
              .map((entry) => {
              const [key, value] = entry;
              const item = key.charAt(0).toUpperCase() + key.slice(1);
              return `<li>${item}: ${value}</li>`;
            })
            .join("");
            marker.bindPopup(`
                <div id="${id}" style="width: 301px;">
                    <h5 id="${id}" style="text-align: center; width: 301px">${updateData.dataObj.category_name}</h5>
                    <div id="${id}" style="display: flex; width: 301px; justify-content: center">
                        <div id="${id}" style="display: flex; align-items: center;">
                            <span id="${id}" onclick="updatePopup(${id}, -1)" style="cursor: pointer; margin-right: 10px; font-size: 1.5em;"><i class="fa-solid fa-arrow-left"></i></span>
                            ${updateData.photo}
                            <span id="${id}" onclick="updatePopup(${id}, 1)" style="cursor: pointer; margin-left: 10px; font-size: 1.5em"><i class="fa-solid fa-arrow-right" style="color: #000000;"></i></span>
                        </div>  
                        <div id="${id}" style="display: flex; min-width: 100px; flex-direction: column; margin-left: 20px"> 
                            <p style="width: 100px" class="info-popup">Date: ${updateData.dataObj.date}</p>
                            <p class="info-popup">Place: ${updateData.dataObj.settlement}</p>      
                            <p style="width: 100px" class="info-popup">Gender: ${updateData.dataObj.gender}</p>
                            <p class="info-popup">Age: ${updateData.dataObj.age}</p> 
                            ${received_items ? `<p style="width: 100px" class="info-popup">Received items:</p><ul>${received_items}</ul>`: ""}
                    </div>
                </div>
                `);
                if (offset == 0)
                {
                    marker.openPopup();
                }
            }
        });
  
}

function fetchRegions(map) {
  fetch(`/api/get_regions_data`)
    .then(response => response.json())
    .then(data => {
      fetch("/static/json/regions.geojson")
        .then((response) => response.json())
        .then((geojson_data) => {
          geojson_data.features.forEach(feature => {
            const shapeName = feature.properties.shapeName;
            const oblastName = data.find(obj => obj.oblast === shapeName);
            if (oblastName) {
              const defaultStyle = {
                "opacity": 1,
                "fillOpacity": 0.3,
                "color": "blue",
                "fillColor": "pink",
                "weight": 1,

              };

              geojsonLayers[oblastName.oblast] = L.geoJSON(feature, {
                style: defaultStyle,
                onEachFeature: (feature, layer) => {
                  layer.on({
                    mouseover: (event) => {
                      layer.setStyle({
                        "fillOpacity": 0.8,
                        "color": "blue",
                        "fillColor": "blue",
                      });
                    },
                    mouseout: (event) => {
                      layer.setStyle(defaultStyle);
                    }
                  });
                  let activities = ""
                  if (oblastName.activities && Array.isArray(oblastName.activities)) {
                    oblastName.activities.forEach((entry) => {
                      if (entry) {
                        activities += `<li>${entry}</li>`;
                      }
                    });
                  }
    
                  const popupContent = `<h5>${oblastName.oblast}</h5><p>Beneficiaries in total: ${oblastName.total_benef}</p><p>Activities: </p><ul>${activities}</ul>`;
                  layer.bindPopup(popupContent);
                }
              })
            }
          });
        })
        .catch(error => {
          console.error('Error parsing GeoJSON:', error);
        });
    })
    .catch(error => {
      console.error('Error fetching regions:', error);
    });
}

function hideGeoJSONLayers(map) {
    Object.values(geojsonLayers).forEach(layer => {
      map.removeLayer(layer);
    });
}

function showGeoJSONLayers(map) {
  Object.values(geojsonLayers).forEach(layer => {
    layer.addTo(map);
  });
}

// function for delete context menu
function attachContextMenuToPopupImages() {
  const popups = document.querySelectorAll(".leaflet-popup-content img");
  popups.forEach((popup) => {
    popup.addEventListener("contextmenu", function (e) {
      e.preventDefault();
    });
  });
}


