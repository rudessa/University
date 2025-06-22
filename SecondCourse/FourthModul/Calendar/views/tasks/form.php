<?php require_once 'views/layout/header.php'; ?>

<h2 class="mb-4">Создание новой задачи</h2>

<form action="index.php?action=create" method="post">
    <div class="form-group">
        <label for="title">Тема *</label>
        <input type="text" class="form-control" id="title" name="title" required>
    </div>
    
    <div class="form-group">
        <label for="type">Тип *</label>
        <select class="form-control" id="type" name="type" required>
            <option value="meeting">Встреча</option>
            <option value="call">Звонок</option>
            <option value="conference">Совещание</option>
            <option value="task">Дело</option>
        </select>
    </div>
    
    <div class="form-group">
        <label for="location">Место</label>
        <input type="text" class="form-control" id="location" name="location">
    </div>
    
    <div class="form-group">
        <label for="start_datetime">Дата и время *</label>
        <input type="datetime-local" class="form-control" id="start_datetime" name="start_datetime" required>
    </div>
    
    <div class="form-group">
        <label for="duration">Длительность (минут) *</label>
        <input type="number" class="form-control" id="duration" name="duration" min="1" value="30" required>
    </div>
    
    <div class="form-group">
        <label for="comment">Комментарий</label>
        <textarea class="form-control" id="comment" name="comment" rows="3"></textarea>
    </div>
    
    <button type="submit" class="btn btn-primary">Создать задачу</button>
    <a href="index.php?action=list" class="btn btn-secondary">Отмена</a>
</form>

<?php require_once 'views/layout/footer.php'; ?>