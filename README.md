# Тестовое задание

## Клонирование репозитория

```bash
git clone https://github.com/Tarasyonok/test-task-auth
```

## Запуск в Docker

```bash
cd test-task-auth
```

```bash
docker-compose up -d --build
```

## Проверка эндпоинтов

Перейдите на [localhost:8000/docs](localhost:8000/docs), здесь вам доступны все эндпоинты.
В базе зарегестрирован админ с email `admin@example.com` и паролем `AdminPass123!`

## Описание эндпоинтов

Вот подробное описание всех эндпоинтов аутентификации:

---

### **1. Регистрация пользователя**

**Эндпоинт:**  
`POST /auth/register`

**Описание:**  
Регистрирует нового пользователя в системе.

**Параметры (тело запроса):**

```json
{
  "email": "user@example.com",
  "password": "StrongPass123",
  "password_repeat": "StrongPass123",
  "first_name": "Иван",
  "last_name": "Петров"
}
```

**Ответ при успехе:**

```json
{"message": "User registered"}
```

**Ошибки:**

- `400 Bad Request` - если email уже занят

---

### **2. Вход в систему**

**Эндпоинт:**  
`POST /auth/login`

**Описание:**  
Аутентифицирует пользователя и возвращает токены доступа.

**Параметры (форма):**

```
username: user@example.com
password: StrongPass123
```

**Ответ при успехе:**

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

- устанавливает HTTP-only куки:
  - `access_token`
  - `refresh_token`

**Ошибки:**

- `401 Unauthorized` - неверные учетные данные

---

### **3. Выход из системы**

**Эндпоинт:**  
`POST /auth/logout`

**Описание:**  
Очищает токены доступа пользователя.

**Ответ:**

```json
{"message": "Logged out"}
```

- удаляет куки `access_token` и `refresh_token`

---

### **4. Обновление токена доступа**

**Эндпоинт:**  
`POST /auth/refresh`

**Описание:**  
Обновляет access token с помощью refresh token.

**Требования:**

- Действительный refresh token в куках

**Ответ при успехе:**

```json
{"access_token": "eyJhbGciOi..."}
```

- устанавливает новую куку `access_token`

**Ошибки:**

- `401 Unauthorized` - невалидный или просроченный refresh token

---

### **5. Получение профиля**

**Эндпоинт:**  
`GET /auth/profile`

**Описание:**  
Возвращает данные текущего пользователя.

**Требования:**

- Действительный access token в куках или заголовке Authorization

**Ответ при успехе:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Петров",
  "is_active": true,
  "role": {
    "id": 2,
    "name": "user"
  }
}
```

**Ошибки:**

- `401 Unauthorized` - если пользователь не аутентифицирован

---

### **6. Обновление профиля**

**Эндпоинт:**  
`PATCH /auth/profile`

**Описание:**  
Обновляет данные пользователя.

**Параметры (тело запроса):**

```json
{
  "first_name": "НовоеИмя",
  "last_name": "НоваяФамилия",
  "password": "NewPass123"
}
```

(все поля опциональны)

**Ответ при успехе:**

```json
{"message": "Profile updated"}
```

**Ошибки:**

- `401 Unauthorized` - если пользователь не аутентифицирован
- `422 Validation Error` - если данные не прошли валидацию

---

### **7. Удаление профиля (мягкое)**

**Эндпоинт:**  
`DELETE /auth/profile`

**Описание:**  
Деактивирует аккаунт пользователя (is_active=False) и выполняет выход.

**Ответ при успехе:**

```json
{"message": "Account deactivated"}
```

- удаляет куки `access_token` и `refresh_token`

**Ошибки:**

- `401 Unauthorized` - если пользователь не аутентифицирован

---

### **8. Получение списка пользователей (админ)**

**Эндпоинт:**  
`GET /auth/admin/users`

**Описание:**  
Возвращает список всех пользователей (только для администраторов).

**Требования:**

- Пользователь должен иметь разрешение "manage_users"

**Ответ при успехе:**

```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "is_active": true,
    "role_id": 1
  },
  {
    "id": 2,
    "email": "user@example.com",
    "is_active": true,
    "role_id": 2
  }
]
```

**Ошибки:**

- `401 Unauthorized` - если пользователь не аутентифицирован
- `403 Forbidden` - если нет прав администратора

---

### **Общие замечания:**

1. Все эндпоинты (кроме `/register` и `/login`) требуют аутентификации
2. Токены передаются либо через HTTP-only куки, либо через заголовок `Authorization: Bearer <token>`
3. Для административных эндпоинтов требуется роль `admin` с соответствующими разрешениями
