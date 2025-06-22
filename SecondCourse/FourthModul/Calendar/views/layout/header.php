<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Мой Календарь</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header class="bg-primary text-white p-3">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h1>Мой Календарь</h1>
                </div>
                <div class="col-md-6 text-right">
                    <?php if (isset($_SESSION['logged_in']) && $_SESSION['logged_in']): ?>
                        <span>Привет, <?= htmlspecialchars($_SESSION['username']) ?>!</span>
                        <a href="index.php?action=logout" class="btn btn-outline-light btn-sm ml-2">Выйти</a>
                    <?php else: ?>
                        <a href="index.php?action=showLoginForm" class="btn btn-outline-light btn-sm">Войти</a>
                        <a href="index.php?action=showRegisterForm" class="btn btn-outline-light btn-sm ml-2">Регистрация</a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </header>
    
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="index.php">Главная</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.php?action=list&type=current">Текущие задачи</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.php?action=list&type=overdue">Просроченные задачи</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.php?action=list&type=completed">Выполненные задачи</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.php?action=list&type=date&date=<?= date('Y-m-d') ?>">Задачи на сегодня</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <?php if (isset($error)): ?>
            <div class="alert alert-danger"><?= $error ?></div>
        <?php endif; ?>
        
        <?php if (isset($success)): ?>
            <div class="alert alert-success"><?= $success ?></div>
        <?php endif; ?>