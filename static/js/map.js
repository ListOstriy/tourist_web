ymaps.ready(function () {
    // 1. Сначала пытаемся определить, где находится пользователь
    ymaps.geolocation.get({
        provider: 'yandex', // Используем данные Яндекса (по IP)
        mapStateAutoApply: true // Карта сама "прилетит" в этот город
    }).then(function (result) {
        // 2. Создаем карту в том месте, которое определил Яндекс
        var myMap = new ymaps.Map("map", {
            center: result.geoObjects.get(0).geometry.getCoordinates(),
            zoom: 12,
            controls: ['zoomControl']
        });

        // 3. (Опционально) Ставим метку там, где "нашли" человека
        myMap.geoObjects.add(result.geoObjects);
    }, function (err) {
        // Если человек запретил доступ к геопозиции или что-то сломалось — 
        // просто рисуем карту на Екатеринбурге!!!!!!!!!!!!! (запасной вариант)
        var myMap = new ymaps.Map("map", {
            center: [56.838607, 60.605514],
            zoom: 12
        });
        console.log("Не удалось определить город.");
    });
    myMap.options.set({
    restrictMapArea: [[-85, -179], [85, 179]],
    minZoom: 3, // На 2 зуме серое всё равно может вылезать по бокам
    maxZoom: 18
});
});
