/**
 * forms.js — Client-side form UX enhancements.
 */

(function () {
    'use strict';

    /* Show/hide landlord contact when owns vs rents is selected */
    var ownsOrRents = document.getElementById('id_owns_or_rents');
    var landlordGroup = document.getElementById('landlord-contact-group');

    function toggleLandlordContact() {
        if (!ownsOrRents || !landlordGroup) {
            return;
        }
        var isRenting = ownsOrRents.value === 'rents';
        landlordGroup.style.display = isRenting ? '' : 'none';
    }

    if (ownsOrRents && landlordGroup) {
        toggleLandlordContact();
        ownsOrRents.addEventListener('change', toggleLandlordContact);
    }

    /* Character counter for textareas with maxlength */
    document.querySelectorAll('textarea[maxlength]').forEach(function (textarea) {
        var counter = document.createElement('span');
        counter.className = 'help-text char-counter';
        counter.setAttribute('aria-live', 'polite');
        textarea.parentNode.appendChild(counter);

        function updateCounter() {
            var max = parseInt(textarea.getAttribute('maxlength'), 10);
            var remaining = max - textarea.value.length;
            counter.textContent = remaining + ' characters remaining';
        }

        updateCounter();
        textarea.addEventListener('input', updateCounter);
    });

    /* Confirm dialog before delete forms */
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            var message = form.getAttribute('data-confirm');
            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    /* Prevent double submission */
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            var submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.setAttribute('aria-disabled', 'true');
            }
        });
    });
})();
