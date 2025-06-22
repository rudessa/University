<?php require_once 'views/layout/header.php'; ?>

<div class="row">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="m-0">Вход в систему</h3>
            </div>
            <div class="card-body">
                <?php if (isset($error)): ?>
                    <div class="alert alert-danger"><?= $error ?></div>
                <?php endif; ?>
                
                <form action="index.php?action=login" method="post">
                    <div class="form-group">
                        <label for="username">Имя пользователя</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Пароль</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Войти</button>
                </form>
                
                <hr>
                
                <p>Еще нет аккаунта? <a href="index.php?action=showRegisterForm">Зарегистрироваться</a></p>
            </div>
        </div>
    </div>
</div>

<?php require_once 'views/layout/footer.php'; ?>