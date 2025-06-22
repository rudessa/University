<?php require_once 'views/layout/header.php'; ?>

<div class="row">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="m-0">Регистрация</h3>
            </div>
            <div class="card-body">
                <form action="index.php?action=register" method="post">
                    <div class="form-group">
                        <label for="username">Имя пользователя</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email (необязательно)</label>
                        <input type="email" class="form-control" id="email" name="email">
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Пароль</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Зарегистрироваться</button>
                </form>
                
                <hr>
                
                <p>Уже есть аккаунт? <a href="index.php?action=showLoginForm">Войти</a></p>
            </div>
        </div>
    </div>
</div>

<?php require_once 'views/layout/footer.php'; ?>