// Установка текущей даты и времени для поля start_datetime при создании новой задачи
document.addEventListener('DOMContentLoaded', function() {
    const startDateTimeInput = document.getElementById('start_datetime');
    
    if (startDateTimeInput && !startDateTimeInput.value) {
        const now = new Date();
        // Форматирование даты и времени в формат yyyy-MM-ddThh:mm
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        startDateTimeInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }
});