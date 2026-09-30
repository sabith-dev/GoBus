document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    const navActions = document.querySelector('.nav-actions');
    const searchForm = document.getElementById('searchForm');
    const swapBtn = document.querySelector('.swap-btn');
    const fromInput = document.getElementById('from');
    const toInput = document.getElementById('to');
    const dateInput = document.getElementById('date');
    const passengersSelect = document.getElementById('passengers');
    const passengersInput = document.getElementById('passengersInput');

    if (dateInput) {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.min = today.toISOString().split('T')[0];
        dateInput.value = tomorrow.toISOString().split('T')[0];
    }

    if (passengersSelect && passengersInput) {
        passengersSelect.addEventListener('change', function() {
            if (this.value === 'more') {
                this.style.display = 'none';
                passengersInput.style.display = 'block';
                passengersInput.focus();
            }
        });

        passengersInput.addEventListener('blur', function() {
            if (!this.value || parseInt(this.value) < 6) {
                this.style.display = 'none';
                passengersSelect.style.display = 'block';
                passengersSelect.value = '5';
            }
        });

        passengersInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.blur();
            }
        });
    }

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-open');
            navActions.classList.toggle('mobile-open');
        });
    }

    if (swapBtn) {
        swapBtn.addEventListener('click', () => {
            const temp = fromInput.value;
            fromInput.value = toInput.value;
            toInput.value = temp;
        });
    }

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const from = fromInput.value.trim();
            const to = toInput.value.trim();
            const date = dateInput.value;
            const passengers = passengersSelect.style.display === 'none' 
                ? passengersInput.value 
                : passengersSelect.value;

            if (!from || !to) {
                alert('Please enter both departure and destination cities');
                return;
            }

            if (from.toLowerCase() === to.toLowerCase()) {
                alert('Departure and destination cities cannot be the same');
                return;
            }

            if (passengersSelect.style.display === 'none' && (!passengersInput.value || parseInt(passengersInput.value) < 6)) {
                alert('Please enter a valid passenger count (6 or more)');
                passengersInput.focus();
                return;
            }

            alert(`Searching for buses from ${from} to ${to} on ${date} for ${passengers} passenger(s)`);
        });
    }

    const animateStats = () => {
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-target'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            const updateStat = () => {
                current += step;
                if (current < target) {
                    if (target >= 1000000) {
                        stat.textContent = (current / 1000000).toFixed(1) + 'M';
                    } else if (target >= 1000) {
                        stat.textContent = Math.floor(current / 1000) + 'K';
                    } else {
                        stat.textContent = Math.floor(current);
                    }
                    requestAnimationFrame(updateStat);
                } else {
                    if (target >= 1000000) {
                        stat.textContent = (target / 1000000).toFixed(0) + 'M';
                    } else if (target >= 1000) {
                        stat.textContent = (target / 1000) + 'K';
                    } else {
                        stat.textContent = target;
                    }
                }
            };

            updateStat();
        });
    };

    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                statsObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const heroStats = document.querySelector('.hero-stats');
    if (heroStats) {
        statsObserver.observe(heroStats);
    }

    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.feature-card, .route-card, .testimonial-card');
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
        });

        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    scrollObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        elements.forEach(el => scrollObserver.observe(el));
    };

    animateOnScroll();

    const smoothScroll = (target) => {
        const element = document.querySelector(target);
        if (element) {
            const offsetTop = element.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    };

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href');
            if (target !== '#') {
                smoothScroll(target);
            }
        });
    });

    const searchInputs = document.querySelectorAll('.input-wrapper input');
    searchInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });

        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });

    const routeCards = document.querySelectorAll('.route-card');
    routeCards.forEach(card => {
        card.addEventListener('click', function() {
            const cities = this.querySelector('.route-cities');
            if (cities) {
                const fromCity = cities.querySelector('span:first-child').textContent;
                const toCity = cities.querySelector('span:last-child').textContent;
                fromInput.value = fromCity;
                toInput.value = toCity;
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    });
});
