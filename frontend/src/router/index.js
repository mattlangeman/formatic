import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import FormView from '../views/FormView.vue'
import SubmissionsView from '../views/SubmissionsView.vue'
import FormTableEditorView from '../views/FormTableEditorView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: {
      title: 'Formatic - Dynamic Form Builder'
    }
  },
  {
    path: '/form/:slug',
    name: 'form',
    component: FormView,
    meta: {
      title: 'Form - Formatic'
    }
  },
  {
    path: '/form/:slug/:pageSlug',
    name: 'form-page',
    component: FormView,
    meta: {
      title: 'Form - Formatic'
    }
  },
  {
    path: '/form/:slug/submissions',
    name: 'submissions',
    component: SubmissionsView,
    meta: {
      title: 'Submissions - Formatic'
    }
  },
  {
    path: '/form/:slug/table-editor',
    name: 'form-table-editor',
    component: FormTableEditorView,
    meta: {
      title: 'Table Editor - Formatic'
    }
  },
  {
    path: '/form/:slug/submission/:submissionId',
    name: 'form-submission',
    component: FormView,
    meta: {
      title: 'Form Submission - Formatic'
    }
  },
  {
    path: '/form/:slug/submission/:submissionId/:pageSlug',
    name: 'form-submission-page',
    component: FormView,
    meta: {
      title: 'Form Submission - Formatic'
    }
  },
  {
    path: '/form/:slug/submission/:submissionId/table',
    name: 'form-submission-table',
    component: FormTableEditorView,
    meta: {
      title: 'Table Editor - Form Submission - Formatic'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards for title updates
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Formatic'
  next()
})

export default router