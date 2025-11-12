// Coordenadas de EAFIT, Medellín
const eafitCoords = [6.2009, -75.5781];

// Inicializar el mapa centrado en EAFIT
var map = L.map('map').setView(eafitCoords, 17);

// Agregar capa de mapa (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Lugares exactos de EAFIT (coordenadas convertidas desde plus codes)

let lugaresEafit = [];
let capasConexiones = []; // Almacena todas las capas dibujadas de conexiones


function limpiarConexiones() {
    capasConexiones.forEach(capa => {
        map.removeLayer(capa);
    });
    capasConexiones = [];
}

function dibujarConexionesDelBloque(nombreBloque) {
    limpiarConexiones();
    
    // Obtener detalles del lugar con sus conexiones
    fetch(`/location/api/lugar/${encodeURIComponent(nombreBloque)}/`)
        .then(response => response.json())
        .then(data => {
            if (data.connections && data.connections.length > 0) {
                // Crear lista de conexiones para mostrar
                let nombresConexiones = data.connections.map(conn => conn[0]).join('<br>');
                
                // Mostrar popup con las conexiones disponibles
                L.popup()
                    .setLatLng(data.coords)
                    .setContent(`<b>${nombreBloque}</b><br><small style="color: #FF6B6B;">📍 Conexiones disponibles:</small><br>${nombresConexiones}`)
                    .openOn(map);
                
                // Dibujar las líneas de conexión (punteadas en rojo)
                data.connections.forEach(conexion => {
                    let destino = conexion[0];
                    let coordenadas = conexion[2]; // Ruta con waypoints
                    
                    // Dibujar línea punteada roja
                    let linea = L.polyline(coordenadas, {
                        color: '#FF6B6B',
                        weight: 3,
                        dashArray: '5, 5',
                        opacity: 0.7
                    }).addTo(map);
                    
                    capasConexiones.push(linea);
                });
            }
        })
        .catch(error => console.error('Error al obtener conexiones:', error));
}


fetch('/location/api/lugares/')
    .then(response => response.json())
    .then(data => {
        lugaresEafit = data; // Guardar en la lista

        // Agregar marcadores al mapa
        lugaresEafit.forEach(lugar => {
            const coords = lugar.coords;
            L.marker(coords)
                .addTo(map)
                .bindPopup(`<b>${lugar.nombre}</b><br>${lugar.descripcion}`)
                .on('click', function() {
                    map.setView(coords, 18);
                });
        });
    });

const fromInput = document.getElementById('fromInput');
const fromSearch = document.getElementById('fromSearch');
const toInput = document.getElementById('toInput');
const toSearch = document.getElementById('toSearch');

const fromSearchImageButton = document.getElementById('imageSearchFrom');
const toSearchImageButton = document.getElementById('imageSearchTo');

var searchingByFromImage = false;

var fromLocation = null;
var toLocation = null;

// Para la busqueda en IA(una mosquiherramienta que nos servira para mas tarde ;D)
fromSearchImageButton.addEventListener('click', function() {
    searchingByFromImage = true;
    console.log(true);
});

toSearchImageButton.addEventListener('click', function() {
    searchingByFromImage = false;
    console.log(false);
});

fromSearch.addEventListener('click', function (event) {
    const clickedElement = event.target.closest('.recomendacion');
    if (!clickedElement) return;

    const nombreBuscado = clickedElement.id;

    for (let lugar of lugaresEafit) {
        if (lugar.nombre === nombreBuscado) {
            fromLocation = lugar;
            goToPlace(lugar.coords[0], lugar.coords[1], lugar.nombre, fromInput, fromSearch);
                dibujarConexionesDelBloque(nombreBuscado); // Mostrar conexiones
                if(fromLocation != null && toLocation != null) {
                    calcRoute(fromLocation, toLocation);
                }
            break;
        }
    }
});

toSearch.addEventListener('click', function (event) {
    const clickedElement = event.target.closest('.recomendacion');
    if (!clickedElement) return;

    const nombreBuscado = clickedElement.id;

    for (let lugar of lugaresEafit) {
        if (lugar.nombre === nombreBuscado) {
            toLocation = lugar;
            goToPlace(lugar.coords[0], lugar.coords[1], lugar.nombre, toInput, toSearch);
            dibujarConexionesDelBloque(nombreBuscado); // Mostrar conexiones
            if(fromLocation != null && toLocation != null) {
                calcRoute(fromLocation, toLocation);
            }
            break;
        }
    }
});

