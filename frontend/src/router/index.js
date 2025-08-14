import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import FormView from '../views/FormView.vue'
import FormDetailView from '../views/FormDetailView.vue'
import SubmissionsView from '../views/SubmissionsView.vue'
import FormTableEditorView from '../views/FormTableEditorView.vue'
import FormBuilderView from '../views/FormBuilderView.vue'
import NewFormView from '../views/NewFormView.vue'

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
    name: 'form-detail',
    component: FormDetailView,
    meta: {
      title: 'Form Details - Formatic'
    }
  },
  {
    path: '/form/:slug/fill',
    name: 'form',
    component: FormView,
    meta: {
      title: 'Form - Formatic'
    }
  },
  {
    path: '/form/:slug/fill/:pageSlug',
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
    redirect: to => ({
      name: 'form-submission-table',
      params: to.params
    })
  },
  {
    path: '/form/:slug/submission/:submissionId/form',
    name: 'form-submission',
    component: FormView,
    meta: {
      title: 'Form Submission - Formatic'
    }
  },
  {
    path: '/form/:slug/submission/:submissionId/form/:pageSlug',
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
    path: '/builder/new',
    name: 'new-form',
    component: NewFormView,
    meta: {
      title: 'Create New Form - Formatic'
    }
  },
  {
    path: '/builder/:slug',
    name: 'form-builder',
    component: FormBuilderView,
    meta: {
      title: 'Form Builder - Formatic'
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