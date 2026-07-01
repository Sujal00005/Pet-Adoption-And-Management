/**
 * pets.js — Pet browsing page breed filter and detail page photo gallery.
 */

(function () {
    'use strict';

    /* ------------------------------------------------------------------
       Breed dropdown — updates options when species changes (browse page)
    ------------------------------------------------------------------ */
    var speciesSelect = document.querySelector('[data-breeds-source]');
    var breedSelect = document.getElementById('id_breed_select');

    if (speciesSelect && breedSelect) {
        var breedsBySpecies = {};
        var breedsScript = document.getElementById(
            speciesSelect.getAttribute('data-breeds-source') || 'breeds-data'
        );

        try {
            breedsBySpecies = breedsScript
                ? JSON.parse(breedsScript.textContent)
                : {};
        } catch (e) {
            breedsBySpecies = {};
        }

        var selectedBreed = breedSelect.value;

        function populateBreeds(species) {
            var current = breedSelect.value;
            breedSelect.innerHTML = '';

            var defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Any Breed';
            breedSelect.appendChild(defaultOption);

            var breeds = breedsBySpecies[species] || [];
            breeds.forEach(function (breed) {
                var option = document.createElement('option');
                option.value = breed;
                option.textContent = breed;
                if (breed === current || breed === selectedBreed) {
                    option.selected = true;
                }
                breedSelect.appendChild(option);
            });
        }

        populateBreeds(speciesSelect.value);

        speciesSelect.addEventListener('change', function () {
            breedSelect.value = '';
            populateBreeds(speciesSelect.value);
        });
    }

    /* ------------------------------------------------------------------
       Photo gallery — previous / next and thumbnail navigation (detail page)
    ------------------------------------------------------------------ */
    var galleryImages = Array.prototype.slice.call(
        document.querySelectorAll('img[data-gallery]')
    );
    var mainImage = document.getElementById('gallery-current');
    var prevBtn = document.getElementById('gallery-prev');
    var nextBtn = document.getElementById('gallery-next');
    var thumbs = document.querySelectorAll('[data-gallery-index]');

    if (!mainImage || galleryImages.length <= 1) {
        return;
    }

    var currentIndex = parseInt(mainImage.getAttribute('data-index') || '0', 10);

    function showImage(index) {
        if (index < 0) {
            index = galleryImages.length - 1;
        } else if (index >= galleryImages.length) {
            index = 0;
        }

        currentIndex = index;
        var img = galleryImages[currentIndex];
        mainImage.src = img.src;
        mainImage.alt = img.alt;
        mainImage.setAttribute('data-index', String(currentIndex));

        thumbs.forEach(function (thumb) {
            var thumbIndex = parseInt(thumb.getAttribute('data-gallery-index'), 10);
            thumb.classList.toggle('active', thumbIndex === currentIndex);
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            showImage(currentIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            showImage(currentIndex + 1);
        });
    }

    thumbs.forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            var index = parseInt(thumb.getAttribute('data-gallery-index'), 10);
            showImage(index);
        });
    });
})();
