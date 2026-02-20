<template>
  <div class="auth-page auth-neuro">
    <div class="container" :class="{ 'right-panel-active': isRegister }">
      <section class="form-container">
        <transition name="auth-form-switch" mode="out-in">
          <form
            v-if="isRegister"
            key="register"
            class="auth-form"
            :class="{ loading: isLoading }"
            @submit.prevent="handleRegister"
          >
            <h1>Регистрация</h1>
            <input v-model="registerForm.companyName" type="text" placeholder="Название компании" required />
            <input v-model="registerForm.email" type="email" placeholder="Email" required />
            <div class="password-field">
              <input
                v-model="registerForm.password"
                :type="showRegisterPassword ? 'text' : 'password'"
                minlength="8"
                placeholder="Пароль"
                required
              />
              <button
                type="button"
                class="eye-toggle"
                :aria-label="showRegisterPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showRegisterPassword = !showRegisterPassword"
              >
                <svg v-if="!showRegisterPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M12 4.5C7 4.5 2.7 7.6 1 12c1.7 4.4 6 7.5 11 7.5s9.3-3.1 11-7.5c-1.7-4.4-6-7.5-11-7.5zm0 12.5a5 5 0 110-10 5 5 0 010 10z"
                    fill="currentColor"
                  />
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M3 5l17 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                  <path d="M12 6a6 6 0 016 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </button>
            </div>
            <button type="submit" :disabled="isLoading">
              {{ isLoading ? "Загрузка..." : "Создать аккаунт" }}
            </button>
            <p v-if="error" class="error">{{ error }}</p>
            <a href="https://t.me/M1ke994" target="_blank" rel="noopener noreferrer" class="forgot-link">Забыли пароль?</a>
          </form>

          <form
            v-else
            key="login"
            class="auth-form"
            :class="{ loading: isLoading }"
            @submit.prevent="handleLogin"
          >
            <h1>Вход</h1>
            <input v-model="loginForm.email" type="email" placeholder="Email" required />
            <div class="password-field">
              <input
                v-model="loginForm.password"
                :type="showLoginPassword ? 'text' : 'password'"
                minlength="8"
                placeholder="Пароль"
                required
              />
              <button
                type="button"
                class="eye-toggle"
                :aria-label="showLoginPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showLoginPassword = !showLoginPassword"
              >
                <svg v-if="!showLoginPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M12 4.5C7 4.5 2.7 7.6 1 12c1.7 4.4 6 7.5 11 7.5s9.3-3.1 11-7.5c-1.7-4.4-6-7.5-11-7.5zm0 12.5a5 5 0 110-10 5 5 0 010 10z"
                    fill="currentColor"
                  />
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M3 5l17 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                  <path d="M12 6a6 6 0 016 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </button>
            </div>
            <button type="submit" :disabled="isLoading">
              {{ isLoading ? "Загрузка..." : "Войти" }}
            </button>
            <p v-if="error" class="error">{{ error }}</p>
            <a href="https://t.me/M1ke994" target="_blank" rel="noopener noreferrer" class="forgot-link">Забыли пароль?</a>
          </form>
        </transition>
      </section>

      <section class="overlay-container">
        <div class="overlay">
          <h2>{{ isRegister ? "Уже есть аккаунт?" : "Новый пользователь?" }}</h2>
          <p>
            {{
              isRegister
                ? "Войдите, чтобы продолжить работу с аналитикой."
                : "Создайте аккаунт и начните отслеживать метрики."
            }}
          </p>
          <button type="button" class="ghost" :disabled="isLoading" @click="toggleMode">
            {{ isRegister ? "Войти" : "Регистрация" }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const isRegister = ref(false);
const isLoading = ref(false);
const error = ref("");
const showLoginPassword = ref(false);
const showRegisterPassword = ref(false);

const loginForm = reactive({
  email: "",
  password: "",
});

const registerForm = reactive({
  companyName: "",
  email: "",
  password: "",
});

function toggleMode() {
  isRegister.value = !isRegister.value;
  error.value = "";
  showLoginPassword.value = false;
  showRegisterPassword.value = false;
}

function validateLoginForm() {
  const email = String(loginForm.email || "").trim();
  const password = String(loginForm.password || "");
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!email) {
    return "Введите email.";
  }
  if (!emailRegex.test(email)) {
    return "Введите корректный email.";
  }
  if (!password) {
    return "Введите пароль.";
  }
  if (password.length < 8) {
    return "Пароль должен содержать минимум 8 символов.";
  }
  return "";
}

async function handleLogin() {
  const validationError = validateLoginForm();
  if (validationError) {
    error.value = validationError;
    return;
  }

  isLoading.value = true;
  error.value = "";
  try {
    await auth.login(String(loginForm.email).trim(), loginForm.password);
    router.push("/dashboard");
  } catch (_) {
    error.value = auth.error || "Ошибка входа.";
  } finally {
    isLoading.value = false;
  }
}

