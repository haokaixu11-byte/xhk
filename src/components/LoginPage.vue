<template>
  <div class="login-wrapper">
    <!-- Background decoration -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="login-card">
      <!-- Logo / Title -->
      <div class="login-header">
        <div class="logo">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="20" fill="url(#grad)" />
            <path d="M13 20.5L18 25.5L27 15" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="grad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                <stop stop-color="#667eea"/>
                <stop offset="1" stop-color="#764ba2"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h1>欢迎回来</h1>
        <p>请登录您的账号</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Username -->
        <div class="form-group" :class="{ 'has-error': errors.username, 'is-focused': focused.username }">
          <label for="username">用户名</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </span>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              autocomplete="username"
              @focus="focused.username = true"
              @blur="focused.username = false; validateUsername()"
            />
          </div>
          <span class="error-msg" v-if="errors.username">{{ errors.username }}</span>
        </div>

        <!-- Password -->
        <div class="form-group" :class="{ 'has-error': errors.password, 'is-focused': focused.password }">
          <label for="password">密码</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </span>
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="current-password"
              @focus="focused.password = true"
              @blur="focused.password = false; validatePassword()"
            />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <span class="error-msg" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <!-- Options Row -->
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="form.remember" />
            <span class="checkmark"></span>
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-link" @click.prevent="handleForgot">忘记密码？</a>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="login-btn" :class="{ loading: isLoading }" :disabled="isLoading">
          <span v-if="!isLoading">登 录</span>
          <span v-else class="loading-content">
            <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            登录中...
          </span>
        </button>

        <!-- Success/Error Message -->
        <transition name="slide-fade">
          <div v-if="message.text" :class="['message-box', message.type]">
            <svg v-if="message.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ message.text }}
          </div>
        </transition>
      </form>

      <!-- Divider -->
      <div class="divider">
        <span>或者使用</span>
      </div>

      <!-- Third-party login -->
      <div class="third-party">
        <button class="third-btn github" @click="thirdPartyLogin('GitHub')">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
          </svg>
          GitHub
        </button>
        <button class="third-btn wechat" @click="thirdPartyLogin('微信')">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M8.69 11.52c-.46 0-.83-.38-.83-.84s.37-.84.83-.84.83.38.83.84-.37.84-.83.84zm4.62 0c-.46 0-.83-.38-.83-.84s.37-.84.83-.84.83.38.83.84-.37.84-.83.84zM12 2C6.48 2 2 6.03 2 11c0 2.64 1.19 5.01 3.09 6.71L4 22l4.5-2.25C9.59 20.23 10.77 20.5 12 20.5c5.52 0 10-4.03 10-9s-4.48-9-10-9z"/>
          </svg>
          微信
        </button>
        <button class="third-btn google" @click="thirdPartyLogin('Google')">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Google
        </button>
      </div>

      <!-- Register link -->
      <p class="register-link">
        还没有账号？<a href="#" @click.prevent="handleRegister">立即注册</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const errors = reactive({
  username: '',
  password: ''
})

const focused = reactive({
  username: false,
  password: false
})

const showPassword = ref(false)
const isLoading = ref(false)
const message = reactive({ text: '', type: '' })

// Validation
const validateUsername = () => {
  if (!form.username) {
    errors.username = '请输入用户名'
  } else if (form.username.length < 3) {
    errors.username = '用户名至少需要3个字符'
  } else {
    errors.username = ''
  }
}

const validatePassword = () => {
  if (!form.password) {
    errors.password = '请输入密码'
  } else if (form.password.length < 6) {
    errors.password = '密码至少需要6个字符'
  } else {
    errors.password = ''
  }
}

const showMessage = (text, type = 'error') => {
  message.text = text
  message.type = type
  setTimeout(() => {
    message.text = ''
    message.type = ''
  }, 3000)
}

const handleLogin = async () => {
  validateUsername()
  validatePassword()
  if (errors.username || errors.password) return

  isLoading.value = true
  message.text = ''

  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1500))

  // Demo: admin/123456 is valid
  if (form.username === 'admin' && form.password === '123456') {
    showMessage('登录成功！欢迎回来 👋', 'success')
  } else {
    showMessage('用户名或密码错误，请重试')
  }

  isLoading.value = false
}

