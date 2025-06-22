<?php
class Task {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    // Создание новой задачи
    public function create($data) {
        try {
            $stmt = $this->pdo->prepare("
                INSERT INTO tasks (title, type, location, start_datetime, duration, comment, user_id)
                VALUES (:title, :type, :location, :start_datetime, :duration, :comment, :user_id)
            ");
            
            $stmt->execute([
                ':title' => $data['title'],
                ':type' => $data['type'],
                ':location' => $data['location'],
                ':start_datetime' => $data['start_datetime'],
                ':duration' => $data['duration'],
                ':comment' => $data['comment'],
                ':user_id' => $data['user_id'] // Теперь обязательный параметр
            ]);
            
            return $this->pdo->lastInsertId();
        } catch (PDOException $e) {
            return false;
        }
    }
    
    // Получение задачи по ID с проверкой владельца
    public function getById($id, $userId) {
        $stmt = $this->pdo->prepare("
            SELECT * FROM tasks 
            WHERE id = :id AND user_id = :user_id
        ");
        $stmt->execute([
            ':id' => $id,
            ':user_id' => $userId
        ]);
        return $stmt->fetch();
    }
    
    // Обновление задачи с проверкой владельца
    public function update($id, $data) {
        try {
            $stmt = $this->pdo->prepare("
                UPDATE tasks
                SET title = :title,
                    type = :type,
                    location = :location,
                    start_datetime = :start_datetime,
                    duration = :duration,
                    comment = :comment,
                    status = :status
                WHERE id = :id AND user_id = :user_id
            ");
            
            $data[':id'] = $id;
            $stmt->execute($data);
            
            return $stmt->rowCount() > 0;
        } catch (PDOException $e) {
            return false;
        }
    }
    
    // Удаление задачи с проверкой владельца
    public function delete($id, $userId) {
        $stmt = $this->pdo->prepare("
            DELETE FROM tasks 
            WHERE id = :id AND user_id = :user_id
        ");
        return $stmt->execute([
            ':id' => $id,
            ':user_id' => $userId
        ]);
    }
    
    // Получение списка текущих задач для конкретного пользователя
    public function getCurrentTasks($userId) {
        $sql = "
            SELECT * FROM tasks
            WHERE status = 'pending'
            AND start_datetime >= CURDATE()
            AND user_id = :user_id
            ORDER BY start_datetime ASC
        ";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':user_id', $userId, PDO::PARAM_INT);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    // Получение списка просроченных задач для конкретного пользователя
    public function getOverdueTasks($userId) {
        $sql = "
            SELECT * FROM tasks
            WHERE ((status = 'pending' AND start_datetime < CURDATE())
            OR status = 'overdue')
            AND user_id = :user_id
            ORDER BY start_datetime ASC
        ";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':user_id', $userId, PDO::PARAM_INT);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    // Получение списка выполненных задач для конкретного пользователя
    public function getCompletedTasks($userId) {
        $sql = "
            SELECT * FROM tasks
            WHERE status = 'completed'
            AND user_id = :user_id
            ORDER BY start_datetime DESC
        ";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':user_id', $userId, PDO::PARAM_INT);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    // Получение списка задач на конкретную дату для конкретного пользователя
    public function getTasksByDate($date, $userId) {
        $sql = "
            SELECT * FROM tasks
            WHERE DATE(start_datetime) = :date
            AND user_id = :user_id
            ORDER BY start_datetime ASC
        ";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':date', $date);
        $stmt->bindParam(':user_id', $userId, PDO::PARAM_INT);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    // Обновление статусов задач (для автоматического определения просроченных)
    // Обновляет все задачи, так как это общая служебная функция
    public function updateStatuses() {
        $stmt = $this->pdo->prepare("
            UPDATE tasks
            SET status = 'overdue'
            WHERE status = 'pending'
            AND start_datetime < NOW()
        ");
        
        return $stmt->execute();
    }
}