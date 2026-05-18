<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { contentApi, type InstallStatus } from '@/api/content'

const step = ref(0)
const status = ref<InstallStatus | null>(null)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const result = ref<{ siteStartTime: string; restartRequired: boolean; loginUrl: string } | null>(null)
const form = reactive({
  siteTitle: 'SRBlogs',
  author: '站点作者',
  adminUsername: 'admin',
  adminPassword: '',
  publicBaseUrl: typeof window !== 'undefined' ? window.location.origin : 'https://example.com',
  corsOrigins: typeof window !== 'undefined' ? window.location.origin : 'https://example.com',
  siteStartTime: ''
})

const steps = ['环境检查', '站点信息', '管理员账号', '安全配置', '完成安装']
const canSubmit = computed(() => form.siteTitle.trim() && form.author.trim() && form.adminUsername.trim() && form.adminPassword.trim() && form.publicBaseUrl.trim() && form.corsOrigins.trim())
const adminLoginUrl = computed(() => {
  if (typeof window === 'undefined') return '/admin/login'
  if (['5173', '5175'].includes(window.location.port)) {
    return `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:5174/admin/login`
  }
  return '/admin/login'
})

function passwordHint() {
  if (!form.adminPassword) return '至少 12 位，包含字母和数字。'
  if (form.adminPassword.length < 12) return '密码长度不足 12 位。'
  if (!/[a-zA-Z]/.test(form.adminPassword) || !/\d/.test(form.adminPassword)) return '密码必须同时包含字母和数字。'
  return '密码格式满足基础要求。'
}

async function loadStatus() {
  loading.value = true
  error.value = ''
  try {
    status.value = await contentApi.installStatus()
    if (status.value.installed && typeof window !== 'undefined') window.location.href = adminLoginUrl.value
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '无法读取安装状态'
  } finally {
    loading.value = false
  }
}

async function submitInstall() {
  if (!canSubmit.value) {
    error.value = '请完整填写安装信息。'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    result.value = await contentApi.install({
      siteTitle: form.siteTitle.trim(),
      author: form.author.trim(),
      adminUsername: form.adminUsername.trim(),
      adminPassword: form.adminPassword,
      publicBaseUrl: form.publicBaseUrl.trim(),
      corsOrigins: form.corsOrigins.trim(),
      siteStartTime: form.siteStartTime.trim() || undefined
    })
    step.value = 4
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : '安装失败'
  } finally {
    submitting.value = false
  }
}

onMounted(loadStatus)
</script>

<template>
  <main class="install-page">
    <section class="install-shell">
      <div class="install-aside">
        <p class="install-kicker">SRBlogs Setup</p>
        <h1>首次启动安装向导</h1>
        <p>完成站点信息、管理员账号和生产安全配置后，系统会创建安装锁并启用后台登录。</p>
        <ol class="install-steps" aria-label="安装步骤">
          <li v-for="(item, index) in steps" :key="item" :class="{ active: index === step, done: index < step }">
            <span>{{ index + 1 }}</span>{{ item }}
          </li>
        </ol>
      </div>

      <form class="install-card" @submit.prevent="submitInstall">
        <div v-if="loading" class="install-state">正在检查安装状态...</div>
        <template v-else>
          <div v-if="step === 0" class="install-panel">
            <h2>环境检查</h2>
            <p>后端当前处于未安装状态，只开放安装接口和健康检查接口。</p>
            <div class="install-check-list">
              <div><b>安装状态</b><span>{{ status?.needsInstall ? '需要初始化' : '已安装' }}</span></div>
              <div><b>缺失项</b><span>{{ status?.missingItems?.join(' / ') || '无' }}</span></div>
              <div><b>配置文件</b><span>/etc/srblogs/backend.env</span></div>
            </div>
          </div>

          <div v-else-if="step === 1" class="install-panel">
            <h2>站点信息</h2>
            <label>站点标题<input v-model="form.siteTitle" autocomplete="organization" /></label>
            <label>作者名称<input v-model="form.author" autocomplete="name" /></label>
          </div>

          <div v-else-if="step === 2" class="install-panel">
            <h2>管理员账号</h2>
            <label>管理员用户名<input v-model="form.adminUsername" autocomplete="username" /></label>
            <label>管理员密码<input v-model="form.adminPassword" type="password" autocomplete="new-password" /></label>
            <p class="install-help">{{ passwordHint() }}</p>
          </div>

          <div v-else-if="step === 3" class="install-panel">
            <h2>安全配置</h2>
            <label>PUBLIC_BASE_URL<input v-model="form.publicBaseUrl" placeholder="https://example.com" /></label>
            <label>CORS_ORIGINS<textarea v-model="form.corsOrigins" rows="3" placeholder="https://example.com"></textarea></label>
            <label>SITE_START_TIME（可选）<input v-model="form.siteStartTime" placeholder="2026-05-18T09:46:56+08:00" /></label>
            <p class="install-help">JWT_SECRET 会由后端自动生成，不会从前端接收或回显。</p>
          </div>

          <div v-else class="install-panel install-complete">
            <h2>安装完成</h2>
            <p>安装锁已创建，后台账号已切换为本次安装填写的管理员账号。</p>
            <div class="install-check-list">
              <div><b>站点起始时间</b><span>{{ result?.siteStartTime }}</span></div>
              <div><b>建议操作</b><span>生产环境执行 sudo systemctl restart srblogs-backend</span></div>
            </div>
            <a class="install-primary" :href="adminLoginUrl">进入后台登录</a>
          </div>

          <p v-if="error" class="install-error">{{ error }}</p>

          <div v-if="step < 4" class="install-actions">
            <button type="button" :disabled="step === 0" @click="step--">上一步</button>
            <button v-if="step < 3" type="button" @click="step++">下一步</button>
            <button v-else type="submit" :disabled="submitting || !canSubmit">{{ submitting ? '安装中...' : '完成安装' }}</button>
          </div>
        </template>
      </form>
    </section>
  </main>