const handleForgot = () => {
  showMessage('重置密码邮件已发送到您的邮箱', 'success')
}

const handleRegister = () => {
  showMessage('注册功能即将上线，敬请期待！', 'success')
}

const thirdPartyLogin = (platform) => {
  showMessage(`${platform} 第三方登录功能即将上线`, 'success')
}
</script>

<style scoped>
/* ===== Layout ===== */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
}

/* ===== Background Shapes ===== */
.bg-shapes .shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  animation: float 8s ease-in-out infinite;
}
.shape-1 { width: 300px; height: 300px; top: -80px; left: -80px; animation-delay: 0s; }
.shape-2 { width: 200px; height: 200px; bottom: -50px; right: -50px; animation-delay: 2s; }
.shape-3 { width: 150px; height: 150px; top: 50%; right: 15%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

/* ===== Card ===== */
.login-card {
  background: white;
  border-radius: 24px;
  padding: 44px 40px 36px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.18);
  position: relative;
  z-index: 1;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== Header ===== */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
}
.logo svg { width: 100%; height: 100%; }
.login-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}
.login-header p {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

/* ===== Form ===== */
.login-form { display: flex; flex-direction: column; gap: 20px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  color: #1f2937;
  background: #f9fafb;
  transition: all 0.25s ease;
  outline: none;
  box-sizing: border-box;
}

.form-group.is-focused .input-wrapper input,
.input-wrapper input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.12);
}

.form-group.has-error .input-wrapper input {
  border-color: #ef4444;
  background: #fff5f5;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1);
}

.input-icon {
  position: absolute;
  left: 13px;
  width: 20px;
  height: 20px;
  color: #9ca3af;
  pointer-events: none;
  display: flex;
  align-items: center;
}
.input-icon svg { width: 100%; height: 100%; }

.toggle-password {
  position: absolute;
  right: 13px;
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  padding: 0;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}
.toggle-password:hover { color: #667eea; }
.toggle-password svg { width: 100%; height: 100%; }

.error-msg {
  font-size: 12px;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ===== Options Row ===== */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: -4px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #6b7280;
  user-select: none;
}
.remember-me input[type="checkbox"] { display: none; }
.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.remember-me input:checked + .checkmark {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
}
.remember-me input:checked + .checkmark::after {
  content: '';
  width: 5px;
  height: 9px;
  border: 2px solid white;
  border-top: none;
  border-left: none;
  transform: rotate(45deg) translateY(-1px);
}

.forgot-link {
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
.forgot-link:hover { color: #764ba2; text-decoration: underline; }

/* ===== Login Button ===== */
.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 2px;
  margin-top: 4px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}
.login-btn:active:not(:disabled) { transform: translateY(0); }
.login-btn:disabled { opacity: 0.75; cursor: not-allowed; }

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* ===== Message Box ===== */
.message-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
}
.message-box svg { width: 18px; height: 18px; flex-shrink: 0; }
.message-box.success { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.message-box.error { background: #fff5f5; color: #ef4444; border: 1px solid #fecaca; }

/* ===== Slide-fade transition ===== */
.slide-fade-enter-active { transition: all 0.35s ease; }
.slide-fade-leave-active { transition: all 0.25s ease; }
.slide-fade-enter-from { transform: translateY(-10px); opacity: 0; }
.slide-fade-leave-to { transform: translateY(-6px); opacity: 0; }

/* ===== Divider ===== */
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0 20px;
  color: #d1d5db;
  font-size: 13px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}
.divider span { color: #9ca3af; white-space: nowrap; }

/* ===== Third-party ===== */
.third-party {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.third-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 8px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
  color: #4b5563;
}
.third-btn svg { width: 18px; height: 18px; flex-shrink: 0; }
.third-btn:hover { border-color: #667eea; color: #667eea; background: #f5f3ff; transform: translateY(-1px); }

/* ===== Register Link ===== */
.register-link {
  text-align: center;
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}
.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}
.register-link a:hover { color: #764ba2; text-decoration: underline; }

/* ===== Responsive ===== */
@media (max-width: 480px) {
  .login-card { padding: 36px 24px 28px; }
  .third-party { flex-direction: column; }
}
</style>