async function handleRegister() {
  isLoading.value = true;
  error.value = "";
  try {
    await auth.register(registerForm.email, registerForm.password, registerForm.companyName);
    router.push("/dashboard");
  } catch (_) {
    error.value = auth.error || "Ошибка регистрации.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.auth-neuro {
  min-height: 100vh;
  padding: 2rem 1rem;
  background: #e0e5ec;
  display: flex;
  align-items: center;
  justify-content: center;
}

.container {
  width: 100%;
  max-width: 60rem;
  min-height: 70vh;
  background: #e0e5ec;
  border-radius: 2rem;
  box-shadow: 0.75rem 0.75rem 1.6rem rgba(163, 177, 198, 0.65), -0.75rem -0.75rem 1.6rem rgba(255, 255, 255, 0.9);
  display: flex;
}

.form-container {
  flex: 1 1 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
}

.auth-form {
  width: 100%;
  max-width: 26rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding: 1.5rem;
}

.auth-form h1 {
  margin: 0 0 0.4rem;
  color: #25324a;
}

.auth-form input {
  border: 0;
  border-radius: 1rem;
  padding: 0.9rem 1rem;
  background: #e0e5ec;
  color: #25324a;
  box-shadow: inset 0.35rem 0.35rem 0.7rem rgba(163, 177, 198, 0.45), inset -0.35rem -0.35rem 0.7rem rgba(255, 255, 255, 0.9);
}

.auth-form input:focus {
  outline: 0.12rem solid rgba(43, 168, 216, 0.35);
}

.password-field {
  position: relative;
}

.password-field input {
  width: 100%;
  padding-right: 2.8rem;
}

.auth-form .eye-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #7a8699;
  padding: 0;
  min-height: 20px;
  min-width: 20px;
  box-shadow: none;
}

.auth-form .eye-toggle:hover {
  filter: none;
  color: #4a5568;
}

.auth-form button {
  border: none;
  border-radius: 30px;
  min-height: 2.8rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #2ba8d8, #4cc9f0);
  box-shadow: 0 0.5rem 1rem rgba(76, 201, 240, 0.35);
  transition: filter 0.2s ease, opacity 0.2s ease;
}

.auth-form button:hover:not(:disabled) {
  filter: brightness(1.05);
}

.auth-form button:focus-visible {
  outline: none;
}

.auth-form button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.auth-form .error {
  margin: 0;
  font-size: 0.9rem;
}

.forgot-link {
  display: block;
  margin-top: 12px;
  font-size: 14px;
  color: #2c8fd6;
  text-align: right;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.auth-form.loading {
  pointer-events: none;
}

.overlay-container {
  flex: 1 1 50%;
  display: flex;
}

.overlay {
  width: 100%;
  background: linear-gradient(135deg, #2ba8d8, #4cc9f0);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  border-radius: 2rem;
  transition: transform 0.6s ease-in-out;
}

.overlay h2 {
  margin: 0;
}

.overlay p {
  margin: 0.9rem 0 1.4rem;
  max-width: 20rem;
}

.ghost {
  min-width: 10rem;
  border-radius: 30px;
  border: 0.12rem solid rgba(255, 255, 255, 0.9);
  background: transparent;
  color: #ffffff;
  min-height: 2.8rem;
}

.ghost:hover {
  background: rgba(255, 255, 255, 0.14);
}

.ghost:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.auth-form-switch-enter-active,
.auth-form-switch-leave-active {
  transition: transform 0.6s ease-in-out, opacity 0.6s ease-in-out;
}

.auth-form-switch-enter-from {
  opacity: 0;
  transform: translateX(2rem);
}

.auth-form-switch-leave-to {
  opacity: 0;
  transform: translateX(-2rem);
}

.container.right-panel-active .overlay {
  transform: translateX(-5%);
}

@media (max-width: 768px) {
  .auth-neuro {
    padding: 1rem;
  }

  .container {
    flex-direction: column;
    min-height: auto;
    gap: 0.5rem;
  }

  .overlay-container {
    order: 1;
    width: 100%;
  }

  .overlay {
    border-radius: 2rem;
    padding: 1.5rem 1.25rem;
    min-height: 12rem;
    transform: translateY(0);
  }

  .form-container {
    order: 2;
    width: 100%;
    padding: 1rem 1.25rem 1.5rem;
  }

  .auth-form {
    max-width: none;
    padding: 0.5rem 0;
  }

  .auth-form-switch-enter-from {
    transform: translateY(1.25rem);
  }

  .auth-form-switch-leave-to {
    transform: translateY(-1.25rem);
  }

  .container.right-panel-active .overlay {
    transform: translateY(-4%);
  }
}
</style>
