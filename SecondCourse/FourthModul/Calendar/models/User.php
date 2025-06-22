<?php
class User {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    // Регистрация нового пользователя
    public function register($username, $password, $email = null) {
        try {
            // Проверка на существующего пользователя
            $stmt = $this->pdo->prepare("SELECT id FROM users WHERE username = :username OR email = :email");
            $stmt->execute([
                ':username' => $username,
                ':email' => $email
            ]);
            
            if ($stmt->rowCount() > 0) {
                return ['success' => false, 'message' => 'Пользователь с таким именем или email уже существует'];
            }
            
            // Хеширование пароля
            $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
            
            // Добавление пользователя в базу
            $stmt = $this->pdo->prepare("
                INSERT INTO users (username, password, email)
                VALUES (:username, :password, :email)
            ");
            
            $stmt->execute([
                ':username' => $username,
                ':password' => $hashedPassword,
                ':email' => $email
            ]);
            
            return ['success' => true, 'id' => $this->pdo->lastInsertId()];
        } catch (PDOException $e) {
            return ['success' => false, 'message' => 'Ошибка при регистрации: ' . $e->getMessage()];
        }
    }
    
    // Аутентификация пользователя
    public function login($username, $password) {
        $stmt = $this->pdo->prepare("SELECT id, username, password FROM users WHERE username = :username");
        $stmt->execute([':username' => $username]);
        $user = $stmt->fetch();
        
        if ($user && password_verify($password, $user['password'])) {
            // Аутентификация успешна
            return ['success' => true, 'user' => [
                'id' => $user['id'],
                'username' => $user['username']
            ]];
        }
        
        return ['success' => false, 'message' => 'Неверное имя пользователя или пароль'];
    }
}