// Función de búsqueda
function searchPlace(input, searchDiv) {
    const query = input.value.toLowerCase().trim();

    if (query.length < 2) {
        searchDiv.style.display = 'none';
        return;
    }

    // Filtrar lugares que coincidan con la búsqueda
    const matches = lugaresEafit.filter(lugar =>
        lugar.nombre.toLowerCase().includes(query) ||
        lugar.descripcion.toLowerCase().includes(query)
    );

    if (matches.length > 0) {
        searchDiv.innerHTML = matches.map(lugar =>
            `<div class="search-item recomendacion" onclick="goToPlace(${lugar.coords[0]}, ${lugar.coords[1]}, '${lugar.name}', ${input}, ${searchDiv})" id="${lugar.nombre}">
                <strong>${lugar.nombre}</strong><br>
                <small>${lugar.descripcion}</small>
            </div>`
        ).join('');
        searchDiv.style.display = 'block';
    } else {
        searchDiv.innerHTML = '<div class="search-item">No se encontraron lugares</div>';
        searchDiv.style.display = 'block';
    }
}

// Función para ir a un lugar específico
function goToPlace(lat, lng, nombre, input, searchDiv) {
    map.setView([lat, lng], 19);
    searchDiv.style.display = 'none';
    input.value = nombre;
    var prefix = (input===fromInput?"¡Estas Aquí!":"¡Vas Hacia Aca!")

    // Mostrar popup del lugar
    L.popup()
        .setLatLng([lat, lng])
        .setContent(`<b>${prefix}</b><br>${nombre}`)
        .openOn(map);
}

fromInput.addEventListener('input', function() {
    searchPlace(this, fromSearch);
});

toInput.addEventListener('input', function() {
    searchPlace(this, toSearch);
});

// Ocultar resultados al hacer clic fuera
document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-container')) {
        fromSearch.style.display = 'none';
        toSearch.style.display = 'none';
    }
});

// Agregar control de ubicación (si el usuario permite geolocalización)
map.locate({setView: false, maxZoom: 19});

map.on('locationfound', function(e) {
    L.marker(e.latlng)
        .addTo(map)
        .bindPopup('¡Tu ubicación actual!')
        .openPopup();
});

// Analisis de ubicacion con IA
document.getElementById('imageForm').addEventListener('submit', function(e) {
    e.preventDefault();

    console.log("inicio")

    const formData = new FormData();
    const imageFile = document.getElementById('imagen').files[0];


    if (!imageFile) {
       alert("Por favor selecciona una imagen.");
       return;
    }

    formData.append('image', imageFile);

    fetch('/location/api/compare-imgs/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCookie('csrftoken') // Necesario para Django
        }
    })
    .then(response => response.json())
    .then(data => {
        lugar = data[0];
        console.log(lugar);
        goToPlace(lugar.coords[0], lugar.coords[1], lugar.nombre, (searchingByFromImage?fromInput:toInput), (searchingByFromImage?fromSearch:toSearch)); //Si, esto es la razon XD
        if(searchingByFromImage)
            fromLocation = lugar;
        else
            toLocation = lugar;

        if(fromLocation != null && toLocation != null) {
            calcRoute();
        }
    })
    .catch(error => {
        console.error('Error al enviar la imagen:', error);
    });
});

function drawRoute(route) {
    var polyline = L.polyline(route,
        {
            color: '#00FF00',
            fillColor: '#0f0',
            weight: 4,
            opacity: 0.8
        }).addTo(map);
    
    // Guardar la capa para poder limpiarla después si es necesario
    let capaRuta = polyline;
    polyline.bindPopup("✓ Ruta Recomendada").openPopup();
    
    // Opcional: Guardar la ruta para limpiarla después
    if (!window.rutaActual) window.rutaActual = [];
    window.rutaActual.push(capaRuta);
}

function calcRoute(from, to) {
    const formData = {
        "from": from.nombre,
        "to": to.nombre
    };

    fetch('/location/api/calcular-ruta/', {
        method: 'POST',
        body: JSON.stringify(formData), // 👈 Convertir a JSON
        headers: {
            'Content-Type': 'application/json', // 👈 Especificar tipo de contenido
            'X-CSRFToken': getCookie('csrftoken') // CSRF para Django
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor:", data);
        if (data[0].ruta_total) {
            drawRoute(data[0].ruta_total);
        } else {
            console.error("La respuesta no contiene 'ruta_total':", data);
            alert("No se pudo calcular la ruta.");
        }
    })
    .catch(error => {
        console.error('Error al calcular la ruta:', error);
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

