<?php require_once 'views/layout/header.php'; ?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <h2>Редактирование задачи</h2>
    <div>
        <a href="index.php?action=list" class="btn btn-secondary">Назад к списку</a>
        <?php if ($task['status'] !== 'completed'): ?>
            <a href="index.php?action=markAsCompleted&id=<?= $task['id'] ?>" class="btn btn-success">Отметить как выполненную</a>
        <?php endif; ?>
    </div>
</div>

<form action="index.php?action=update&id=<?= $task['id'] ?>" method="post">
    <div class="form-group">
        <label for="title">Тема *</label>
        <input type="text" class="form-control" id="title" name="title" value="<?= htmlspecialchars($task['title']) ?>" required>
    </div>
    
    <div class="form-group">
        <label for="type">Тип *</label>
        <select class="form-control" id="type" name="type" required>
            <option value="meeting" <?= $task['type'] === 'meeting' ? 'selected' : '' ?>>Встреча</option>
            <option value="call" <?= $task['type'] === 'call' ? 'selected' : '' ?>>Звонок</option>
            <option value="conference" <?= $task['type'] === 'conference' ? 'selected' : '' ?>>Совещание</option>
            <option value="task" <?= $task['type'] === 'task' ? 'selected' : '' ?>>Дело</option>
        </select>
    </div>
    
    <div class="form-group">
        <label for="location">Место</label>
        <input type="text" class="form-control" id="location" name="location" value="<?= htmlspecialchars($task['location']) ?>">
    </div>
    
    <div class="form-group">
        <label for="start_datetime">Дата и время *</label>
        <input type="datetime-local" class="form-control" id="start_datetime" name="start_datetime" value="<?= date('Y-m-d\TH:i', strtotime($task['start_datetime'])) ?>" required>
    </div>
    
    <div class="form-group">
        <label for="duration">Длительность (минут) *</label>
        <input type="number" class="form-control" id="duration" name="duration" min="1" value="<?= $task['duration'] ?>" required>
    </div>
    
    <div class="form-group">
        <label for="comment">Комментарий</label>
        <textarea class="form-control" id="comment" name="comment" rows="3"><?= htmlspecialchars($task['comment']) ?></textarea>
    </div>
    
    <div class="form-group">
        <label for="status">Статус</label>
        <select class="form-control" id="status" name="status">
            <option value="pending" <?= $task['status'] === 'pending' ? 'selected' : '' ?>>Ожидает</option>
            <option value="completed" <?= $task['status'] === 'completed' ? 'selected' : '' ?>>Выполнено</option>
            <option value="overdue" <?= $task['status'] === 'overdue' ? 'selected' : '' ?>>Просрочено</option>
        </select>
    </div>
    
    <button type="submit" class="btn btn-primary">Сохранить изменения</button>
    <a href="index.php?action=delete&id=<?= $task['id'] ?>" class="btn btn-danger" onclick="return confirm('Вы уверены, что хотите удалить эту задачу?')">Удалить задачу</a>
</form>

<?php require_once 'views/layout/footer.php'; ?>