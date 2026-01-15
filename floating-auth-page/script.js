document.addEventListener('DOMContentLoaded', () => {
    // --- Tab Switching Logic ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');
    const tabIndicator = document.querySelector('.tab-indicator');

    function updateIndicator(btn) {
        tabIndicator.style.width = btn.offsetWidth + 'px';
        tabIndicator.style.left = btn.offsetLeft + 'px';
    }

    // Initial indicator position
    const activeBtn = document.querySelector('.tab-btn.active');
    if (activeBtn) updateIndicator(activeBtn);

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            // Update indicator
            updateIndicator(btn);

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update forms with fade effect
            forms.forEach(form => {
                form.classList.remove('active');
                if (form.id === `${targetTab}-form`) {
                    setTimeout(() => form.classList.add('active'), 50);
                }
            });

            // Update Header Text
            const headerH1 = document.querySelector('.auth-header h1');
            const headerP = document.querySelector('.auth-header p');
            if (targetTab === 'signup') {
                headerH1.textContent = 'Join the Mission';
                headerP.textContent = 'Begin your enterprise journey today.';
            } else {
                headerH1.textContent = 'Welcome Back';
                headerP.textContent = 'Manage your enterprise workspace with ease.';
            }
        });
    });

    // --- Switch Link Logic ---
    const switchToSignin = document.querySelector('.switch-to-signin');
    if (switchToSignin) {
        switchToSignin.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector('.tab-btn[data-tab="signin"]').click();
        });
    }

    // --- Password Toggle Logic ---
    const toggleBtns = document.querySelectorAll('.toggle-password');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.parentElement.querySelector('input');
            const icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });
    });

    // --- Form Submission & API Call Logic ---
    const formsList = document.querySelectorAll('.auth-form');
    formsList.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = form.querySelector('.btn-primary');
            btn.classList.add('loading');
            btn.disabled = true;

            try {
                if (form.id === 'signin-form') {
                    // Sign In Logic
                    const username = document.getElementById('login-username').value;
                    const password = document.getElementById('login-password').value;

                    if (!username || !password) {
                        showValidation(document.getElementById('login-password'), 'Please fill all fields');
                        btn.classList.remove('loading');
                        btn.disabled = false;
                        return;
                    }

                    const response = await fetch('http://localhost:5000/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });

                    const data = await response.json();

                    if (data.success) {
                        localStorage.setItem('user', JSON.stringify(data.user));
                        window.location.href = `http://localhost:8501?user=${data.user.username}`;
                    } else {
                        showValidation(document.getElementById('login-password'), data.message || 'Login failed');
                        btn.classList.remove('loading');
                        btn.disabled = false;
                    }

                } else if (form.id === 'signup-form') {
                    // Sign Up Logic
                    const fullName = document.getElementById('reg-fullname').value;
                    const username = document.getElementById('reg-username').value;
                    const email = document.getElementById('reg-email').value;
                    const pass = document.getElementById('reg-password').value;
                    const confirm = document.getElementById('reg-confirm-password').value;

                    // Validation
                    if (!fullName || !username || !email || !pass || !confirm) {
                        showValidation(form.querySelector('.floating-input'), 'Please fill all fields');
                        btn.classList.remove('loading');
                        btn.disabled = false;
                        return;
                    }

                    if (pass !== confirm) {
                        showValidation(document.getElementById('reg-confirm-password'), 'Passwords do not match');
                        btn.classList.remove('loading');
                        btn.disabled = false;
                        return;
                    }

                    if (pass.length < 8) {
                        showValidation(document.getElementById('reg-password'), 'Password must be at least 8 characters');
                        btn.classList.remove('loading');
                        btn.disabled = false;
                        return;
                    }

                    const response = await fetch('http://localhost:5000/api/signup', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            full_name: fullName,
                            username: username,
                            email: email,
                            password: pass
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        alert('Account created successfully! Please sign in.');
                        document.querySelector('.tab-btn[data-tab="signin"]').click();
                        form.reset();
                        btn.classList.remove('loading');
                        btn.disabled = false;
                    } else {
                        showValidation(form.querySelector('.floating-input'), data.message || 'Signup failed');
                        btn.classList.remove('loading');
                        btn.disabled = false;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                showValidation(form.querySelector('.floating-input'), 'Network error. Is backend running on localhost:5000?');
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        });
    });

    // --- Helper: Validation Message ---
    function showValidation(input, message) {
        const group = input.closest('.input-group');
        let msgEl = group.querySelector('.validation-msg');

        if (!msgEl) {
            msgEl = document.createElement('div');
            msgEl.className = 'validation-msg';
            group.appendChild(msgEl);
        }

        msgEl.textContent = message;
        msgEl.style.display = 'block';

        const wrapper = group.querySelector('.field-wrapper');
        wrapper.style.borderColor = '#ef4444';

        setTimeout(() => {
            msgEl.style.display = 'none';
            wrapper.style.borderColor = '';
        }, 3000);
    }

    // Handle initial indicator resize
    window.addEventListener('resize', () => {
        const active = document.querySelector('.tab-btn.active');
        if (active) updateIndicator(active);
    });
});