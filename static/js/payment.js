document.addEventListener('DOMContentLoaded', function() {
    const paymentMethods = document.querySelectorAll('.payment-method');

    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            paymentMethods.forEach(m => m.classList.remove('active'));
            this.classList.add('active');

            const methodType = this.dataset.method;
            document.querySelectorAll('.payment-form').forEach(form => {
                form.style.display = 'none';
            });

            const targetForm = document.getElementById(methodType + 'Form');
            if (targetForm) {
                targetForm.style.display = 'block';
            }
        });
    });

    // Card number formatting
    const cardInput = document.querySelector('input[name="card_number"]');
    if (cardInput) {
        cardInput.addEventListener('input', function() {
            let value = this.value.replace(/\s/g, '').replace(/[^0-9]/g, '');
            let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
            this.value = formatted;
        });
    }

    // Expiry date formatting
    const expiryInput = document.querySelector('input[name="card_expiry"]');
    if (expiryInput) {
        expiryInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            this.value = value;
        });
    }
});
