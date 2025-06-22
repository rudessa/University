<?php
require_once 'models/User.php';

class AuthController {
    private $userModel;
    
    public function __construct($pdo) {
        $this->userModel = new User($pdo);
        
        // Запуск сессии, если еще не запущена
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }
    
    // Показ формы входа
    public function showLoginForm() {
        $message = $_GET['message'] ?? '';
        if ($message === 'auth_required') {
            $error = 'Для доступа к задачам необходимо войти в систему';
        }
        require_once 'views/auth/login.php';
    }
    
    // Обработка входа
    public function login() {
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $username = $_POST['username'] ?? '';
            $password = $_POST['password'] ?? '';
            
            $result = $this->userModel->login($username, $password);
            
            if ($result['success']) {
                $_SESSION['logged_in'] = true;
                $_SESSION['user_id'] = $result['user']['id'];
                $_SESSION['username'] = $result['user']['username'];
                
                header('Location: index.php');
                exit;
            } else {
                $error = $result['message'];
                require_once 'views/auth/login.php';
            }
        } else {
            // Если запрос не POST, перенаправляем на форму входа
            header('Location: index.php?action=showLoginForm');
            exit;
        }
    }
    
    // Показ формы регистрации
    public function showRegisterForm() {
        require_once 'views/auth/register.php';
    }
    
    // Обработка регистрации
    public function register() {
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $username = $_POST['username'] ?? '';
            $password = $_POST['password'] ?? '';
            $email = $_POST['email'] ?? null;
            
            $result = $this->userModel->register($username, $password, $email);
            
            if ($result['success']) {
                $_SESSION['logged_in'] = true;
                $_SESSION['user_id'] = $result['id'];
                $_SESSION['username'] = $username;
                
                header('Location: index.php');
                exit;
            } else {
                $error = $result['message'];
                require_once 'views/auth/register.php';
            }
        } else {
            // Если запрос не POST, перенаправляем на форму регистрации
            header('Location: index.php?action=showRegisterForm');
            exit;
        }
    }
    
    // Обработка выхода
    public function logout() {
        // Уничтожаем все данные сессии
        session_unset();
        session_destroy();
        
        // После выхода перенаправляем на форму входа, 
        // а не на главную страницу, чтобы предотвратить доступ к задачам
        header('Location: index.php?action=showLoginForm');
        exit;
    }
    
    // Проверка авторизации
    public function isLoggedIn() {
        return isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true;
    }
    
    // Метод для перенаправления на главную страницу если уже авторизован
    public function redirectIfLoggedIn() {
        if ($this->isLoggedIn()) {
            header('Location: index.php');
            exit;
        }
    }
}