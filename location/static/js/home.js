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

// Función de búsqueda
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

searchInput.addEventListener('input', function() {
    const query = this.value.toLowerCase().trim();

    if (query.length < 2) {
        searchResults.style.display = 'none';
        return;
    }

    // Filtrar lugares que coincidan con la búsqueda
    const matches = lugareseafit.filter(lugar =>
        lugar.nombre.toLowerCase().includes(query) ||
        lugar.descripcion.toLowerCase().includes(query)
    );

    if (matches.length > 0) {
        searchResults.innerHTML = matches.map(lugar =>
            `<div class="search-item" onclick="goToPlace(${lugar.coords[0]}, ${lugar.coords[1]}, '${lugar.nombre}')">
                <strong>${lugar.nombre}</strong><br>
                <small>${lugar.descripcion}</small>
            </div>`
        ).join('');
        searchResults.style.display = 'block';
    } else {
        searchResults.innerHTML = '<div class="search-item">No se encontraron lugares</div>';
        searchResults.style.display = 'block';
    }
});

// Función para ir a un lugar específico
function goToPlace(lat, lng, nombre) {
    map.setView([lat, lng], 19);
    searchResults.style.display = 'none';
    searchInput.value = nombre;

    // Mostrar popup del lugar
    L.popup()
        .setLatLng([lat, lng])
        .setContent(`<b>¡Estás aquí!</b><br>${nombre}`)
        .openOn(map);
}

// Ocultar resultados al hacer clic fuera
document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-container')) {
        searchResults.style.display = 'none';
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
       lugar = data
       goToPlace(lugar.coords[0], lugar.coords[1], lugar.nombre)
    })
    .catch(error => {
        console.error('Error al enviar la imagen:', error);
    });
});


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

