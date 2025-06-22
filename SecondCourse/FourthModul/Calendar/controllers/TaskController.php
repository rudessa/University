<?php
require_once 'models/Task.php';

class TaskController {
    private $taskModel;
    private $authController;
    
    public function __construct($pdo) {
        $this->taskModel = new Task($pdo);
        // Создаем экземпляр AuthController для проверки авторизации
        $this->authController = new AuthController($pdo);
        // Обновление статусов задач при каждом запросе
        $this->taskModel->updateStatuses();
    }
    
    // Проверка авторизации перед доступом к задачам
    private function checkAuth() {
        if (!$this->authController->isLoggedIn()) {
            header('Location: index.php?action=showLoginForm&message=auth_required');
            exit;
        }
        return $_SESSION['user_id'];
    }
    
    // Показ формы создания задачи
    public function showCreateForm() {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        require_once 'views/tasks/form.php';
    }
    
    // Обработка создания задачи
    public function create() {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $data = [
                'title' => $_POST['title'] ?? '',
                'type' => $_POST['type'] ?? 'task',
                'location' => $_POST['location'] ?? '',
                'start_datetime' => $_POST['start_datetime'] ?? date('Y-m-d H:i:s'),
                'duration' => (int)($_POST['duration'] ?? 30),
                'comment' => $_POST['comment'] ?? '',
                'user_id' => $userId // Обязательно сохраняем ID пользователя
            ];
            
            $taskId = $this->taskModel->create($data);
            
            if ($taskId) {
                header('Location: index.php?action=list');
                exit;
            } else {
                $error = 'Не удалось создать задачу';
                require_once 'views/tasks/form.php';
            }
        } else {
            // Если запрос не POST, перенаправляем на форму
            header('Location: index.php?action=showCreateForm');
            exit;
        }
    }
    
    // Показ списка текущих задач
    public function listTasks($type = 'current') {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        
        $tasks = [];
        $title = '';
        
        switch ($type) {
            case 'current':
                $tasks = $this->taskModel->getCurrentTasks($userId);
                $title = 'Текущие задачи';
                break;
            case 'overdue':
                $tasks = $this->taskModel->getOverdueTasks($userId);
                $title = 'Просроченные задачи';
                break;
            case 'completed':
                $tasks = $this->taskModel->getCompletedTasks($userId);
                $title = 'Выполненные задачи';
                break;
            case 'date':
                $date = $_GET['date'] ?? date('Y-m-d');
                $tasks = $this->taskModel->getTasksByDate($date, $userId);
                $title = 'Задачи на ' . date('d.m.Y', strtotime($date));
                break;
        }
        
        require_once 'views/tasks/list.php';
    }
    
    // Показ деталей задачи
    public function showTask($id) {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        
        // Получаем задачу и проверяем, принадлежит ли она текущему пользователю
        $task = $this->taskModel->getById($id, $userId);
        
        if (!$task) {
            header('Location: index.php?action=list');
            exit;
        }
        
        require_once 'views/tasks/detail.php';
    }
    
    // Обработка обновления задачи
    public function update($id) {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        
        // Сначала проверяем, принадлежит ли задача текущему пользователю
        $task = $this->taskModel->getById($id, $userId);
        
        if (!$task) {
            header('Location: index.php?action=list');
            exit;
        }
        
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $data = [
                ':title' => $_POST['title'] ?? '',
                ':type' => $_POST['type'] ?? 'task',
                ':location' => $_POST['location'] ?? '',
                ':start_datetime' => $_POST['start_datetime'] ?? date('Y-m-d H:i:s'),
                ':duration' => (int)($_POST['duration'] ?? 30),
                ':comment' => $_POST['comment'] ?? '',
                ':status' => $_POST['status'] ?? 'pending',
                ':user_id' => $userId // Добавляем для проверки владельца
            ];
            
            $success = $this->taskModel->update($id, $data);
            
            if ($success) {
                header('Location: index.php?action=list');
                exit;
            } else {
                $error = 'Не удалось обновить задачу';
                require_once 'views/tasks/detail.php';
            }
        } else {
            // Если запрос не POST, перенаправляем на страницу задачи
            header('Location: index.php?action=showTask&id=' . $id);
            exit;
        }
    }
    
    // Обработка удаления задачи
    public function delete($id) {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        
        // Удаляем задачу только если она принадлежит текущему пользователю
        $this->taskModel->delete($id, $userId);
        header('Location: index.php?action=list');
        exit;
    }
    
    // Отметка задачи как выполненной
    public function markAsCompleted($id) {
        $userId = $this->checkAuth(); // Проверяем авторизацию
        
        // Сначала проверяем, принадлежит ли задача текущему пользователю
        $task = $this->taskModel->getById($id, $userId);
        
        if (!$task) {
            header('Location: index.php?action=list');
            exit;
        }
        
        $data = [
            ':status' => 'completed',
            ':user_id' => $userId // Добавляем для проверки владельца
        ];
        
        $this->taskModel->update($id, $data);
        header('Location: index.php?action=list');
        exit;
    }
}