document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative';
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);

        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'btn btn-outline-secondary position-absolute top-50 end-0 translate-middle-y';
        toggle.innerHTML = '<i class="fas fa-eye"></i>';
        toggle.style.cssText = 'right: 10px; border: none; background: none;';
        wrapper.appendChild(toggle);

        toggle.addEventListener('click', function() {
            const type = field.getAttribute('type') === 'password' ? 'text' : 'password';
            field.setAttribute('type', type);
            toggle.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
        });
    });

    // OTP input auto-focus
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', function() {
            if (this.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });
    });
});
