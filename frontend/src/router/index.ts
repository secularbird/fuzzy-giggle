import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

// User views
import UserHome from '../views/user/Home.vue';
import UserSearch from '../views/user/Search.vue';
import UserDocument from '../views/user/Document.vue';
import UserScrape from '../views/user/Scrape.vue';

// Admin views
import AdminHome from '../views/admin/Home.vue';
import AdminDocuments from '../views/admin/Documents.vue';
import AdminEntities from '../views/admin/Entities.vue';
import AdminSettings from '../views/admin/Settings.vue';

const routes: RouteRecordRaw[] = [
  // User routes
  {
    path: '/',
    name: 'user-home',
    component: UserHome,
    meta: { layout: 'user', title: '首页' }
  },
  {
    path: '/search',
    name: 'user-search',
    component: UserSearch,
    meta: { layout: 'user', title: '搜索' }
  },
  {
    path: '/document/:id',
    name: 'user-document',
    component: UserDocument,
    meta: { layout: 'user', title: '文档详情' }
  },
  {
    path: '/scrape',
    name: 'user-scrape',
    component: UserScrape,
    meta: { layout: 'user', title: '网页抓取' }
  },
  
  // Admin routes
  {
    path: '/admin',
    name: 'admin-home',
    component: AdminHome,
    meta: { layout: 'admin', title: '管理首页' }
  },
  {
    path: '/admin/documents',
    name: 'admin-documents',
    component: AdminDocuments,
    meta: { layout: 'admin', title: '文档管理' }
  },
  {
    path: '/admin/entities',
    name: 'admin-entities',
    component: AdminEntities,
    meta: { layout: 'admin', title: '实体管理' }
  },
  {
    path: '/admin/settings',
    name: 'admin-settings',
    component: AdminSettings,
    meta: { layout: 'admin', title: '系统设置' }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Update document title
router.beforeEach((to, _from, next) => {
  const title = to.meta?.title;
  if (title) {
    document.title = `${title} - Knowledge Server`;
  } else {
    document.title = 'Knowledge Server';
  }
  next();
});

export default router;
