/**
 * Agenda de Turnos - Frontend Controller (Vanilla JS)
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.getElementById('search-input');
    const filterDate = document.getElementById('filter-date');
    const btnClearDate = document.getElementById('btn-clear-date');
    const statusTabs = document.querySelectorAll('.status-tab');
    const appointmentsGrid = document.getElementById('appointments-grid');
    const emptyState = document.getElementById('empty-state');
    const loadingIndicator = document.getElementById('loading-indicator');
    const appointmentsCount = document.getElementById('appointments-count');
    const appointmentForm = document.getElementById('appointment-form');
    const modal = document.getElementById('appointment-modal');
    
    // Stats Elements
    const statTotalVal = document.querySelector('#stat-total .stat-value');
    const statPendingVal = document.querySelector('#stat-pending .stat-value');
    const statConfirmedVal = document.querySelector('#stat-confirmed .stat-value');
    const statCompletedVal = document.querySelector('#stat-completed .stat-value');
    
    // Application State
    let currentFilters = {
        search: '',
        date: '',
        status: 'all'
    };
    let debounceTimer;

    // Initialize
    init();

    function init() {
        // Setup Date picker default restraints (min today)
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('appointment_date').min = today;

        // Event Listeners
        searchInput.addEventListener('input', handleSearchInput);
        filterDate.addEventListener('change', handleDateFilterChange);
        btnClearDate.addEventListener('click', clearDateFilter);
        
        statusTabs.forEach(tab => {
            tab.addEventListener('click', handleStatusTabClick);
        });

        appointmentForm.addEventListener('submit', handleFormSubmit);

        // Load initial appointments
        fetchAppointments();
    }

    /* ==========================================================================
       API / Fetch Functions
       ========================================================================== */
    
    /**
     * Fetches appointments from the server and updates UI
     */
    async function fetchAppointments() {
        showLoading(true);
        
        // Build query string
        const params = new URLSearchParams();
        if (currentFilters.search) params.append('search', currentFilters.search);
        if (currentFilters.date) params.append('date', currentFilters.date);
        if (currentFilters.status) params.append('status', currentFilters.status);

        try {
            const response = await fetch(`/api/appointments?${params.toString()}`);
            if (!response.ok) throw new Error('Error al obtener los datos del servidor');
            
            const appointments = await response.json();
            renderAppointments(appointments);
            updateStats();
        } catch (error) {
            console.error(error);
            showToast('No se pudieron cargar los turnos. Intente de nuevo.', 'error');
        } finally {
            showLoading(false);
        }
    }

    /**
     * Updates only the stats dashboard based on unfiltered status counts from DB
     */
    async function updateStats() {
        try {
            // Fetch all appointments (no filters) to calculate dashboard totals
            const response = await fetch('/api/appointments');
            if (!response.ok) throw new Error();
            const allAppointments = await response.json();

            let total = allAppointments.length;
            let pending = allAppointments.filter(a => a.status === 'Pending').length;
            let confirmed = allAppointments.filter(a => a.status === 'Confirmed').length;
            let completed = allAppointments.filter(a => a.status === 'Completed').length;

            // Animate number updates
            animateValue(statTotalVal, parseInt(statTotalVal.textContent) || 0, total, 400);
            animateValue(statPendingVal, parseInt(statPendingVal.textContent) || 0, pending, 400);
            animateValue(statConfirmedVal, parseInt(statConfirmedVal.textContent) || 0, confirmed, 400);
            animateValue(statCompletedVal, parseInt(statCompletedVal.textContent) || 0, completed, 400);

        } catch (error) {
            console.error('Error al actualizar estadísticas:', error);
        }
    }

    /* ==========================================================================
       UI Rendering Functions
       ========================================================================== */

    /**
     * Renders appointment cards in the main board
     */
    function renderAppointments(appointments) {
        appointmentsCount.textContent = `${appointments.length} ${appointments.length === 1 ? 'turno encontrado' : 'turnos encontrados'}`;

        if (appointments.length === 0) {
            appointmentsGrid.style.display = 'none';
            emptyState.style.display = 'flex';
            return;
        }

        emptyState.style.display = 'none';
        appointmentsGrid.innerHTML = '';
        appointmentsGrid.style.display = 'grid';

        appointments.forEach(appointment => {
            const card = createAppointmentCard(appointment);
            appointmentsGrid.appendChild(card);
        });
    }

    /**
     * Creates an HTML card element for a single appointment record
     */
    function createAppointmentCard(appointment) {
        const card = document.createElement('article');
        card.className = `appointment-card status-${appointment.status}`;
        card.id = `appointment-card-${appointment.id}`;

        // Format date: YYYY-MM-DD -> DD/MM/YYYY
        const [year, month, day] = appointment.appointment_date.split('-');
        const formattedDate = `${day}/${month}/${year}`;

        // Map status names for badges
        const statusTranslations = {
            'Pending': 'Pendiente',
            'Confirmed': 'Confirmado',
            'Completed': 'Completado',
            'Cancelled': 'Cancelado'
        };

        const statusLabel = statusTranslations[appointment.status] || appointment.status;

        // Notes placeholder
        const notesContent = appointment.notes 
            ? appointment.notes 
            : 'Sin observaciones adicionales.';

        // Card HTML Structure
        card.innerHTML = `
            <div class="card-header">
                <span class="card-service">${appointment.service}</span>
                <span class="card-status-badge">${statusLabel}</span>
            </div>
            
            <div class="card-client-name">
                <i class="fa-solid fa-user-circle"></i> ${escapeHTML(appointment.client_name)}
            </div>

            <div class="card-details">
                <div class="detail-item">
                    <span class="detail-label">Fecha</span>
                    <span class="detail-val"><i class="fa-solid fa-calendar-alt"></i> ${formattedDate}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Hora</span>
                    <span class="detail-val"><i class="fa-solid fa-clock"></i> ${appointment.appointment_time} hs</span>
                </div>
                <div class="detail-item" style="grid-column: span 2; margin-top: 4px;">
                    <span class="detail-label">Contacto</span>
                    <span class="detail-val">
                        <i class="fa-solid fa-phone"></i> ${escapeHTML(appointment.client_phone)}
                        ${appointment.client_email ? ` | <i class="fa-solid fa-envelope"></i> ${escapeHTML(appointment.client_email)}` : ''}
                    </span>
                </div>
            </div>

            <div class="card-notes" title="${escapeHTML(notesContent)}">
                ${escapeHTML(notesContent)}
            </div>

            <div class="card-actions">
                ${getActionButtons(appointment)}
            </div>
        `;

        // Set up event listeners for buttons within card
        setupCardEvents(card, appointment);

        return card;
    }

    /**
     * Renders action buttons dynamically based on status
     */
    function getActionButtons(appointment) {
        let buttons = '';

        // All appointments allow editing and deletion/removal
        buttons += `
            <button class="btn btn-secondary btn-sm btn-edit" title="Editar Turno">
                <i class="fa-solid fa-pen"></i>
            </button>
            <button class="btn btn-danger btn-sm btn-delete" title="Eliminar Turno">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        `;

        // Quick status changes based on state
        if (appointment.status === 'Pending') {
            buttons = `
                <button class="btn btn-success btn-sm btn-confirm" title="Confirmar Turno">
                    <i class="fa-solid fa-check"></i> Confirmar
                </button>
            ` + buttons;
        } else if (appointment.status === 'Confirmed') {
            buttons = `
                <button class="btn btn-primary btn-sm btn-complete" title="Completar Turno">
                    <i class="fa-solid fa-circle-check"></i> Completar
                </button>
            ` + buttons;
        }

        return buttons;
    }

    /**
     * Links event listeners to dynamically created card buttons
     */
    function setupCardEvents(card, appointment) {
        // Edit button
        card.querySelector('.btn-edit').addEventListener('click', () => {
            editAppointment(appointment);
        });

        // Delete button
        card.querySelector('.btn-delete').addEventListener('click', () => {
            deleteAppointment(appointment.id, appointment.client_name);
        });

        // Quick action: Confirm
        const btnConfirm = card.querySelector('.btn-confirm');
        if (btnConfirm) {
            btnConfirm.addEventListener('click', () => {
                updateAppointmentStatus(appointment.id, 'Confirmed');
            });
        }

        // Quick action: Complete
        const btnComplete = card.querySelector('.btn-complete');
        if (btnComplete) {
            btnComplete.addEventListener('click', () => {
                updateAppointmentStatus(appointment.id, 'Completed');
            });
        }
    }

    /* ==========================================================================
       CRUD Event Actions
       ========================================================================== */

    /**
     * Populates form and opens modal for editing
     */
    async function editAppointment(appointment) {
        // Clear errors
        clearFormErrors();
        
        document.getElementById('appointment-id').value = appointment.id;
        document.getElementById('client_name').value = appointment.client_name;
        document.getElementById('client_phone').value = appointment.client_phone;
        document.getElementById('client_email').value = appointment.client_email || '';
        document.getElementById('appointment_date').value = appointment.appointment_date;
        document.getElementById('appointment_time').value = appointment.appointment_time;
        document.getElementById('service').value = appointment.service;
        document.getElementById('status').value = appointment.status;

        // Open modal via public globally scoped function
        window.openModal(true);
    }

    /**
     * Sends PUT request to update status of an appointment
     */
    async function updateAppointmentStatus(id, newStatus) {
        try {
            // Get original data first
            const getRes = await fetch(`/api/appointments/${id}`);
            if (!getRes.ok) throw new Error();
            const appointment = await getRes.json();

            // Set new status and send PUT
            appointment.status = newStatus;

            const putRes = await fetch(`/api/appointments/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(appointment)
            });

            if (!putRes.ok) {
                const errData = await putRes.json();
                throw new Error(errData.error || 'Error al actualizar el estado.');
            }

            showToast(`Turno actualizado a "${newStatus === 'Confirmed' ? 'Confirmado' : 'Completado'}"`, 'success');
            fetchAppointments();
        } catch (error) {
            console.error(error);
            showToast(error.message || 'No se pudo actualizar el estado del turno.', 'error');
        }
    }

    /**
     * Sends DELETE request to remove appointment
     */
    async function deleteAppointment(id, clientName) {
        if (!confirm(`¿Está seguro de que desea eliminar el turno reservado para "${clientName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/appointments/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error();

            showToast('Turno eliminado correctamente', 'success');
            fetchAppointments();
        } catch (error) {
            console.error(error);
            showToast('No se pudo eliminar el turno. Intente nuevamente.', 'error');
        }
    }

    /**
     * Validates and submits modal form data (Create or Update)
     */
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        if (!validateForm()) return;

        const appointmentId = document.getElementById('appointment-id').value;
        const isEdit = !!appointmentId;

        // Gather form data
        const data = {
            client_name: document.getElementById('client_name').value.trim(),
            client_phone: document.getElementById('client_phone').value.trim(),
            client_email: document.getElementById('client_email').value.trim(),
            appointment_date: document.getElementById('appointment_date').value,
            appointment_time: document.getElementById('appointment_time').value,
            service: document.getElementById('service').value,
            notes: document.getElementById('notes').value.trim()
        };

        if (isEdit) {
            data.status = document.getElementById('status').value;
        }

        const url = isEdit ? `/api/appointments/${appointmentId}` : '/api/appointments';
        const method = isEdit ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                if (result.errors) {
                    // Display validation errors returned from the server
                    showServerErrors(result.errors);
                    showToast('Por favor, revise los campos con errores.', 'error');
                } else {
                    throw new Error(result.error || 'Ocurrió un error en el servidor.');
                }
                return;
            }

            showToast(isEdit ? 'Cambios guardados con éxito.' : 'Turno reservado correctamente.', 'success');
            window.closeModal();
            fetchAppointments();
        } catch (error) {
            console.error(error);
            showToast(error.message || 'No se pudo guardar la reserva.', 'error');
        }
    }

    /* ==========================================================================
       Form Validation Helpers
       ========================================================================== */

    function validateForm() {
        let isValid = true;
        clearFormErrors();

        const nameInput = document.getElementById('client_name');
        const phoneInput = document.getElementById('client_phone');
        const emailInput = document.getElementById('client_email');
        const dateInput = document.getElementById('appointment_date');
        const timeInput = document.getElementById('appointment_time');
        const serviceInput = document.getElementById('service');

        // Name validation
        if (!nameInput.value.trim()) {
            showFieldError('client_name', 'El nombre del cliente es obligatorio.');
            isValid = false;
        } else if (nameInput.value.trim().length < 3) {
            showFieldError('client_name', 'El nombre debe tener al menos 3 caracteres.');
            isValid = false;
        }

        // Phone validation
        if (!phoneInput.value.trim()) {
            showFieldError('client_phone', 'El teléfono de contacto es obligatorio.');
            isValid = false;
        }

        // Email validation (optional)
        if (emailInput.value.trim()) {
            const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
            if (!emailRegex.test(emailInput.value.trim())) {
                showFieldError('client_email', 'El correo electrónico no es válido.');
                isValid = false;
            }
        }

        // Date validation
        if (!dateInput.value) {
            showFieldError('appointment_date', 'La fecha de la cita es obligatoria.');
            isValid = false;
        }

        // Time validation
        if (!timeInput.value) {
            showFieldError('appointment_time', 'La hora de la cita es obligatoria.');
            isValid = false;
        }

        // Service validation
        if (!serviceInput.value) {
            showFieldError('service', 'Debe seleccionar un servicio.');
            isValid = false;
        }

        return isValid;
    }

    function showFieldError(fieldId, message) {
        const errorSpan = document.getElementById(`error-${fieldId}`);
        const inputWrapper = document.getElementById(fieldId).closest('.input-wrapper');
        
        if (errorSpan) {
            errorSpan.textContent = message;
            errorSpan.classList.add('visible');
        }
        if (inputWrapper) {
            inputWrapper.classList.add('invalid');
        }
    }

    function clearFormErrors() {
        document.querySelectorAll('.error-message').forEach(span => {
            span.classList.remove('visible');
            span.textContent = '';
        });
        document.querySelectorAll('.input-wrapper').forEach(wrapper => {
            wrapper.classList.remove('invalid');
        });
    }

    function showServerErrors(errors) {
        Object.keys(errors).forEach(fieldId => {
            showFieldError(fieldId, errors[fieldId]);
        });
    }

    /* ==========================================================================
       Filter Handlers
       ========================================================================== */

    function handleSearchInput(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            currentFilters.search = e.target.value.trim();
            fetchAppointments();
        }, 300); // 300ms debounce
    }

    function handleDateFilterChange(e) {
        currentFilters.date = e.target.value;
        if (currentFilters.date) {
            btnClearDate.style.display = 'block';
        } else {
            btnClearDate.style.display = 'none';
        }
        fetchAppointments();
    }

    function clearDateFilter() {
        filterDate.value = '';
        currentFilters.date = '';
        btnClearDate.style.display = 'none';
        fetchAppointments();
    }

    function handleStatusTabClick(e) {
        const selectedTab = e.currentTarget;
        
        // Update active class
        statusTabs.forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        selectedTab.classList.add('active');
        selectedTab.setAttribute('aria-selected', 'true');

        currentFilters.status = selectedTab.getAttribute('data-status');
        fetchAppointments();
    }

    /* ==========================================================================
       General Utility Functions
       ========================================================================== */

    function showLoading(show) {
        if (show) {
            loadingIndicator.style.display = 'flex';
            appointmentsGrid.style.display = 'none';
            emptyState.style.display = 'none';
        } else {
            loadingIndicator.style.display = 'none';
        }
    }

    /**
     * Prevents XSS injections when rendering user data in HTML
     */
    function escapeHTML(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Toast notification trigger helper
     */
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Define icons based on type
        const icons = {
            'success': 'fa-solid fa-circle-check',
            'error': 'fa-solid fa-circle-exclamation',
            'info': 'fa-solid fa-circle-info'
        };
        const iconClass = icons[type] || icons['info'];

        toast.innerHTML = `
            <i class="${iconClass} toast-icon"></i>
            <span class="toast-message">${escapeHTML(message)}</span>
        `;
        
        container.appendChild(toast);
        
        // Trigger show class for transition entry
        setTimeout(() => toast.classList.add('show'), 50);

        // Auto remove toast after 4000ms
        setTimeout(() => {
            toast.classList.remove('show');
            // Remove from DOM after transition out
            toast.addEventListener('transitionend', () => {
                toast.remove();
            });
        }, 4000);
    }

    /**
     * Helper to animate stats values updates
     */
    function animateValue(obj, start, end, duration) {
        if (start === end) return;
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                obj.innerHTML = end;
            }
        };
        window.requestAnimationFrame(step);
    }
});
