let currentEditingId = null;
let isSubmitting = false;

window.formatText = (command) => {
    const editor = document.getElementById('text_editor');
    editor?.focus();
    document.execCommand(command, false, null);
    updateHiddenField();
};

const updateHiddenField = () => {
    const editor = document.getElementById('text_editor');
    const hiddenTextarea = document.getElementById('text');
    if (editor && hiddenTextarea) {
        hiddenTextarea.value = editor.innerHTML;
    }
};

const openModal = () => {
    ['number', 'title', 'link_approvement'].forEach(id => {
        document.getElementById(id).value = '';
    });
    document.getElementById('text_editor').innerHTML = '';
    document.getElementById('text').value = '';
    currentEditingId = null;
    document.getElementById('changeModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
};

const closeModal = () => {
    document.getElementById('changeModal').style.display = 'none';
    document.body.style.overflow = 'auto';
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('changeForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (isSubmitting) return;

            isSubmitting = true;
            updateHiddenField();

            const url = currentEditingId ? `/change/${currentEditingId}/edit/` : form.action;
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    closeModal();
                    window.location.reload();
                } else {
                    console.log('Ошибки формы:', data.errors);
                }
            })
            .catch(error => console.error('Ошибка:', error))
            .finally(() => isSubmitting = false);
        });
    }

    // Сворачивание/разворачивание
    document.querySelectorAll('.change-header').forEach(header => {
        header.addEventListener('click', (e) => {
            if (!e.target.closest('.change-actions')) {
                header.parentElement.classList.toggle('active');
            }
        });
    });

    // Закрытие модального окна
    const modal = document.getElementById('changeModal');
    if (modal) {
        let mouseDownInside = false;
        modal.addEventListener('mousedown', (e) => {
            mouseDownInside = e.target !== modal;
        });
        modal.addEventListener('click', (e) => {
            if (e.target === modal && !mouseDownInside) closeModal();
            mouseDownInside = false;
        });
    }

    // Прокрутка к изменению
    const changeData = sessionStorage.getItem('loadChangeData');
    if (changeData) {
        const { changeId } = JSON.parse(changeData);
        sessionStorage.removeItem('loadChangeData');

        setTimeout(() => {
            const changeElement = document.querySelector(`[data-change-id="${changeId}"]`);
            if (changeElement) {
                changeElement.classList.add('highlighted-change', 'active');
                changeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

                setTimeout(() => {
                    changeElement.classList.add('fade-out');
                    setTimeout(() => {
                        changeElement.classList.remove('highlighted-change', 'fade-out');
                    }, 500);
                }, 4500);
            }
        }, 100);
    }
});

// Редактирование изменения
const editChange = (changeId) => {
    fetch(`/change/${changeId}/edit/`)
        .then(response => response.json())
        .then(data => {
            openModal();
            setTimeout(() => {
                document.getElementById('text_editor').innerHTML = data.text;
                document.getElementById('text').value = data.text;
                document.getElementById('number').value = data.number || '';
                document.getElementById('title').value = data.title || '';
                document.getElementById('link_approvement').value = data.link_approvement || '';
                currentEditingId = changeId;
            }, 100);
        })
        .catch(error => console.error('Ошибка:', error));
};

// Отменить изменение
const cancelChange = (changeId) => {
    if (confirm('Вы уверены, что хотите отменить это изменение?')) {
        fetch(`/change/${changeId}/cancel/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => data.success && window.location.reload())
        .catch(error => console.error('Ошибка:', error));
    }
};

// Удалить изменение
const deleteChange = (changeId) => {
    if (confirm('Вы уверены, что хотите полностью удалить это изменение?')) {
        fetch(`/change/${changeId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-change-id="${changeId}"]`)?.remove();
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }
};