</template>

<style scoped>
.install-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 16px;
  background: #f5f5f5;
  color: #151515;
}
.install-shell {
  width: min(1080px, 100%);
  display: grid;
  grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
  gap: 18px;
}
.install-aside,
.install-card {
  border: 1px solid rgba(17, 17, 17, .12);
  background: rgba(255, 255, 255, .92);
  border-radius: 8px;
  box-shadow: 0 18px 48px rgba(17, 17, 17, .08);
}
.install-aside { padding: 30px; }
.install-card { padding: 28px; min-height: 520px; }
.install-kicker {
  margin: 0 0 14px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .16em;
  color: #dc2626;
  text-transform: uppercase;
}
h1, h2 { margin: 0; letter-spacing: 0; }
h1 { font-size: clamp(32px, 5vw, 56px); line-height: 1.02; }
h2 { font-size: 26px; }
.install-aside p,
.install-panel p {
  color: rgba(17, 17, 17, .64);
  line-height: 1.8;
}
.install-steps {
  display: grid;
  gap: 10px;
  padding: 0;
  margin: 34px 0 0;
  list-style: none;
}
.install-steps li {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(17, 17, 17, .55);
  font-weight: 700;
}
.install-steps span {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #f1f1f1;
  color: #777;
}
.install-steps li.active,
.install-steps li.done { color: #151515; }
.install-steps li.active span,
.install-steps li.done span { background: #dc2626; color: white; }
.install-panel { display: grid; gap: 18px; }
.install-panel label {
  display: grid;
  gap: 8px;
  font-size: 13px;
  font-weight: 800;
  color: rgba(17, 17, 17, .72);
}
.install-panel input,
.install-panel textarea {
  width: 100%;
  border: 1px solid rgba(17, 17, 17, .14);
  border-radius: 8px;
  padding: 12px 13px;
  color: #151515;
  background: white;
  outline: none;
  font: inherit;
}
.install-panel input:focus,
.install-panel textarea:focus { border-color: #dc2626; box-shadow: 0 0 0 3px rgba(220, 38, 38, .12); }
.install-check-list {
  display: grid;
  gap: 10px;
}
.install-check-list div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px;
  border-radius: 8px;
  background: #f7f7f7;
  color: rgba(17, 17, 17, .68);
}
.install-check-list b { color: #151515; }
.install-help { margin: 0; font-size: 13px; }
.install-error {
  margin: 18px 0 0;
  padding: 12px 14px;
  border-radius: 8px;
  background: rgba(220, 38, 38, .1);
  color: #b91c1c;
  font-weight: 700;
}
.install-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}
.install-actions button,
.install-primary {
  border: 0;
  border-radius: 8px;
  padding: 12px 18px;
  font-weight: 900;
  cursor: pointer;
  text-decoration: none;
}
.install-actions button:first-child { background: #eeeeee; color: #333; }
.install-actions button:last-child,
.install-primary { background: #dc2626; color: white; }
.install-actions button:disabled { cursor: not-allowed; opacity: .5; }
.install-state {
  min-height: 420px;
  display: grid;
  place-items: center;
  color: rgba(17, 17, 17, .6);
  font-weight: 800;
}
.install-complete .install-primary {
  justify-self: start;
  margin-top: 8px;
}
@media (max-width: 820px) {
  .install-shell { grid-template-columns: 1fr; }
  .install-card { min-height: auto; }
}
</style>
