import { createApp } from 'vue'
import { plugin } from '@formkit/vue'
import App from './App.vue'
import router from './router'
import formkitConfig from './plugins/formkit'
import './style.css'

const app = createApp(App)

app.use(router)
app.use(plugin, formkitConfig)

app.mount('#app')