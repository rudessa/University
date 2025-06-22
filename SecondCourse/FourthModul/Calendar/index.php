<?php
// Запуск сессии
session_start();

// Подключение конфигурации базы данных
require_once 'config/database.php';

// Подключение контроллеров
require_once 'controllers/TaskController.php';
require_once 'controllers/AuthController.php';

// Создание экземпляров контроллеров
$authController = new AuthController($pdo);
$taskController = new TaskController($pdo);

// Обработка действий
$action = $_GET['action'] ?? 'showCreateForm';
$id = $_GET['id'] ?? null;
$type = $_GET['type'] ?? 'current';

// Маршрутизация
switch ($action) {
    // Аутентификация
    case 'showLoginForm':
        $authController->showLoginForm();
        break;
    case 'login':
        $authController->login();
        break;
    case 'showRegisterForm':
        $authController->showRegisterForm();
        break;
    case 'register':
        $authController->register();
        break;
    case 'logout':
        $authController->logout();
        break;
    
    // Задачи - доступ только авторизованным пользователям
    case 'showCreateForm':
    case 'create':
    case 'list':
    case 'showTask':
    case 'update':
    case 'delete':
    case 'markAsCompleted':
        // Проверка авторизации происходит внутри методов TaskController
        switch ($action) {
            case 'showCreateForm':
                $taskController->showCreateForm();
                break;
            case 'create':
                $taskController->create();
                break;
            case 'list':
                $taskController->listTasks($type);
                break;
            case 'showTask':
                $taskController->showTask($id);
                break;
            case 'update':
                $taskController->update($id);
                break;
            case 'delete':
                $taskController->delete($id);
                break;
            case 'markAsCompleted':
                $taskController->markAsCompleted($id);
                break;
        }
        break;
    
    // По умолчанию - если авторизован, то форма создания задачи,
    // иначе форма входа
    default:
        if ($authController->isLoggedIn()) {
            $taskController->showCreateForm();
        } else {
            $authController->showLoginForm();
        }
        break;
}
?>