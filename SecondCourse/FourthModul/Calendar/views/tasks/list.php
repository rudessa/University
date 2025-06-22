<?php require_once 'views/layout/header.php'; ?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <h2><?= $title ?></h2>
    <a href="index.php" class="btn btn-primary">Создать новую задачу</a>
</div>

<?php if (empty($tasks)): ?>
    <div class="alert alert-info">Задачи не найдены</div>
<?php else: ?>
    <div class="row mb-3">
        <div class="col-md-4">
            <form action="index.php" method="get" class="form-inline">
                <input type="hidden" name="action" value="list">
                <input type="hidden" name="type" value="date">
                <input type="date" name="date" class="form-control mr-2" value="<?= date('Y-m-d') ?>">
                <button type="submit" class="btn btn-secondary">Показать</button>
            </form>
        </div>
    </div>

    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Тема</th>
                    <th>Тип</th>
                    <th>Место</th>
                    <th>Дата и время</th>
                    <th>Длительность</th>
                    <th>Статус</th>
                    <th>Действия</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($tasks as $task): ?>
                <tr class="<?= $task['status'] === 'overdue' ? 'table-danger' : ($task['status'] === 'completed' ? 'table-success' : '') ?>">
                    <td><a href="index.php?action=showTask&id=<?= $task['id'] ?>"><?= htmlspecialchars($task['title']) ?></a></td>
                    <td>
                        <?php
                        $typeLabels = [
                            'meeting' => 'Встреча',
                            'call' => 'Звонок',
                            'conference' => 'Совещание',
                            'task' => 'Дело'
                        ];
                        echo $typeLabels[$task['type']] ?? $task['type'];
                        ?>
                    </td>
                    <td><?= htmlspecialchars($task['location']) ?></td>
                    <td><?= date('d.m.Y H:i', strtotime($task['start_datetime'])) ?></td>
                    <td><?= $task['duration'] ?> мин</td>
                    <td>
                        <?php
                        $statusLabels = [
                            'pending' => 'Ожидает',
                            'completed' => 'Выполнено',
                            'overdue' => 'Просрочено'
                        ];
                        echo $statusLabels[$task['status']] ?? $task['status'];
                        ?>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <a href="index.php?action=showTask&id=<?= $task['id'] ?>" class="btn btn-info">Просмотр</a>
                            <?php if ($task['status'] !== 'completed'): ?>
                                <a href="index.php?action=markAsCompleted&id=<?= $task['id'] ?>" class="btn btn-success">Выполнить</a>
                            <?php endif; ?>
                            <a href="index.php?action=delete&id=<?= $task['id'] ?>" class="btn btn-danger" onclick="return confirm('Вы уверены, что хотите удалить эту задачу?')">Удалить</a>
                        </div>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
<?php endif; ?>

<?php require_once 'views/layout/footer.php'; ?>