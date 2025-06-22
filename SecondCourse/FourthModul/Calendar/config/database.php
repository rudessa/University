<?php
// Конфигурация подключения к базе данных
define('DB_SERVER', '127.0.0.1');
define('DB_PORT', '3306');
define('DB_USERNAME', 'svetochek46');
define('DB_PASSWORD', '4sUtwZxF');
define('DB_NAME', 'svetochek46');

// Устанавливаем соединение с базой данных
try {
    $pdo = new PDO(
        "mysql:host=" . DB_SERVER . ";port=" . DB_PORT . ";dbname=" . DB_NAME,
        DB_USERNAME,
        DB_PASSWORD,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
        ]
    );
} catch(PDOException $e) {
    die("ОШИБКА: Не удалось подключиться к базе данных: " . $e->getMessage());
}
?>